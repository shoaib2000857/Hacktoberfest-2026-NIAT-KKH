import hashlib
import io
import json
import os
from pathlib import Path
from uuid import uuid4
from datetime import date
from typing import Literal
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field
from promisegraph import Claim, Finding, investigate, graph, candidates, verify
from . import store
from .gemma import GemmaClient
from .ollama import OllamaClient, installed_models

app = FastAPI(title='PromiseTrap', version='0.1.0')
P = '/api/v1'
LIMIT = 12 * 1024 * 1024

def require(cid):
    case = store.get(cid)
    if not case:
        raise HTTPException(404, 'Investigation not found')
    return case

def editable(cid):
    case = require(cid)
    if case['status'] == 'processing':
        raise HTTPException(409, 'Wait for analysis to finish before changing sources')
    return case

def find_source(sid):
    for case in store.all_cases():
        for source in case['sources']:
            if source['id'] == sid:
                return case, source
    raise HTTPException(404, 'Source not found')

class Create(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    description: str = Field(default='', max_length=2000)

class TextSource(BaseModel):
    filename: str = Field(min_length=1, max_length=200)
    text: str = Field(min_length=1, max_length=60000)
    published_at: date | None = None
    version_group: str | None = Field(default=None, max_length=100)

class Review(BaseModel):
    review_status: Literal['accepted', 'rejected', 'unresolved', 'unreviewed']
    review_notes: str = Field(default='', max_length=4000)

class AnalyzeOptions(BaseModel):
    provider: Literal['gemma','ollama'] = 'gemma'
    model: str | None = Field(default=None,max_length=160)

@app.get(P+'/health')
def health():
    models=installed_models()
    return {'status': 'ok', 'gemma_configured': bool(os.getenv('GEMINI_API_KEY')), 'model': os.getenv('GEMMA_MODEL','gemma-4-26b-a4b-it'), 'ollama_available':bool(models), 'ollama_models':models, 'ollama_default_model':os.getenv('OLLAMA_MODEL','gemma3:4b')}

@app.post(P+'/model/smoke-test')
def smoke(body: AnalyzeOptions = AnalyzeOptions()):
    try:
        client = OllamaClient(body.model) if body.provider=='ollama' else GemmaClient()
        return {'provider':body.provider,'model': client.model, 'response': client.verify_access()}
    except Exception as exc:
        raise HTTPException(502, safe_error(exc))

@app.post(P+'/investigations', status_code=201)
def create(body: Create):
    case = {'id': str(uuid4()), 'title': body.title.strip(), 'description': body.description, 'status': 'created', 'stage': 'Ready for sources', 'created_at': store.now(), 'sources': [], 'claims': [], 'findings': [], 'model_identifier': None, 'error_message': None}
    if not case['title']:
        raise HTTPException(422, 'Title cannot be empty')
    store.save(case)
    return case

@app.get(P+'/investigations')
def list_cases():
    return [{k:v for k,v in c.items() if k not in ('claims','findings','sources')} | {'source_count':len(c['sources']), 'finding_count':len(c['findings'])} for c in store.all_cases()]

@app.post(P+'/examples/internship', status_code=201)
def example():
    from .example import DOCUMENTS, authored_claims
    case = create(Create(title='The Launchpad promise',description='Synthetic internship case. Authored claims compared by real PromiseGraph rules; no model inference.'))
    for filename,text in DOCUMENTS:
        add_source(case,filename,'text/plain',text.encode(),text)
    cs, fs = investigate(authored_claims(case['sources']),{s['id']:s for s in case['sources']})
    case.update(claims=[c.model_dump() for c in cs],findings=[f.model_dump() for f in fs],status='completed',stage='Synthetic example ready',model_identifier='Authored fixture · PromiseGraph rules',is_example=True,analysis_completed_at=store.now())
    for source in case['sources']:
        source['extraction_status']='authored_fixture'
    store.save(case)
    return case

@app.get(P+'/investigations/{cid}')
def detail(cid: str):
    return require(cid)

@app.patch(P+'/investigations/{cid}')
def rename(cid: str, body: Create):
    case = editable(cid)
    case.update(title=body.title, description=body.description)
    store.save(case)
    return case

@app.delete(P+'/investigations/{cid}', status_code=204)
def delete(cid: str):
    case = editable(cid)
    for s in case['sources']:
        path = store.ROOT / s['id']
        if path.parent == store.ROOT:
            path.unlink(missing_ok=True)
    with store.connect() as con:
        con.execute('DELETE FROM investigations WHERE id=?', (cid,))

def add_source(case, filename, mime, data, text='', pages=None, published=None, version_group=None):
    if len(case['sources']) >= 12:
        raise HTTPException(422, 'An investigation supports at most 12 sources')
    sid = str(uuid4())
    filename = Path(filename.replace('\\','/')).name[:200]
    (store.ROOT / sid).write_bytes(data)
    source = {'id':sid, 'filename':filename, 'mime_type':mime, 'sha256':hashlib.sha256(data).hexdigest(), 'uploaded_at':store.now(), 'published_at':published, 'version_group':version_group, 'extracted_text':text, 'pages':pages or [], 'sequence_index':len(case['sources']), 'extraction_status':'pending'}
    case['sources'].append(source)
    case['status'] = 'created'
    store.save(case)
    return source

@app.post(P+'/investigations/{cid}/sources/text', status_code=201)
def text_source(cid: str, body: TextSource):
    case = editable(cid)
    return add_source(case, body.filename, 'text/plain', body.text.encode(), body.text, published=body.published_at.isoformat() if body.published_at else None, version_group=body.version_group)

@app.post(P+'/investigations/{cid}/sources', status_code=201)
async def upload(cid: str, files: list[UploadFile] = File(...)):
    case = editable(cid)
    if len(files) + len(case['sources']) > 12:
        raise HTTPException(422, 'Maximum 12 sources per investigation')
    prepared = []
    for file in files:
        data = await file.read(LIMIT+1)
        if not data or len(data) > LIMIT:
            raise HTTPException(413, 'Files must be between 1 byte and 12 MB')
        mime, text, pages = file.content_type, '', []
        try:
            if mime in ('image/png','image/jpeg','image/webp'):
                from PIL import Image
                with Image.open(io.BytesIO(data)) as im:
                    if im.width * im.height > 20000000:
                        raise ValueError('Image exceeds 20 megapixels')
                    detected = {'PNG':'image/png','JPEG':'image/jpeg','WEBP':'image/webp'}.get(im.format)
                    if detected != mime:
                        raise ValueError('Image MIME does not match its bytes')
                    im.verify()
            elif mime == 'application/pdf':
                import pymupdf
                with pymupdf.open(stream=data, filetype='pdf') as doc:
                    if doc.is_encrypted or doc.page_count > 20:
                        raise ValueError('PDF must be unencrypted and at most 20 pages')
                    pages = [{'page_number':i+1, 'text':p.get_text()} for i,p in enumerate(doc)]
                    text = '\n'.join(p['text'] for p in pages)
                    if len(text) > 60000:
                        raise ValueError('PDF text exceeds 60,000 characters')
            elif mime in ('text/plain','text/markdown'):
                text = data.decode('utf-8')
                if len(text)>60000:
                    raise ValueError('Text exceeds 60,000 characters')
            elif mime == 'application/json':
                batch = json.loads(data)
                entries = batch.get('sources', [])
                if not entries or len(entries)+len(prepared)+len(case['sources'])>12:
                    raise ValueError('Batch must contain sources within the 12-source limit')
                for entry in entries:
                    b = TextSource.model_validate(entry)
                    prepared.append((b.filename,'text/plain',b.text.encode(),b.text,[],b.published_at.isoformat() if b.published_at else None,b.version_group))
                continue
            else:
                raise HTTPException(415, 'Supported: PNG, JPEG, WebP, PDF, UTF-8 text, Markdown, JSON batches')
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(422, f'Invalid document: {exc}')
        prepared.append((file.filename or 'source',mime,data,text,pages,None,None))
    if len(prepared)+len(case['sources'])>12:
        raise HTTPException(422, 'Maximum 12 sources')
    return [add_source(case,*args) for args in prepared]

@app.get(P+'/investigations/{cid}/sources')
def sources(cid: str):
    return require(cid)['sources']

@app.get(P+'/sources/{sid}')
def source_metadata(sid: str):
    return find_source(sid)[1]

@app.get(P+'/sources/{sid}/content')
def content(sid: str):
    source = find_source(sid)[1]
    return FileResponse(store.ROOT / source['id'], media_type=source['mime_type'], headers={'X-Content-Type-Options':'nosniff', 'Cache-Control':'no-store'})

def images_for(source):
    data = (store.ROOT / source['id']).read_bytes()
    if source['mime_type'].startswith('image/'):
        return [(data,source['mime_type'])]
    if source['mime_type'] == 'application/pdf':
        import pymupdf
        with pymupdf.open(stream=data,filetype='pdf') as doc:
            return [(page.get_pixmap(matrix=pymupdf.Matrix(1,1)).tobytes('png'),'image/png') for page in doc]
    return []

def safe_error(exc):
    # Provider messages may contain request details. Do not persist or expose them.
    if isinstance(exc, RuntimeError):
        return str(exc)
    return f'Analysis failed ({type(exc).__name__}). Check model access, API quota and source validity; retry when resolved.'

def run_analysis(cid,provider='gemma',model=None):
    case = require(cid)
    previous = {f['id']:f for f in case['findings']}
    try:
        client = OllamaClient(model) if provider=='ollama' else GemmaClient()
        case['model_identifier'] = client.model
        case['analysis_provider'] = provider
        case['stage'] = 'Verifying '+('local Ollama' if provider=='ollama' else 'Gemma 4')+' access'
        store.save(case)
        client.verify_access()
        claims, errors = [], []
        for index,source in enumerate(case['sources']):
            case['stage'] = f'Extracting source {index+1} of {len(case["sources"])}: {source["filename"]}'
            store.save(case)
            try:
                extracted = client.extract_claims(source, images_for(source))
                for claim in extracted:
                    if source['pages']:
                        for page in source['pages']:
                            if claim.original_text in page['text']:
                                claim.page_number = page['page_number']
                                break
                claims.extend(extracted)
                source['extraction_status'] = 'completed'
            except Exception as exc:
                source['extraction_status'] = 'failed'
                errors.append(f'{source["filename"]}: {safe_error(exc)}')
            store.save(case)
        if not claims:
            raise RuntimeError('No claims were extracted. '+ ' '.join(errors))
        case['stage'] = 'Normalizing claims and verifying evidence'
        store.save(case)
        source_map = {s['id']:s for s in case['sources']}
        claims, findings = investigate(claims, source_map)
        case['stage'] = 'Reviewing ambiguous pairs with '+('local Ollama' if provider=='ollama' else 'Gemma 4')
        store.save(case)
        by_id = {c.id:c for c in claims}
        for f in findings[:20]:
            if f.status in ('potential_conflict','missing_disclosure') and f.evidence_verified:
                try:
                    semantic = client.compare_claims(by_id[f.claim_a_id],by_id[f.claim_b_id])
                    f.status = semantic.status
                    f.explanation = semantic.explanation
                    f.limitations += semantic.limitations
                    f.validation_method = 'hybrid'
                except Exception:
                    f.limitations.append('Semantic review unavailable; deterministic finding retained.')
                    errors.append('One semantic comparison failed; rule output retained.')
            if f.id in previous:
                f.review_status = previous[f.id]['review_status']
                f.review_notes = previous[f.id].get('review_notes','')
        case['claims'] = [c.model_dump() for c in claims]
        case['findings'] = [f.model_dump() for f in findings]
        case['status'] = 'partial' if errors else 'completed'
        case['stage'] = 'Completed with some extraction or semantic errors' if errors else 'Investigation complete'
        case['error_message'] = '\n'.join(errors) or None
        case['analysis_completed_at'] = store.now()
    except Exception as exc:
        case['status'], case['stage'], case['error_message'] = 'failed','Analysis failed',safe_error(exc)
    store.save(case)

@app.post(P+'/investigations/{cid}/analyze', status_code=202)
def analyze(cid: str, background: BackgroundTasks, body: AnalyzeOptions = AnalyzeOptions()):
    with store.LOCK:
        case = editable(cid)
        if len(case['sources'])<2:
            raise HTTPException(422, 'Add at least two sources to compare')
        if body.provider=='gemma' and not os.getenv('GEMINI_API_KEY'):
            raise HTTPException(503, 'Gemma is not configured. Set GEMINI_API_KEY in the backend .env and restart.')
        case.update(status='processing',stage='Queued for '+body.provider,analysis_started_at=store.now(),error_message=None)
        store.save(case)
    background.add_task(run_analysis,cid,body.provider,body.model)
    return {'analysis_id':case['analysis_started_at'], 'status':'processing'}

@app.get(P+'/investigations/{cid}/analysis-status')
def status(cid: str):
    c = require(cid)
    return {k:c.get(k) for k in ('status','stage','error_message','analysis_started_at','analysis_completed_at')}

@app.get(P+'/investigations/{cid}/claims')
def claims(cid: str):
    return require(cid)['claims']

@app.get(P+'/investigations/{cid}/findings')
def findings(cid: str):
    return require(cid)['findings']

@app.get(P+'/investigations/{cid}/graph')
def evidence_graph(cid: str):
    c = require(cid)
    return graph([Claim.model_validate(x) for x in c['claims']], [Finding.model_validate(x) for x in c['findings']], {s['id']:s for s in c['sources']})

@app.get(P+'/investigations/{cid}/timeline')
def timeline(cid: str):
    c = require(cid)
    dated = all(s.get('published_at') for s in c['sources']) and bool(c['sources'])
    ordered = sorted(c['sources'],key=lambda s: s['published_at'] if dated else s['sequence_index'])
    return {'mode':'publication_dates' if dated else 'document_sequence', 'sources':ordered, 'changes':[f for f in c['findings'] if f['status']=='changed_term']}

@app.patch(P+'/findings/{fid}/review')
def review(fid: str, body: Review):
    with store.LOCK:
        for case in store.all_cases():
            for f in case['findings']:
                if f['id'] == fid:
                    if case['status']=='processing':
                        raise HTTPException(409,'Wait for analysis to finish before reviewing')
                    f.update(body.model_dump())
                    store.save(case)
                    return f
    raise HTTPException(404,'Finding not found')

def markdown(c):
    lookup = {x['id']:x for x in c['claims']}
    source_lookup = {s['id']:s for s in c['sources']}
    lines = [f'# {c["title"]}', '', '## Scope and limitations', 'Decision support, not proof of fraud. Sources may concern different populations, stages or time periods. Human review is required. Image quotations remain unverified unless corroborated by extracted text.', '',f'Model: {c.get("model_identifier") or "Not analyzed"}', f'Analysis: {c.get("analysis_completed_at") or "Not completed"}',f'Generated: {store.now()}', '', '## Sources']
    for s in c['sources']:
        lines += [f'- {s["filename"]} ({s["id"]}); SHA-256: {s["sha256"]}; published: {s.get("published_at") or "unknown"}; uploaded: {s["uploaded_at"]}']
    lines += ['', '## Findings']
    for f in c['findings']:
        lines += ['',f'### {f["title"]}', f'Status: {f["status"]}; review: {f["review_status"]}; verified: {f["evidence_verified"]}',f['explanation']]
        for cid in [f['claim_a_id'],f['claim_b_id']]:
            claim = lookup[cid]
            lines += [f'> {claim["original_text"]}',f'Source: {source_lookup[claim["source_id"]]["filename"]}; page: {claim.get("page_number") or "n/a"}; location: {claim["location_quality"]}']
        lines += ['Limitations: '+' '.join(f['limitations']), 'Analyst notes: '+f.get('review_notes','')]
    lines += ['', '## Timeline', 'Publication dates are shown only when supplied. Otherwise document sequence is used.']
    for s in c['sources']:
        lines += [f'- {s.get("published_at") or "Undated"}: {s["filename"]}']
    lines += ['', '## Unverified matters', 'Source authenticity, equivalent offer scope, and undisclosed context are not independently established.', '', '## Questions to ask', 'Which terms govern participation? Are fees mandatory? Which conditions apply to compensation and certification?', '', '## Methodology', 'Gemma 4 extracts structured claims from text and images. PromiseGraph normalizes claims, matches comparable subjects, checks numeric and guarantee rules, validates quotations, and constructs a provenance graph. Ambiguous findings receive bounded Gemma semantic review. Findings are not calibrated fraud probabilities.']
    return '\n\n'.join(lines)

@app.get(P+'/investigations/{cid}/report')
def report(cid: str, format: Literal['json','markdown','pdf']='json'):
    c = require(cid)
    headers = {'Content-Disposition':f'attachment; filename="investigation-{cid}.{ {"json":"json","markdown":"md","pdf":"pdf"}[format]}"','Cache-Control':'no-store'}
    if format=='json':
        return Response(json.dumps(c,indent=2),media_type='application/json',headers=headers)
    text = markdown(c)
    if format=='markdown':
        return Response(text,media_type='text/markdown',headers=headers)
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from xml.sax.saxutils import escape
    stream = io.BytesIO()
    doc = SimpleDocTemplate(stream,title=c['title'],leftMargin=48,rightMargin=48)
    styles = getSampleStyleSheet()
    flow = []
    for line in text.split('\n\n'):
        style = styles['Heading1'] if line.startswith('# ') else styles['Heading2'] if line.startswith('##') else styles['BodyText']
        flow += [Paragraph(escape(line.lstrip('# ').replace('₹','INR ')),style),Spacer(1,8)]
    doc.build(flow)
    return Response(stream.getvalue(),media_type='application/pdf',headers=headers)

# Persisted in-process jobs interrupted by a restart must not remain stuck forever.
for interrupted in store.all_cases():
    if interrupted['status']=='processing':
        interrupted.update(status='failed',stage='Interrupted by server restart',error_message='The previous job was interrupted. Run analysis again.')
        store.save(interrupted)

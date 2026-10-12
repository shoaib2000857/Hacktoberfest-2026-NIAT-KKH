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
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Request
from starlette.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field
from promisegraph import Claim, Finding, investigate, graph, candidates, verify
from . import store
from .gemma import GemmaClient, PROMPT_VERSION
from .ollama import OllamaClient, installed_models
from promisegraph.extensions import financial, conditions, personal, receipt, journey, compare_extended
from promisegraph import normalize

app = FastAPI(title='PromiseTrap', version='0.2.0')
app.add_middleware(TrustedHostMiddleware,allowed_hosts=['127.0.0.1','localhost','testserver'])
LOCAL_ORIGINS={'http://127.0.0.1:3000','http://localhost:3000','http://127.0.0.1:8000','http://localhost:8000'}
@app.middleware('http')
async def local_browser_access(request: Request,call_next):
    origin=request.headers.get('origin')
    if (origin and origin not in LOCAL_ORIGINS) or request.headers.get('sec-fetch-site')=='cross-site':
        return Response('Cross-origin browser access is disabled.',status_code=403)
    response=await call_next(request)
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['Cache-Control']='no-store'
    return response

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

def preserve_reviews(findings, previous):
    by_id={f['id']:f for f in previous}
    keys=('status','explanation','scope','evidence_verified','limitations')
    for finding in findings:
        old=by_id.get(finding.id)
        if old and all(old.get(k)==finding.model_dump(mode='json').get(k) for k in keys):
            finding.review_status=old['review_status']
            finding.review_notes=old.get('review_notes','')
            finding.alternative=old.get('alternative')
    return findings

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
    document_stage: Literal['advertisement','registration','selection','offer','agreement','other'] = 'other'
    effective_at: date | None = None

class SourceMetadata(BaseModel):
    document_stage: Literal['advertisement','registration','selection','offer','agreement','other'] = 'other'
    published_at: date | None = None
    effective_at: date | None = None
    version_group: str | None = Field(default=None,max_length=100)

class Simulation(BaseModel):
    a: Claim
    b: Claim

class Profile(BaseModel):
    year_of_study: str | None = Field(default=None,max_length=40)
    degree: str | None = Field(default=None,max_length=100)
    location: str | None = Field(default=None,max_length=100)
    academic_score: str | None = Field(default=None,max_length=40)

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
    for index,(filename,text) in enumerate(DOCUMENTS):
        add_source(case,filename,'text/plain',text.encode(),text,document_stage=['advertisement','registration','offer'][index])
    cs, fs = investigate(authored_claims(case['sources']),{s['id']:s for s in case['sources']})
    case.update(claims=[c.model_dump() for c in cs],findings=[f.model_dump() for f in fs],status='completed',stage='Synthetic example ready',model_identifier='Authored fixture · PromiseGraph rules',is_example=True,claims_provenance='authored_fixture',analysis_completed_at=store.now())
    for source in case['sources']:
        source['extraction_status']='authored_fixture'
    store.save(case)
    return detail(case['id'])

@app.get(P+'/investigations/{cid}')
def detail(cid: str):
    case=require(cid)
    source_map={s['id']:s for s in case['sources']}
    claims=[Claim.model_validate(c) for c in case['claims']]
    return case | {'financial':financial(claims,source_map),'conditions':conditions(claims,source_map),'receipt':receipt(case),'journey':journey(case)}

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
        con.execute('DELETE FROM extraction_cache')

def add_source(case, filename, mime, data, text='', pages=None, published=None, version_group=None, document_stage='other', effective_at=None):
    if len(case['sources']) >= 12:
        raise HTTPException(422, 'An investigation supports at most 12 sources')
    sid = str(uuid4())
    filename = Path(filename.replace('\\','/')).name[:200]
    (store.ROOT / sid).write_bytes(data)
    source = {'id':sid, 'filename':filename, 'mime_type':mime, 'sha256':hashlib.sha256(data).hexdigest(), 'uploaded_at':store.now(), 'published_at':published, 'effective_at':effective_at, 'document_stage':document_stage, 'version_group':version_group, 'extracted_text':text, 'pages':pages or [], 'sequence_index':len(case['sources']), 'extraction_status':'pending'}
    case['sources'].append(source)
    case['status'] = 'created'
    store.save(case)
    return source

@app.post(P+'/investigations/{cid}/sources/text', status_code=201)
def text_source(cid: str, body: TextSource):
    case = editable(cid)
    return add_source(case, body.filename, 'text/plain', body.text.encode(), body.text, published=body.published_at.isoformat() if body.published_at else None, version_group=body.version_group,document_stage=body.document_stage,effective_at=body.effective_at.isoformat() if body.effective_at else None)

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
                    if doc.is_encrypted or not doc.page_count or doc.page_count > 20:
                        raise ValueError('PDF must be unencrypted and at most 20 pages')
                    if any(max(p.rect.width,p.rect.height)>14400 or min(p.rect.width,p.rect.height)<=0 for p in doc):
                        raise ValueError('PDF page dimensions are outside the supported range')
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
                    prepared.append((b.filename,'text/plain',b.text.encode(),b.text,[],b.published_at.isoformat() if b.published_at else None,b.version_group,b.document_stage,b.effective_at.isoformat() if b.effective_at else None))
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

@app.patch(P+'/sources/{sid}')
def update_source(sid: str, body: SourceMetadata):
    with store.LOCK:
        case,source=find_source(sid)
        editable(case['id'])
        source.update(body.model_dump(mode='json'))
        case.setdefault('history',[]).append({'at':store.now(),'action':'source_metadata_review','source_id':sid,'previous_findings':case['findings']})
        # Revalidate existing claims and compare using supplied effective/version metadata.
        cs,fs=investigate([Claim.model_validate(c) for c in case['claims']],{s['id']:s for s in case['sources']})
        case['claims'],case['findings']=[c.model_dump(mode='json') for c in cs],[f.model_dump(mode='json') for f in preserve_reviews(fs,case['findings'])]
        store.save(case)
        return source

@app.post(P+'/sources/{sid}/verify')
async def verify_copy(sid: str, file: UploadFile):
    source=find_source(sid)[1]
    data=await file.read(LIMIT+1)
    if len(data)>LIMIT:
        raise HTTPException(413,'Copy exceeds 12 MB')
    digest=hashlib.sha256(data).hexdigest()
    return {'byte_identical':digest==source['sha256'],'uploaded_sha256':digest,'recorded_sha256':source['sha256'],'notice':'Byte comparison only; no proof of origin, authorship or historical authenticity.'}

@app.get(P+'/sources/{sid}/page/{number}')
def pdf_page(sid: str, number: int):
    source=find_source(sid)[1]
    if source['mime_type']!='application/pdf':
        raise HTTPException(400,'Source is not a PDF')
    import pymupdf
    with pymupdf.open(store.ROOT/source['id']) as doc:
        if number<1 or number>len(doc):
            raise HTTPException(404,'PDF page not found')
        page=doc[number-1]
        scale=min(1.5,1600/max(page.rect.width,page.rect.height))
        data=page.get_pixmap(matrix=pymupdf.Matrix(scale,scale),alpha=False).tobytes('png')
    return Response(data,media_type='image/png')

def images_for(source):
    data = (store.ROOT / source['id']).read_bytes()
    if source['mime_type'].startswith('image/'):
        return [(data,source['mime_type'])]
    if source['mime_type'] == 'application/pdf':
        import pymupdf
        with pymupdf.open(stream=data,filetype='pdf') as doc:
            return [(page.get_pixmap(matrix=pymupdf.Matrix(min(1.5,1600/max(page.rect.width,page.rect.height)),min(1.5,1600/max(page.rect.width,page.rect.height))),alpha=False).tobytes('png'),'image/png') for page in doc]
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
                if hashlib.sha256((store.ROOT/source['id']).read_bytes()).hexdigest()!=source['sha256']:
                    raise RuntimeError('Stored source bytes differ from their recorded hash. Add a new source before analysis.')
                cache_key=hashlib.sha256(json.dumps([source['id'],source['sha256'],client.model,PROMPT_VERSION,source.get('document_stage'),source.get('effective_at'),source.get('published_at'),source.get('version_group')]).encode()).hexdigest()
                cached=store.cached(cache_key)
                extracted=[Claim.model_validate(c) for c in cached] if cached is not None else client.extract_claims(source,images_for(source))
                if any(c.source_id!=source['id'] for c in extracted):
                    raise ValueError('Model returned an invalid source reference')
                store.cache(cache_key,[c.model_dump(mode='json') for c in extracted])
                for claim in extracted:
                    claim.page_number=None
                    if source['pages']:
                        for page in source['pages']:
                            if claim.original_text in page['text']:
                                claim.page_number = page['page_number']
                                break
                claims.extend(extracted)
                source['extraction_status'] = 'completed'
                source.update(model_identifier=client.model,prompt_version=PROMPT_VERSION,analyzed_at=store.now(),extraction_error=None)
            except Exception as exc:
                source.update(model_identifier=client.model,prompt_version=PROMPT_VERSION,analyzed_at=store.now())
                source['extraction_status'] = 'failed'
                source['extraction_error']=safe_error(exc)
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
        for index,f in enumerate(findings):
            if index<20 and f.status in ('potential_conflict','missing_disclosure','material_qualification') and f.evidence_verified:
                try:
                    semantic = client.compare_claims(by_id[f.claim_a_id],by_id[f.claim_b_id])
                    f.semantic_review = semantic.model_dump()
                    f.validation_method = 'hybrid'
                except Exception:
                    f.limitations.append('Semantic review unavailable; deterministic finding retained.')
                    errors.append('One semantic comparison failed; rule output retained.')
        preserve_reviews(findings,list(previous.values()))
        case['claims_provenance']='model:'+client.model
        case['claims'] = [c.model_dump(mode='json') for c in claims]
        case['findings'] = [f.model_dump(mode='json') for f in findings]
        case['status'] = 'partial' if errors else 'completed'
        case['stage'] = 'Completed with some extraction or semantic errors' if errors else 'Investigation complete'
        case['error_message'] = '\n'.join(errors) or None
        case['analysis_completed_at'] = store.now()
        case.setdefault('history',[]).append({'at':store.now(),'action':'analysis','model':client.model,'provider':provider})
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
    ordered = journey(c)['sources']
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
                    case.setdefault('history',[]).append({'at':store.now(),'action':'finding_review','finding_id':fid,'status':body.review_status})
                    store.save(case)
                    return f
    raise HTTPException(404,'Finding not found')

@app.patch(P+'/investigations/{cid}/claims/{claim_id}')
def review_claim(cid: str, claim_id: str, body: Claim):
    with store.LOCK:
        case=editable(cid)
        old=next((c for c in case['claims'] if c['id']==claim_id),None)
        if not old or body.id!=claim_id or body.source_id!=old['source_id']:
            raise HTTPException(422,'Claim identity cannot be changed')
        previous_findings=case['findings']
        claims=[body if c['id']==claim_id else Claim.model_validate(c) for c in case['claims']]
        cs,fs=investigate(claims,{s['id']:s for s in case['sources']})
        case['claims'],case['findings']=[c.model_dump(mode='json') for c in cs],[f.model_dump(mode='json') for f in preserve_reviews(fs,case['findings'])]
        case.setdefault('history',[]).append({'at':store.now(),'action':'claim_review','claim_id':claim_id,'before':old,'after':body.model_dump(mode='json'),'previous_findings':previous_findings})
        store.save(case)
        return next(c for c in case['claims'] if c['id']==claim_id)

@app.post(P+'/investigations/{cid}/simulate')
def simulate_pair(cid: str, body: Simulation):
    case=require(cid)
    a,b=normalize(body.a,from_quote=False),normalize(body.b,from_quote=False)
    # Structured normalization deliberately bypasses original quote inference in the hypothetical copy.
    source_map={s['id']:s for s in case['sources']}
    if a.source_id not in source_map or b.source_id not in source_map:
        raise HTTPException(422,'Simulation must reference existing evidence')
    result=compare_extended(a,b,source_map,hypothetical=True)
    result.evidence_verified=False
    return {'hypothetical':True,'finding':result.model_dump(mode='json'),'method':'Structured fields normalized and rerun through PromiseGraph; no new image inference. Original evidence preserved.'}

@app.post(P+'/investigations/{cid}/eligibility')
def check_profile(cid: str, body: Profile):
    case=require(cid)
    return {'results':personal([Claim.model_validate(c) for c in case['claims']],{s['id']:s for s in case['sources']},body.model_dump()),'notice':'Eligibility support only. Profile is not stored; unknown rules require clarification.'}

@app.post(P+'/investigations/{cid}/clarify')
def clarification(cid: str, body: AnalyzeOptions | None = None):
    case=editable(cid)
    selected=[f for f in case['findings'] if f['status']!='consistent' and f['review_status']!='rejected']
    if not selected:
        raise HTTPException(422,'No unresolved findings to clarify')
    claims=[c for c in case['claims'] if any(c['id'] in [f['claim_a_id'],f['claim_b_id']] for f in selected)]
    if body:
        try:
            client=OllamaClient(body.model) if body.provider=='ollama' else GemmaClient()
            output=client.clarify_findings(selected,claims)
            questions=output.questions
        except Exception as exc:
            raise HTTPException(502,safe_error(exc)) from None
        method=client.model
    else:
        lookup={c['id']:c for c in claims}
        questions=[]
        for f in selected:
            a,b=[lookup[id]['original_text'] for id in (f['claim_a_id'],f['claim_b_id'])]
            request=('Could you confirm which terms apply to the same applicants and effective period?' if f['status'] in {'contradiction','potential_conflict','changed_term'} else 'Could you explain how these qualifications apply and clarify the missing information?')
            questions.append(f'One source states "{a}"; another states "{b}". {request} [Finding {f["id"]}]')
        method='Deterministic evidence template'
    draft='Hello,\n\nI am reviewing the opportunity and would appreciate clarification:\n\n'+'\n\n'.join(questions)+'\n\nSupporting excerpts:\n'+'\n'.join('"'+c['original_text']+'" [source '+c['source_id']+'; claim '+c['id']+']' for c in claims)+'\n\nThank you.'
    case['clarification_draft']=draft
    case.setdefault('history',[]).append({'at':store.now(),'action':'clarification','model':method})
    store.save(case)
    return {'draft':draft,'method':method}

@app.post(P+'/investigations/{cid}/findings/{fid}/challenge')
def challenge(cid: str, fid: str, body: AnalyzeOptions=AnalyzeOptions()):
    case=editable(cid)
    f=next((f for f in case['findings'] if f['id']==fid),None)
    if not f:
        raise HTTPException(404,'Finding not found')
    pair=[c for c in case['claims'] if c['id'] in [f['claim_a_id'],f['claim_b_id']]]
    try:
        client=OllamaClient(body.model) if body.provider=='ollama' else GemmaClient()
        output=client.challenge_finding(f,pair)
    except Exception as exc:
        raise HTTPException(502,safe_error(exc)) from None
    # Reload before saving to preserve concurrent analyst review.
    with store.LOCK:
        case=editable(cid)
        current=next(x for x in case['findings'] if x['id']==fid)
        current['alternative']=output.model_dump(mode='json')
        case.setdefault('history',[]).append({'at':store.now(),'action':'challenge','finding_id':fid,'model':client.model})
        store.save(case)
    return output

@app.get(P+'/investigations/{cid}/receipt')
def evidence_receipt(cid: str):
    return Response(json.dumps(receipt(require(cid)),indent=2),media_type='application/json',headers={'Content-Disposition':'attachment; filename="promisetrap-receipt.json"'})

@app.post(P+'/examples/advanced/{scenario}',status_code=201)
def advanced_example(scenario: str, images: bool=False):
    from .advanced_samples import DATASETS, document, SAMPLES
    if scenario not in DATASETS:
        raise HTTPException(404,'Unknown fictional sample')
    case=create(Create(title='Fictional '+scenario+' investigation',description='Explicit fictional sources. Image mode requires real model analysis; fixtures are authored.'))
    case.update(is_example=True,example_mode='fictional_images' if images else 'authored_fixture',claims_provenance='none' if images else 'authored_fixture')
    claims=[]
    for item in DATASETS[scenario]:
        name=item['name']+('.png' if images else '.txt')
        data=(SAMPLES/name).read_bytes() if images else document(item).encode()
        source=add_source(case,name,'image/png' if images else 'text/plain',data,'' if images else data.decode(),published=item.get('date'),version_group='nova-deadline' if item.get('date') else None,document_stage=item['stage'],effective_at=item.get('date'))
        source['extraction_status']='pending' if images else 'authored_fixture'
        if not images:
            for raw in item['claims']:
                fields={**raw}
                fields.setdefault('scope',{'program':'fictional nova 2026','audience':'all registered applicants','purpose':'registration','period':'2026 intake','application_stage':'registration','contractual_condition':'nova 2026 terms','qualifying_event':'registration'})
                claims.append(Claim(id=str(uuid4()),source_id=source['id'],category={'fee':'financial','certificate':'certification'}.get(fields['category'],fields['category']),subject=fields['subject'],predicate=fields['predicate'],value=fields.get('date_value',fields.get('amount')),currency=fields.get('currency'),unit=fields.get('unit'),modality={'mandatory':'required','unspecified':'asserted'}.get(fields.get('modality','asserted'),fields.get('modality','asserted')),original_text=fields['original_text'],normalized_summary=fields['normalized_statement'],conditions=fields.get('conditions',[]),scope=fields['scope'],value_kind=fields.get('value_kind','unspecified'),financial_role=fields.get('financial_role'),payment_timing=fields.get('payment_timing'),applicable_cost=fields.get('applicable_cost'),criteria=fields.get('criteria',[])))
    if not images:
        cs,fs=investigate(claims,{s['id']:s for s in case['sources']})
        case.update(claims=[c.model_dump(mode='json') for c in cs],findings=[f.model_dump(mode='json') for f in fs],status='completed',stage='Authored fixture compared by PromiseGraph',model_identifier='Authored fixture · PromiseGraph rules',is_example=True)
    store.save(case)
    return detail(case['id'])

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
    lines += ['', '## Promise Journey', journey(c)['note']]
    for s in journey(c)['sources']:
        lines += [f'- {s.get("published_at") or "Undated"}: {s["filename"]}']
    lines += ['', '## Unverified matters', 'Source authenticity, equivalent offer scope, and undisclosed context are not independently established.', '', '## Questions to ask', 'Which terms govern participation? Are fees mandatory? Which conditions apply to compensation and certification?', '', '## Methodology', 'Gemma 4 extracts structured claims from text and images. PromiseGraph normalizes claims, matches comparable subjects, checks numeric and guarantee rules, validates quotations, and constructs a provenance graph. Ambiguous findings receive bounded Gemma semantic review. Findings are not calibrated fraud probabilities.']
    data=financial([Claim.model_validate(x) for x in c['claims']],source_lookup)
    lines += ['', '## Reality Calculator',data['method']]
    for currency,total in data['currencies'].items():
        lines += [f"{currency}: mandatory upfront fees {total['mandatory_upfront_cost']}; optional fees {total['optional_fees']}; deposits {total['deposits']}; fixed deductions {total['fixed_deductions']}."]
        for kind in ('guaranteed_compensation','conditional_compensation','potential_compensation'):
            lines += [f"{kind.replace('_',' ')}: "+('; '.join(f"{v['amount']} {currency} per {v['unit']} [claim {v['claim_id']}]" for v in total[kind]) or 'not established')]
    lines += data['uncertainties']+[data['refund_policy'],'','## FinePrint Radar & ConditionChain']
    for group in conditions([Claim.model_validate(x) for x in c['claims']],source_lookup):
        lines += [group['benefit']+' [claim '+group['claim_id']+']',group['ordering']]+[x['text']+(' — absent from advertised conditions' if x['not_in_advertisement'] else '') for x in group['conditions']]
    lines += ['','## Alternative interpretations']
    for f in c['findings']:
        if f.get('alternative'):
            alt=f['alternative']
            lines += [f['title'],alt['interpretation'],'Suggestion only: '+alt['recommended_classification'],'Supporting claims: '+', '.join(alt['supporting_claim_ids']),'Weakening claims: '+', '.join(alt['weakening_claim_ids'])]+alt['unresolved_questions']
    lines += ['','## Clarification draft',c.get('clarification_draft') or 'No draft generated.','Messages are never sent.','','## Promise Receipt','Recorded hashes compare bytes only; they do not authenticate origin or historical provenance.','','## Review history']
    lines += [f"{h['at']}: {h['action']} {h.get('model','')} {h.get('status','')}" for h in c.get('history',[])]
    return '\n\n'.join(lines)

@app.get(P+'/investigations/{cid}/report')
def report(cid: str, format: Literal['json','markdown','pdf']='json'):
    c = detail(cid)
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
        spacer=Spacer(1,8)
        if line.startswith('#'):
            spacer.keepWithNext=True
        flow += [Paragraph(escape(line.lstrip('# ').replace('₹','INR ')),style),spacer]
    doc.build(flow)
    return Response(stream.getvalue(),media_type='application/pdf',headers=headers)

# Persisted in-process jobs interrupted by a restart must not remain stuck forever.
for interrupted in store.all_cases():
    if interrupted['status']=='processing':
        interrupted.update(status='failed',stage='Interrupted by server restart',error_message='The previous job was interrupted. Run analysis again.')
        store.save(interrupted)

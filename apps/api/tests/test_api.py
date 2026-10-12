import io
import importlib
import json
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setenv('PROMISETRAP_DATA_DIR',str(tmp_path))
    monkeypatch.setenv('GEMINI_API_KEY','')
    import app.store
    importlib.reload(app.store)
    import app.main
    importlib.reload(app.main)
    with TestClient(app.main.app) as c:
        yield c

def test_create_source_hash_preview_delete(client):
    r=client.post('/api/v1/investigations',json={'title':'Test case'})
    assert r.status_code==201
    cid=r.json()['id']
    s=client.post(f'/api/v1/investigations/{cid}/sources/text',json={'filename':'../../ad.txt','text':'Free registration.'}).json()
    assert s['filename']=='ad.txt' and len(s['sha256'])==64
    assert client.get('/api/v1/sources/'+s['id']+'/content').content==b'Free registration.'
    assert client.delete('/api/v1/investigations/'+cid).status_code==204
    assert client.get('/api/v1/sources/'+s['id']+'/content').status_code==404

def test_synthetic_end_to_end_review_export(client):
    case=client.post('/api/v1/examples/internship').json()
    assert case['is_example'] and len(case['findings'])==3 and len(case['claims'])==9
    cid=case['id']
    assert client.get(f'/api/v1/investigations/{cid}/graph').status_code==200
    assert client.get(f'/api/v1/investigations/{cid}/timeline').json()['mode']=='document_sequence'
    fid=case['findings'][0]['id']
    assert client.patch('/api/v1/findings/'+fid+'/review',json={'review_status':'accepted','review_notes':'Scope checked'}).json()['review_status']=='accepted'
    assert 'Scope checked' in client.get(f'/api/v1/investigations/{cid}/report?format=markdown').text
    assert client.get(f'/api/v1/investigations/{cid}/report?format=pdf').content.startswith(b'%PDF')
    assert client.get(f'/api/v1/investigations/{cid}/report?format=json').json()['sources'][0]['sha256']

def test_no_key_no_fake_output(client):
    case=client.post('/api/v1/examples/internship').json()
    response=client.post('/api/v1/investigations/'+case['id']+'/analyze')
    assert response.status_code==503
    assert client.get('/api/v1/investigations/'+case['id']).json()['model_identifier'].startswith('Authored fixture')

def test_invalid_image_rejected(client):
    cid=client.post('/api/v1/investigations',json={'title':'Invalid'}).json()['id']
    assert client.post(f'/api/v1/investigations/{cid}/sources',files={'files':('ad.png',b'not an image','image/png')}).status_code==422

def test_pdf_pages_and_preview(client):
    import pymupdf
    doc=pymupdf.open();page=doc.new_page();page.insert_text((50,50),'Registration is free.')
    data=doc.tobytes();doc.close()
    cid=client.post('/api/v1/investigations',json={'title':'PDF test'}).json()['id']
    response=client.post(f'/api/v1/investigations/{cid}/sources',files={'files':('ad.pdf',data,'application/pdf')})
    assert response.status_code==201
    source=response.json()[0]
    assert source['pages'][0]['page_number']==1 and 'Registration is free.' in source['extracted_text']
    assert client.get('/api/v1/sources/'+source['id']+'/content').content==data

def test_batch_date_validation(client):
    cid=client.post('/api/v1/investigations',json={'title':'Batch'}).json()['id']
    body=json.dumps({'sources':[{'filename':'ad','text':'Free registration.','published_at':'2026-10-12'}]}).encode()
    response=client.post(f'/api/v1/investigations/{cid}/sources',files={'files':('sources.json',body,'application/json')})
    assert response.status_code==201 and response.json()[0]['published_at']=='2026-10-12'

def test_mock_gemma_pipeline_and_review_preservation(client,monkeypatch):
    import app.main
    from app.example import authored_claims
    case=client.post('/api/v1/examples/internship').json()
    claims=authored_claims(case['sources'])
    # Stable IDs here model adapter supplies IDs derived from source and quotation.
    class Fake:
        model='gemma-4-26b-a4b-it'
        def verify_access(self):return 'READY'
        def extract_claims(self,source,images):return [c for c in claims if c.source_id==source['id']]
        def compare_claims(self,a,b):raise ValueError('not needed in this direct-conflict case')
    monkeypatch.setattr(app.main,'GemmaClient',Fake)
    monkeypatch.setenv('GEMINI_API_KEY','test-not-a-real-key')
    r=client.post('/api/v1/investigations/'+case['id']+'/analyze')
    assert r.status_code==202
    c=client.get('/api/v1/investigations/'+case['id']).json()
    assert c['status']=='completed' and len(c['findings'])==3
    f=c['findings'][0]
    client.patch('/api/v1/findings/'+f['id']+'/review',json={'review_status':'accepted','review_notes':'Keep this'})
    client.post('/api/v1/investigations/'+case['id']+'/analyze')
    c=client.get('/api/v1/investigations/'+case['id']).json()
    assert next(x for x in c['findings'] if x['id']==f['id'])['review_notes']=='Keep this'

def test_mock_extraction_failure_visible(client,monkeypatch):
    import app.main
    class Broken:
        model='gemma-4-26b-a4b-it'
        def verify_access(self):raise ValueError('provider error with secrets')
    monkeypatch.setattr(app.main,'GemmaClient',Broken)
    monkeypatch.setenv('GEMINI_API_KEY','test')
    cid=client.post('/api/v1/examples/internship').json()['id']
    client.post(f'/api/v1/investigations/{cid}/analyze')
    c=client.get('/api/v1/investigations/'+cid).json()
    assert c['status']=='failed' and 'secrets' not in c['error_message']

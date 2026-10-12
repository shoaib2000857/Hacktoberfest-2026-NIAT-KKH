"""Integration checks use authored fixtures, not simulated live-model success."""
from test_api import client
import hashlib
import copy
import pytest

P='/api/v1'

def sample(client,name):
    response=client.post(P+'/examples/advanced/'+name)
    assert response.status_code==201,response.text
    return response.json()

@pytest.mark.parametrize('name,count,statuses',[
    ('internship',3,{'contradiction'}),('scholarship',1,{'contradiction'}),
    ('optional',0,set()),('deadline',1,{'changed_term'})])
def test_four_authored_scenarios(client,name,count,statuses):
    c=sample(client,name)
    assert len(c['findings'])==count
    assert {f['status'] for f in c['findings']}==statuses
    assert all(f['evidence_verified'] for f in c['findings'])
    assert c['model_identifier'].startswith('Authored fixture')
    assert all('FICTIONAL SAMPLE' in s['extracted_text'] for s in c['sources'])

def test_calculator_optional_rates_guarantees_refund(client):
    c=sample(client,'internship');totals=c['financial']['currencies']['INR']
    assert totals['mandatory_upfront_cost']=='499'
    assert totals['guaranteed_compensation']==[]
    assert totals['conditional_compensation'][0]['amount']=='20000'
    assert 'Unknown' in c['financial']['refund_policy']
    optional=sample(client,'optional')['financial']['currencies']['INR']
    assert optional['mandatory_upfront_cost']=='0' and optional['optional_fees']=='200'

def test_promiselab_preserves_original_and_uses_edited_fields(client):
    c=sample(client,'internship');cid=c['id']
    f=next(f for f in c['findings'] if f['category']=='financial')
    a,b=[copy.deepcopy(next(x for x in c['claims'] if x['id']==id)) for id in (f['claim_a_id'],f['claim_b_id'])]
    b.update(subject='printed certificate',modality='optional',conditions=[])
    b['scope'].update(purpose='printed certificate',application_stage='completion')
    r=client.post(f'{P}/investigations/{cid}/simulate',json={'a':a,'b':b})
    assert r.status_code==200,r.text
    assert r.json()['hypothetical'] and r.json()['finding']['status']=='insufficient_evidence'
    assert not r.json()['finding']['evidence_verified']
    current=client.get(f'{P}/investigations/{cid}').json()
    assert current['claims']==c['claims'] and current['findings']==c['findings']
    b['source_id']='invented'
    assert client.post(f'{P}/investigations/{cid}/simulate',json={'a':a,'b':b}).status_code==422

def test_personal_criteria_are_not_persisted(client):
    c=sample(client,'scholarship');path=f'{P}/investigations/{c["id"]}'
    unknown=client.post(path+'/eligibility',json={}).json()
    assert unknown['results'][0]['status']=='unknown'
    assert client.post(path+'/eligibility',json={'year_of_study':'2'}).json()['results'][0]['status']=='not_satisfied'
    assert client.post(path+'/eligibility',json={'year_of_study':'4'}).json()['results'][0]['status']=='satisfied'
    assert 'profile' not in client.get(path).json()

def test_receipt_hash_equal_different_and_draft_report(client):
    c=sample(client,'internship');s=c['sources'][0];path=f'{P}/investigations/{c["id"]}'
    data=client.get(P+'/sources/'+s['id']+'/content').content
    assert hashlib.sha256(data).hexdigest()==s['sha256']
    for data,equal in [(data,True),(data+b'edited',False)]:
        assert client.post(P+'/sources/'+s['id']+'/verify',files={'file':('copy',data)}).json()['byte_identical']==equal
    draft=client.post(path+'/clarify').json()['draft']
    assert all(x['original_text'] in draft for x in c['claims'])
    assert client.get(path+'/receipt').json()['sources'][0]['sha256']==s['sha256']
    report=client.get(path+'/report?format=markdown').text
    assert 'Reality Calculator' in report and '499' in report and 'Clarification draft' in report
    assert client.get(path+'/report?format=json').json()['financial']

def test_review_preserved_on_unchanged_metadata_and_claim_rejections(client):
    c=sample(client,'internship');f=c['findings'][0];s=c['sources'][0]
    client.patch(P+'/findings/'+f['id']+'/review',json={'review_status':'accepted','review_notes':'Checked scope'})
    r=client.patch(P+'/sources/'+s['id'],json={'document_stage':s['document_stage']})
    assert r.status_code==200
    c=client.get(P+'/investigations/'+c['id']).json()
    assert next(x for x in c['findings'] if x['id']==f['id'])['review_notes']=='Checked scope'
    claim=next(x for x in c['claims'] if x['id']==f['claim_a_id']);claim['review_status']='rejected'
    client.patch(f'{P}/investigations/{c["id"]}/claims/{claim["id"]}',json=claim)
    c=client.get(P+'/investigations/'+c['id']).json()
    assert all(claim['id'] not in (x['claim_a_id'],x['claim_b_id']) for x in c['findings'])
    assert c['history'][-1]['action']=='claim_review'

def test_images_are_real_and_have_no_authored_extractions(client):
    c=client.post(P+'/examples/advanced/internship?images=true').json()
    assert c['status']=='created' and c['claims']==[] and c['findings']==[]
    assert client.get(P+'/sources/'+c['sources'][0]['id']+'/content').content.startswith(b'\x89PNG')

def test_bad_model_challenge_references_cannot_change_finding(client,monkeypatch):
    import app.main
    from app.gemma import GemmaClient
    class Bad(GemmaClient):
        def __init__(self):self.model='test-double'
        def generate(self,*args):return '{"interpretation":"test","supporting_claim_ids":["fabricated"],"weakening_claim_ids":[],"unresolved_questions":[],"recommended_classification":"consistent"}'
    monkeypatch.setattr(app.main,'GemmaClient',Bad)
    c=sample(client,'internship');f=c['findings'][0]
    r=client.post(f'{P}/investigations/{c["id"]}/findings/{f["id"]}/challenge',json={'provider':'gemma'})
    assert r.status_code==502 and 'invalid evidence references' in r.json()['detail']
    current=client.get(P+'/investigations/'+c['id']).json()
    assert current['findings']==c['findings']

def test_valid_challenge_retains_classification(client,monkeypatch):
    import app.main
    from promisegraph.advanced.schemas import ModelReview
    class Good:
        model='test-double'
        def challenge_finding(self,f,pair):
            return ModelReview(interpretation='A dated revision could explain the difference; dates are not supplied.',supporting_claim_ids=[pair[0]['id']],weakening_claim_ids=[pair[1]['id']],unresolved_questions=['Which version applies?'],recommended_classification='potential_conflict')
    monkeypatch.setattr(app.main,'GemmaClient',Good)
    c=sample(client,'internship');f=c['findings'][0]
    r=client.post(f'{P}/investigations/{c["id"]}/findings/{f["id"]}/challenge',json={'provider':'gemma'})
    assert r.status_code==200
    current=client.get(P+'/investigations/'+c['id']).json()['findings'][0]
    assert current['status']==f['status'] and current['explanation']==f['explanation']
    assert current['alternative']['recommended_classification']=='potential_conflict'

def test_cross_site_and_rebinding_protection(client):
    assert client.post(P+'/investigations',json={'title':'Forged'},headers={'Origin':'https://untrusted.example'}).status_code==403
    assert client.get(P+'/investigations',headers={'Sec-Fetch-Site':'cross-site'}).status_code==403
    assert client.get(P+'/health',headers={'Host':'untrusted.example'}).status_code==400
    assert client.post(P+'/investigations',json={'title':'Local'},headers={'Origin':'http://127.0.0.1:3000'}).status_code==201

def test_pdf_raster_navigation_bounds(client):
    import pymupdf
    doc=pymupdf.open();doc.new_page().insert_text((50,50),'Documented terms.')
    data=doc.tobytes();doc.close()
    cid=client.post(P+'/investigations',json={'title':'PDF'}).json()['id']
    source=client.post(f'{P}/investigations/{cid}/sources',files={'files':('terms.pdf',data,'application/pdf')}).json()[0]
    r=client.get(P+'/sources/'+source['id']+'/page/1')
    assert r.status_code==200 and r.content.startswith(b'\x89PNG')
    assert client.get(P+'/sources/'+source['id']+'/page/2').status_code==404

def test_cache_reuse_and_partial_extraction(client,monkeypatch):
    import app.main
    from promisegraph import Claim
    c=sample(client,'internship');original=[Claim.model_validate(x) for x in c['claims']]
    calls=[]
    class Cached:
        model='test-double'
        def verify_access(self):return 'READY'
        def extract_claims(self,source,images):
            calls.append(source['id'])
            return [claim for claim in original if claim.source_id==source['id']]
    monkeypatch.setattr(app.main,'GemmaClient',Cached);monkeypatch.setenv('GEMINI_API_KEY','test-key')
    path=f'{P}/investigations/{c["id"]}'
    client.post(path+'/analyze');client.post(path+'/analyze')
    assert len(calls)==3 and client.get(path).json()['status']=='completed'
    class Partial(Cached):
        model='test-double-v2'
        def extract_claims(self,source,images):
            if source['id']==c['sources'][1]['id']:raise ValueError('provider details must be hidden')
            return super().extract_claims(source,images)
    monkeypatch.setattr(app.main,'GemmaClient',Partial);client.post(path+'/analyze')
    current=client.get(path).json()
    assert current['status']=='partial' and current['claims']
    assert 'provider details' not in current['error_message']
    assert current['sources'][1]['extraction_status']=='failed'

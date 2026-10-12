import pytest
from promisegraph import Claim, investigate, graph, normalize

def claim(id='a',source='s1',**kw):
    value=kw.pop('value',0)
    return Claim(id=id,source_id=source,category='financial',subject=kw.pop('subject','registration'),predicate='required_fee',original_text=kw.pop('original_text',f'Declared value: {value}.'),normalized_summary='Registration fee',value=value,currency=kw.pop('currency','INR'),audience=kw.pop('audience','all applicants'),**kw)

def sources(a,b,**metadata):
    return {'s1':{'filename':'ad','extracted_text':a.original_text,**metadata},'s2':{'filename':'terms','extracted_text':b.original_text,**metadata}}

def test_normalization():
    c=normalize(claim(value='₹20,000',currency='₹',subject='application'))
    assert c.value==20000 and c.currency=='INR' and c.subject=='registration'

def test_fee_conflict_and_graph():
    a,b=claim(),claim('b','s2',value=499,original_text='Mandatory fee: ₹499.')
    cs,fs=investigate([a,b],sources(a,b))
    assert len(fs)==1 and fs[0].status=='contradiction' and fs[0].evidence_verified
    assert cs[0].text_start==0 and cs[0].location_quality=='exact'
    g=graph(cs,fs,sources(a,b))
    ids={n['id'] for n in g['nodes']}
    assert len(g['nodes'])==5 and all(e['source'] in ids and e['target'] in ids for e in g['edges'])

def test_optional_printed_certificate_not_registration_fee():
    a,b=claim(),claim('b','s2',value=200,subject='printed certificate',modality='optional')
    assert investigate([a,b],sources(a,b))[1]==[]

def test_different_stages_not_conflicting():
    a,b=claim(stage='application'),claim('b','s2',stage='enrollment',value=499)
    assert not investigate([a,b],sources(a,b))[1]

def test_different_audiences_not_conflicting():
    a,b=claim(audience='students'),claim('b','s2',audience='professionals',value=499)
    assert not investigate([a,b],sources(a,b))[1]

def test_currency_mismatch_not_numeric_conflict():
    a,b=claim(),claim('b','s2',value=499,currency='USD')
    assert not investigate([a,b],sources(a,b))[1]

def test_free_fee_without_currency_is_comparable():
    a,b=claim(currency=None),claim('b','s2',value=499)
    assert investigate([a,b],sources(a,b))[1][0].status=='contradiction'

def test_guarantee_condition_conflict():
    a,b=claim(modality='guaranteed',original_text='Guaranteed certificate.'),claim('b','s2',modality='conditional',conditions=['evaluation'],original_text='Certificate subject to evaluation.')
    fs=investigate([a,b],sources(a,b))[1]
    assert fs[0].status=='contradiction'

def test_possible_benefit_is_qualification():
    a,b=claim(modality='possible'),claim('b','s2',modality='conditional',conditions=['attendance'])
    fs=investigate([a,b],sources(a,b))[1]
    assert fs[0].status=='missing_disclosure'

def test_unverified_quote_downgraded():
    a,b=claim(),claim('b','s2',value=499)
    ss=sources(a,b);ss['s2']['extracted_text']='Nothing supporting that quote'
    fs=investigate([a,b],ss)[1]
    assert fs[0].status=='insufficient_evidence' and not fs[0].evidence_verified

def test_image_quote_is_not_text_verified():
    a,b=claim(),claim('b','s2',value=499)
    ss=sources(a,b);ss['s2']['extracted_text']=''
    cs,fs=investigate([a,b],ss)
    assert cs[1].location_quality=='approximate' and not fs[0].evidence_verified

def test_unknown_source_rejected():
    with pytest.raises(ValueError,match='Unknown source'):
        investigate([claim(source='invented')],{})

def test_duplicate_claim_ids_rejected():
    with pytest.raises(ValueError,match='Duplicate'):
        investigate([claim(),claim()],{'s1':{'filename':'ad','extracted_text':'Registration is free.'}})

def test_dated_version_is_changed_term():
    a,b=claim(value='2026-10-15'),claim('b','s2',value='2026-10-20')
    a.predicate=b.predicate='deadline'
    ss=sources(a,b,version_group='ad');ss['s1']['published_at']='2026-10-10';ss['s2']['published_at']='2026-10-12'
    assert investigate([a,b],ss)[1][0].status=='changed_term'

def test_upload_order_does_not_imply_drift():
    a,b=claim(),claim('b','s2',value=499)
    ss=sources(a,b,version_group='ad')
    assert investigate([a,b],ss)[1][0].status=='contradiction'

def test_conditions_differ_scope_review():
    a,b=claim(conditions=['early bird']),claim('b','s2',value=499,conditions=['late entry'])
    assert investigate([a,b],sources(a,b))[1][0].status=='potential_conflict'

def test_normalizes_explicit_quote_when_model_fields_are_generic():
    a=claim(value=None,original_text='Free registration.')
    a.category='compensation';a.subject='launchpad fellowship';a.predicate='offers'
    b=claim('b','s2',value=None,original_text='Mandatory ₹499 processing fee.')
    b.category='financial/registration';b.subject='processing fee';b.predicate='required'
    cs,fs=investigate([a,b],sources(a,b))
    assert fs[0].status=='contradiction'
    assert cs[0].value==0 and cs[1].value==499 and cs[1].currency=='INR'

def test_quote_normalization_preserves_optional_service_scope():
    a=claim(original_text='Registration is free.')
    b=claim('b','s2',value=None,original_text='Optional printed certificate costs ₹200.')
    b.subject='registration';b.category='financial/registration';b.predicate='required'
    cs,fs=investigate([a,b],sources(a,b))
    assert cs[1].modality=='optional' and cs[1].subject=='printed certificate' and not fs

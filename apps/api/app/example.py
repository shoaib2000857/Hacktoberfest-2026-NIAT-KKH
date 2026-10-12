"""Authored synthetic fixture, never represented as live model output."""
from uuid import uuid4
from promisegraph import Claim, investigate

DOCUMENTS = [
    ('Internship advertisement.txt', 'Launchpad Fellowship\nThree months. A real head start.\nFree registration. ₹20,000 fixed monthly stipend. Guaranteed certificate.\nOpen to all undergraduate students. Applications close October 15, 2026.'),
    ('Registration form.txt', 'Launchpad Fellowship — application terms\nMandatory ₹499 processing fee. Payment required to submit your application.\nOptional printed certificate costs ₹200. Applications close October 15, 2026.'),
    ('Offer letter.txt', 'Launchpad Fellowship — offer conditions\nStipend based on performance. Certificate subject to evaluation.\nThe internship lasts three months. The processing fee is non-refundable.')
]

def authored_claims(sources):
    specs = [
        (0,'financial','registration','required_fee',0,'INR',None,'required',[],'Free registration.','Registration is free'),
        (0,'compensation','internship','compensation',20000,'INR','month','guaranteed',[],'₹20,000 fixed monthly stipend.','Fixed stipend of ₹20,000 / month'),
        (0,'certification','participation','certification',None,None,None,'guaranteed',[],'Guaranteed certificate.','Certificate guaranteed'),
        (0,'deadlines','registration','deadline','2026-10-15',None,None,'asserted',[],'Applications close October 15, 2026.','Applications close October 15'),
        (1,'financial','registration','required_fee',499,'INR',None,'required',[],'Mandatory ₹499 processing fee.','Mandatory processing fee of ₹499'),
        (1,'financial','printed certificate','required_fee',200,'INR',None,'optional',[],'Optional printed certificate costs ₹200.','Optional printed certificate: ₹200'),
        (1,'deadlines','registration','deadline','2026-10-15',None,None,'asserted',[],'Applications close October 15, 2026.','Applications close October 15'),
        (2,'compensation','internship','compensation',None,'INR','month','conditional',['performance'],'Stipend based on performance.','Stipend depends on performance'),
        (2,'certification','participation','certification',None,None,None,'conditional',['evaluation'],'Certificate subject to evaluation.','Certificate depends on evaluation')
    ]
    return [Claim(id=str(uuid4()),source_id=sources[i]['id'],category=cat,subject=sub,predicate=pred,value=val,currency=cur,unit=unit,modality=mod,conditions=cond,audience='undergraduate students',stage='application' if pred=='required_fee' else 'participation',original_text=quote,normalized_summary=summary) for i,cat,sub,pred,val,cur,unit,mod,cond,quote,summary in specs]

"""Bridge richer deterministic modules into the retained PromiseTrap API schema."""
import hashlib
import re
from datetime import date
from decimal import Decimal, InvalidOperation

from .schemas import Claim, Finding
from .advanced.schemas import Claim as StructuredClaim, Source as StructuredSource, Scope, Stage
from .advanced.contradictions import compare as compare_structured
from .advanced.financial import calculate
from .advanced.conditions import dependencies, eligibility
from .advanced.verification import validate_anchor

STAGES = ['advertisement','registration','selection','offer','agreement','other']


def structured(c: Claim, sources: dict | None = None, hypothetical=False) -> StructuredClaim:
    amount = None
    try:
        if c.value is not None and c.predicate != 'deadline':
            amount = Decimal(str(c.value))
            if not amount.is_finite() or amount < 0:
                amount = None
    except InvalidOperation:
        pass
    source = (sources or {}).get(c.source_id,{})
    stage = source.get('document_stage','other')
    scope = c.scope or Scope(audience=None if c.audience=='unspecified' else c.audience, purpose=c.predicate, application_stage=None if c.stage=='unspecified' else c.stage)
    category = {'financial':'fee','certification':'certificate','deadlines':'deadline'}.get(c.category,c.category)
    if category not in {'fee','compensation','certificate','scholarship','deadline','eligibility','access','placement','other'}:
        category = 'other'
    role = c.financial_role or ('fee' if c.category=='financial' and c.predicate=='required_fee' else 'compensation' if c.category=='compensation' else None)
    value_kind = c.value_kind if c.value_kind!='unspecified' else 'maximum' if not hypothetical and re.search(r'\bup to\b',c.original_text,re.I) else 'exact' if amount is not None else 'unspecified'
    date_value = None
    if c.predicate=='deadline':
        try: date_value=date.fromisoformat(str(c.value))
        except ValueError: pass
    out = StructuredClaim(id=c.id,source_id=c.source_id,original_text=c.original_text,normalized_statement=c.normalized_summary,category=category,subject=c.subject,predicate=c.predicate,amount=amount,currency=c.currency if amount is not None else None,unit=c.unit or ('one_time' if role in {'fee','deposit','deduction'} else None),modality={'required':'mandatory','asserted':'unspecified'}.get(c.modality,c.modality),value_kind=value_kind,conditions=c.conditions,scope=scope,stage=Stage(stage if stage in STAGES else 'other'),date_value=date_value,financial_role=role,payment_timing=c.payment_timing or ('upfront' if re.search(r'\bupfront\b',c.original_text,re.I) else None),refund_terms=c.refund_terms,refundable=c.refundable,applicable_cost=c.applicable_cost,criteria=c.criteria,effective_date=source.get('effective_at') or source.get('published_at'),version_group=source.get('version_group'),review_status=c.review_status,evidence_quality={'unknown':'unavailable'}.get(c.location_quality,c.location_quality),uncertainty='high' if c.uncertainty_note else 'low')
    if sources is not None and not hypothetical:
        s = StructuredSource(id=c.source_id,filename=source.get('filename','Unknown'),mime=source.get('mime_type','text/plain'),sha256=source.get('sha256',''),text=source.get('extracted_text',''),pages=[p['text'] for p in source.get('pages',[])],page_count=len(source.get('pages',[])) or None,stage=out.stage,effective_date=source.get('effective_at') or source.get('published_at'),version_group=source.get('version_group'))
        out = validate_anchor(out,s)
    return out


def compare_extended(a: Claim,b: Claim,sources: dict,hypothetical=False) -> Finding:
    output=compare_structured(structured(a,sources,hypothetical),structured(b,sources,hypothetical),hypothetical=hypothetical)
    return Finding(id=hashlib.sha256('|'.join(sorted([a.id,b.id])).encode()).hexdigest()[:24],claim_a_id=a.id,claim_b_id=b.id,category=a.category,status=output.classification,title=output.title,explanation=output.explanation,evidence_verified=output.evidence_state=='verified_text',limitations=output.scope.reasons+output.scope.unknowns,scope=output.scope.model_dump(),pattern=output.rule)


def financial(claims: list[Claim],sources: dict) -> dict:
    return calculate([structured(c,sources) for c in claims if c.review_status!='rejected'])


def conditions(claims: list[Claim],sources: dict) -> list[dict]:
    return dependencies([structured(c,sources) for c in claims])


def personal(claims: list[Claim],sources: dict,profile: dict) -> list[dict]:
    return eligibility([structured(c,sources) for c in claims],profile)


def receipt(case: dict) -> dict:
    return {'investigation_id':case['id'],'sources':[{k:v for k,v in s.items() if k not in {'extracted_text','pages'}} for s in case['sources']], 'notice':'SHA-256 compares recorded bytes only. It does not prove origin, authorship or historical authenticity.'}


def journey(case: dict) -> dict:
    dated=bool(case['sources']) and all(s.get('published_at') for s in case['sources'])
    ordered=sorted(case['sources'],key=lambda s:(s['published_at'] if dated else str(STAGES.index(s.get('document_stage','other'))).zfill(2),s['filename']))
    return {'label':'Publication timeline' if dated else 'Document Sequence','note':'User-supplied publication dates.' if dated else 'Grouped by application stage; upload order does not establish chronology.','sources':ordered}

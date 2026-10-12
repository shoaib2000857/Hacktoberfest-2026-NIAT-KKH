"""Transparent, conservative comparisons. No model or network dependency."""
import hashlib
import re
from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from .schemas import Claim, Finding

ALIASES = {'application': 'registration', 'application fee': 'required_fee', 'registration fee': 'required_fee', 'fee': 'required_fee', 'stipend': 'compensation', 'salary': 'compensation', 'certificate': 'certification'}

def normalize(c: Claim) -> Claim:
    c = c.model_copy(deep=True)
    for key in ('subject', 'predicate', 'category', 'audience', 'stage'):
        value = getattr(c, key).strip().lower()
        setattr(c, key, ALIASES.get(value, value))
    if c.currency:
        c.currency = {'₹': 'INR', 'rs': 'INR', 'rupees': 'INR', '$': 'USD', '€': 'EUR'}.get(c.currency.lower(), c.currency.upper())
    if isinstance(c.value, str):
        raw = c.value.strip()
        if raw.lower() in ('free', 'nothing', 'no fee'):
            c.value = 0.0
        else:
            numeric = re.fullmatch(r'(?:₹|\$|€|INR\s*|USD\s*)?([\d,]+(?:\.\d+)?)', raw)
            if numeric:
                try:
                    c.value = float(Decimal(numeric.group(1).replace(',', '')))
                except InvalidOperation:
                    pass
    # Normalize explicit quoted terms, independently of an extractor's vocabulary.
    # This never creates evidence: the quote is subsequently verified against its source.
    quote = c.original_text.lower()
    money = re.search(r'(₹|\bINR\s*|\bRs\.?\s*|\$|\bUSD\s*|€)\s*([\d,]+(?:\.\d+)?)', c.original_text, re.IGNORECASE)
    amount = float(money.group(2).replace(',', '')) if money else None
    quoted_currency = {'₹':'INR','$':'USD','€':'EUR'}.get(money.group(1).strip(), 'USD' if money and money.group(1).strip().upper()=='USD' else 'INR') if money else None
    free_registration = re.search(r'\b(?:free registration|registration (?:is |costs )?(?:free|nothing)|no registration fees? |no registration fees?\b)', quote)
    fee = re.search(r'\b(?:application|registration|processing)\s+fee\b', quote)
    certificate = re.search(r'\bcertificates?\b', quote)
    stipend = re.search(r'\bstipend\b', quote)
    optional = bool(re.search(r'\boptional\b', quote))
    conditional = bool(re.search(r'\b(?:subject to|based on|depends on|provided that|conditional on)\b', quote))
    guarantee = bool(re.search(r'\b(?:guaranteed|fixed)\b', quote)) and not bool(re.search(r'\b(?:not|no) guaranteed\b', quote))
    if optional:
        c.modality = 'optional'
    if free_registration:
        c.category,c.subject,c.predicate,c.value = 'financial','registration','required_fee',0.0
        c.modality = 'required'
    elif fee and amount is not None:
        c.category,c.subject,c.predicate,c.value = 'financial','registration','required_fee',amount
        c.currency = quoted_currency
        if 'mandatory' in quote or 'required' in quote:
            c.modality = 'required'
    elif optional and certificate and amount is not None:
        c.category,c.subject,c.predicate,c.value = 'financial','printed certificate' if 'printed' in quote else 'certificate','required_fee',amount
        c.currency = quoted_currency
    elif stipend:
        c.category,c.subject,c.predicate = 'compensation','internship','compensation'
        if amount is not None:
            c.value,c.currency = amount,quoted_currency
        if 'monthly' in quote or '/month' in quote or 'per month' in quote:
            c.unit = 'month'
        if guarantee:
            c.modality = 'guaranteed'
        elif conditional:
            c.modality = 'conditional'
    elif certificate:
        c.category,c.subject,c.predicate = 'certification','participation','certification'
        if guarantee:
            c.modality = 'guaranteed'
        elif conditional:
            c.modality = 'conditional'
    if c.modality == 'conditional':
        for qualifier in ('performance','evaluation','attendance'):
            if qualifier in quote and qualifier not in c.conditions:
                c.conditions.append(qualifier)
    return c

def candidates(claims: list[Claim]):
    buckets = defaultdict(list)
    for claim in claims:
        buckets[(claim.category, claim.subject, claim.predicate)].append(claim)
    for bucket in buckets.values():
        for i, a in enumerate(bucket):
            for b in bucket[i+1:]:
                if a.source_id != b.source_id:
                    yield a, b

def verify(c: Claim, sources: dict) -> bool:
    source = sources.get(c.source_id)
    if not source or not c.original_text.strip():
        return False
    text = source.get('extracted_text', '')
    if not text:
        c.location_quality = 'approximate'
        return False
    start = text.find(c.original_text)
    if start < 0:
        c.location_quality = 'unknown'
        return False
    c.text_start, c.text_end = start, start + len(c.original_text)
    c.location_quality = 'exact'
    return True

def compare(a: Claim, b: Claim, sources: dict) -> Finding | None:
    if a.modality == 'optional' or b.modality == 'optional':
        return None
    scope_mismatch = any(getattr(a, k) != getattr(b, k) and 'unspecified' not in (getattr(a, k), getattr(b, k)) for k in ('audience', 'stage'))
    if scope_mismatch:
        return None
    conditions_differ = {x.lower().strip() for x in a.conditions} != {x.lower().strip() for x in b.conditions}
    numeric = isinstance(a.value, (int, float)) and isinstance(b.value, (int, float))
    currency_ok = a.currency == b.currency or (a.predicate == 'required_fee' and ((a.value == 0 and a.currency is None) or (b.value == 0 and b.currency is None)))
    units_ok = a.unit == b.unit
    value_diff = a.value is not None and b.value is not None and a.value != b.value
    guaranteed_conditional = {a.modality, b.modality} == {'guaranteed', 'conditional'}
    added_condition = b.conditions and not a.conditions or a.conditions and not b.conditions
    if not (value_diff or guaranteed_conditional or added_condition):
        return None
    if numeric and (not currency_ok or not units_ok):
        return None
    if value_diff and not numeric and a.predicate not in ('deadline', 'duration', 'eligibility') and not guaranteed_conditional:
        return None
    status = 'contradiction' if (numeric or guaranteed_conditional) else 'potential_conflict'
    limitations = ['Applies only if both sources describe the same offer and participants.']
    if conditions_differ and not guaranteed_conditional:
        status = 'potential_conflict'
        limitations.append('Conditions differ; equivalence requires human review.')
    if added_condition and not guaranteed_conditional and not value_diff:
        status = 'missing_disclosure'
    sa, sb = sources[a.source_id], sources[b.source_id]
    versioned = sa.get('version_group') and sa.get('version_group') == sb.get('version_group')
    dated = sa.get('published_at') and sb.get('published_at') and sa['published_at'] != sb['published_at']
    if versioned and dated:
        status = 'changed_term'
        limitations.append('Dated versions show a change, not simultaneous contradictory terms.')
    if a.effective_at != b.effective_at and a.effective_at and b.effective_at and status != 'changed_term':
        status = 'potential_conflict'
        limitations.append('Effective periods differ.')
    if a.predicate == 'deadline' and value_diff:
        try:
            date.fromisoformat(str(a.value)); date.fromisoformat(str(b.value))
        except ValueError:
            status = 'potential_conflict'
            limitations.append('Deadline lacks a comparable ISO date.')
    av, bv = verify(a, sources), verify(b, sources)
    verified = av and bv
    if not verified:
        status = 'insufficient_evidence'
        limitations.append('At least one excerpt cannot be verified against extracted text. Image quotations require visual review.')
    pair = '|'.join(sorted([a.id, b.id]))
    titles = {'contradiction': 'Conflicting '+a.category+' terms', 'potential_conflict': 'Check the scope of '+a.category, 'changed_term': 'A promise changed between versions', 'missing_disclosure': 'Additional conditions in the detailed terms', 'insufficient_evidence': 'Evidence needs verification'}
    pattern = 'terms_discrepancy'
    if a.predicate == 'required_fee' and numeric and min(a.value,b.value) == 0:
        pattern = 'hidden_mandatory_fee'
        if status == 'contradiction':
            titles[status] = 'Free registration meets a mandatory fee'
    elif guaranteed_conditional:
        pattern = 'changed_compensation' if a.category == 'compensation' else 'unsupported_guarantee'
        if status == 'contradiction':
            titles[status] = 'A fixed stipend becomes conditional' if a.category == 'compensation' else 'A guaranteed certificate gains conditions'
    elif a.predicate == 'deadline':
        pattern = 'moving_deadline'
    elif status == 'missing_disclosure':
        pattern = 'missing_material_conditions'
    return Finding(id=hashlib.sha256(pair.encode()).hexdigest()[:24], claim_a_id=a.id, claim_b_id=b.id, category=a.category, status=status,
        severity='high' if status == 'contradiction' else 'medium', title=titles[status], pattern=pattern,
        explanation=f'“{a.normalized_summary}” compared with “{b.normalized_summary}”. '+('An explicit guarantee is qualified by conditions.' if guaranteed_conditional else 'The comparable values or disclosed conditions differ.'),
        evidence_verified=verified, limitations=limitations)

def investigate(claims: list[Claim], sources: dict) -> tuple[list[Claim], list[Finding]]:
    ids = [c.id for c in claims]
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate claim identifiers')
    if any(c.source_id not in sources for c in claims):
        raise ValueError('Unknown source reference')
    normalized = [normalize(c) for c in claims]
    for c in normalized:
        verify(c, sources)
    findings = [f for a,b in candidates(normalized) if (f := compare(a,b,sources))]
    return normalized, findings

def graph(claims: list[Claim], findings: list[Finding], sources: dict) -> dict:
    nodes = [{'id': s, 'kind': 'source', 'label': v['filename']} for s,v in sources.items()]
    nodes += [{'id': c.id, 'kind': 'claim', 'label': c.normalized_summary, 'source_id': c.source_id} for c in claims]
    nodes += [{'id': f.id, 'kind': 'finding', 'label': f.title, 'status': f.status} for f in findings]
    edges = [{'id': 'contains-'+c.id, 'source': c.source_id, 'target': c.id, 'relationship': 'contains_claim'} for c in claims]
    for f in findings:
        relation = {'contradiction': 'contradicts', 'changed_term': 'updates', 'missing_disclosure': 'qualifies'}.get(f.status, 'references')
        edges += [{'id': f.id+'-'+cid, 'source': cid, 'target': f.id, 'relationship': relation} for cid in [f.claim_a_id, f.claim_b_id]]
    return {'nodes': nodes, 'edges': edges}

import re
from decimal import Decimal

from .normalization import monetary_values, normalize
from .schemas import Claim, Finding, Source


def validate_anchor(claim: Claim, source: Source) -> Claim:
    if claim.source_id != source.id:
        raise ValueError("Claim cites a different source")
    c = normalize(claim)
    c.stage = source.stage
    c.effective_date = source.effective_date
    c.version_group = source.version_group
    c.text_offset = None
    if c.page and (not source.page_count or c.page > source.page_count):
        c.page = None
    text = source.pages[c.page - 1] if c.page and source.pages else source.text
    if c.original_text and c.original_text in text:
        c.evidence_quality = "exact"
        c.text_offset = text.index(c.original_text)
    elif source.mime.startswith("image/") or source.mime == "application/pdf":
        c.evidence_quality = "approximate"
        c.uncertainty = "high"
    else:
        c.evidence_quality = "unavailable"
        c.uncertainty = "high"
    c.value_verified = c.amount is None
    if c.amount is not None:
        if c.currency:
            c.value_verified = (c.amount, c.currency) in monetary_values(c.original_text) or (c.amount == 0 and bool(re.search(r"\bfree\b", c.original_text, re.I)))
        elif c.unit == "percent":
            c.value_verified = any(Decimal(v) == c.amount for v in re.findall(r"([0-9]+(?:\.[0-9]+)?)\s*%", c.original_text))
        else:
            c.value_verified = False
        if not c.value_verified:
            c.uncertainty = "high"
    if c.applicable_cost is not None and (c.applicable_cost, c.currency) not in monetary_values(c.original_text):
        c.applicable_cost = None
        c.uncertainty = "high"
    quote=c.original_text.casefold()
    if c.payment_timing and not (c.payment_timing.casefold() in quote or (c.payment_timing=='upfront' and re.search(r'\b(?:upfront|before payment|before registration|payment required to submit)\b',quote))):
        c.payment_timing=None
        c.uncertainty='high'
    if c.refund_terms and c.refund_terms.casefold() not in quote:
        c.refund_terms=None
        c.uncertainty='high'
    if c.refundable is not None:
        if re.search(r'non[- ]refundable|not refundable',quote):
            c.refundable=False
        elif re.search(r'\brefundable\b',quote):
            c.refundable=True
        else:
            c.refundable=None
    return c


def validate_finding(finding: Finding, claims: dict[str, Claim]) -> Finding:
    if any(cid not in claims for cid in finding.claim_ids):
        raise ValueError("Finding cites a nonexistent claim")
    f = finding.model_copy(deep=True)
    qualities = {claims[cid].evidence_quality for cid in f.claim_ids}
    if "unavailable" in qualities:
        f.evidence_state = "unsupported"
        f.classification = "insufficient_evidence"
        f.explanation += " An excerpt could not be located in its source; this finding is unsupported."
    elif "approximate" in qualities:
        f.evidence_state = "visual_review_required"
        if f.classification == "contradiction":
            f.classification = "potential_conflict"
        f.explanation += " Image-derived wording requires visual verification against the original."
    else:
        f.evidence_state = "verified_text"
    return f


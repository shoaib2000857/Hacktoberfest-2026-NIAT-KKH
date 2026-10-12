from typing import Literal
from pydantic import BaseModel, Field
from .advanced.schemas import Scope, Criterion, ModelReview

class Claim(BaseModel):
    id: str
    source_id: str
    category: str
    subject: str
    predicate: str
    value: str | float | None = None
    currency: str | None = None
    unit: str | None = None
    modality: Literal['guaranteed', 'conditional', 'possible', 'required', 'prohibited', 'optional', 'asserted'] = 'asserted'
    conditions: list[str] = Field(default_factory=list)
    audience: str = 'unspecified'
    stage: str = 'unspecified'
    effective_at: str | None = None
    original_text: str
    normalized_summary: str
    page_number: int | None = None
    text_start: int | None = None
    text_end: int | None = None
    location_quality: Literal['exact', 'approximate', 'unknown'] = 'unknown'
    uncertainty_note: str | None = None
    scope: Scope | None = None
    value_kind: Literal['exact','maximum','minimum','unspecified'] = 'unspecified'
    financial_role: Literal['fee','deposit','deduction','compensation','coverage'] | None = None
    payment_timing: str | None = None
    refund_terms: str | None = None
    refundable: bool | None = None
    applicable_cost: float | None = Field(default=None,ge=0,allow_inf_nan=False)
    criteria: list[Criterion] = Field(default_factory=list,max_length=20)
    review_status: Literal['unreviewed','confirmed','rejected'] = 'unreviewed'

class Extraction(BaseModel):
    claims: list[Claim] = Field(max_length=80)

class Finding(BaseModel):
    id: str
    claim_a_id: str
    claim_b_id: str
    category: str
    status: Literal['contradiction', 'potential_conflict', 'changed_term', 'material_qualification', 'missing_disclosure', 'consistent', 'insufficient_evidence']
    severity: Literal['informational', 'low', 'medium', 'high'] = 'medium'
    title: str
    pattern: str = 'terms_discrepancy'
    explanation: str
    validation_method: Literal['rule', 'semantic', 'hybrid'] = 'rule'
    evidence_verified: bool = False
    limitations: list[str] = Field(default_factory=list)
    review_status: Literal['unreviewed', 'accepted', 'rejected', 'unresolved'] = 'unreviewed'
    review_notes: str = ''
    scope: dict | None = None
    alternative: ModelReview | None = None
    semantic_review: dict | None = None

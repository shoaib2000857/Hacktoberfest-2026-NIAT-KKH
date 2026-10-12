from typing import Literal
from pydantic import BaseModel, Field

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

class Extraction(BaseModel):
    claims: list[Claim] = Field(max_length=80)

class Finding(BaseModel):
    id: str
    claim_a_id: str
    claim_b_id: str
    category: str
    status: Literal['contradiction', 'potential_conflict', 'changed_term', 'missing_disclosure', 'consistent', 'insufficient_evidence']
    severity: Literal['informational', 'low', 'medium', 'high'] = 'medium'
    title: str
    pattern: str = 'terms_discrepancy'
    explanation: str
    validation_method: Literal['rule', 'semantic', 'hybrid'] = 'rule'
    evidence_verified: bool = False
    limitations: list[str] = Field(default_factory=list)
    review_status: Literal['unreviewed', 'accepted', 'rejected', 'unresolved'] = 'unreviewed'
    review_notes: str = ''

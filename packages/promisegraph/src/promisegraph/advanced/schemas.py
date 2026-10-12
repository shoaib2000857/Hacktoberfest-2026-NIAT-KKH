from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


def uid() -> str:
    return uuid4().hex


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class Stage(str, Enum):
    advertisement = "advertisement"
    registration = "registration"
    selection = "selection"
    offer = "offer"
    agreement = "agreement"
    other = "other"


class Scope(Record):
    program: str | None = None
    audience: str | None = None
    purpose: str | None = None
    period: str | None = None
    application_stage: str | None = None
    contractual_condition: str | None = None
    qualifying_event: str | None = None


class Criterion(Record):
    field: Literal["year_of_study", "degree", "location", "academic_score"]
    operator: Literal["equals", "at_least", "one_of"]
    value: str


class Claim(Record):
    id: str = Field(default_factory=uid)
    source_id: str
    original_text: str = Field(max_length=4000)
    normalized_statement: str = Field(max_length=4000)
    category: Literal["fee", "compensation", "certificate", "scholarship", "deadline", "eligibility", "access", "placement", "other"]
    subject: str
    predicate: str
    amount: Decimal | None = Field(default=None, ge=0, allow_inf_nan=False)
    currency: str | None = None
    unit: str | None = None
    modality: Literal["guaranteed", "conditional", "optional", "mandatory", "prohibited", "possible", "unspecified"] = "unspecified"
    value_kind: Literal["exact", "maximum", "minimum", "unspecified"] = "unspecified"
    conditions: list[str] = Field(default_factory=list, max_length=30)
    scope: Scope = Field(default_factory=Scope)
    stage: Stage = Stage.other
    effective_date: date | None = None
    version_group: str | None = None
    date_value: date | None = None
    page: int | None = Field(default=None, ge=1)
    text_offset: int | None = Field(default=None, ge=0)
    evidence_quality: Literal["exact", "approximate", "unavailable"] = "unavailable"
    value_verified: bool = False
    uncertainty: Literal["low", "medium", "high"] = "medium"
    financial_role: Literal["fee", "deposit", "deduction", "compensation", "coverage"] | None = None
    applicable_cost: Decimal | None = Field(default=None, ge=0, allow_inf_nan=False)
    payment_timing: str | None = None
    refundable: bool | None = None
    refund_terms: str | None = None
    criteria: list[Criterion] = Field(default_factory=list, max_length=20)
    review_status: Literal["unreviewed", "confirmed", "rejected"] = "unreviewed"

    @model_validator(mode="after")
    def money_currency(self):
        if self.currency and not self.amount and self.amount != 0:
            raise ValueError("Currency requires a monetary value")
        return self


class Source(Record):
    id: str = Field(default_factory=uid)
    filename: str
    mime: str
    sha256: str
    collected_at: str = Field(default_factory=now)
    stage: Stage = Stage.other
    publication_date: date | None = None
    effective_date: date | None = None
    version_group: str | None = None
    source_url: str | None = None
    text: str = ""
    pages: list[str] = Field(default_factory=list)
    page_count: int | None = None
    status: Literal["uploaded", "extracting", "complete", "failed"] = "uploaded"
    error: str | None = None
    model: str | None = None
    prompt_version: str | None = None
    analyzed_at: str | None = None
    provenance: Literal["uploaded", "fictional_fixture"] = "uploaded"


class ScopeResult(Record):
    comparable: bool
    certain: bool
    reasons: list[str]
    unknowns: list[str]


Classification = Literal["contradiction", "potential_conflict", "changed_term", "material_qualification", "missing_disclosure", "consistent", "insufficient_evidence"]


class ModelReview(Record):
    interpretation: str = Field(max_length=5000)
    supporting_claim_ids: list[str]
    weakening_claim_ids: list[str]
    unresolved_questions: list[str]
    recommended_classification: Classification


class Finding(Record):
    id: str = Field(default_factory=uid)
    title: str
    category: str
    classification: Classification
    claim_ids: list[str] = Field(min_length=1, max_length=2)
    explanation: str
    scope: ScopeResult
    evidence_state: Literal["verified_text", "visual_review_required", "unsupported", "hypothetical"]
    rule: str
    review_status: Literal["unreviewed", "accepted", "dismissed", "needs_clarification"] = "unreviewed"
    alternative: ModelReview | None = None
    semantic_review: ModelReview | None = None


class Investigation(Record):
    id: str = Field(default_factory=uid)
    title: str = Field(min_length=1, max_length=150)
    created_at: str = Field(default_factory=now)
    sources: list[Source] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    status: Literal["draft", "queued", "extracting", "comparing", "complete", "partial", "failed"] = "draft"
    progress_message: str = "Add evidence to begin."
    mode: Literal["live", "fictional_fixture"] = "live"
    history: list[dict] = Field(default_factory=list)
    clarification: str = ""


class Extraction(Record):
    claims: list[Claim] = Field(max_length=80)


class Clarification(Record):
    questions: list[str] = Field(max_length=30)
    claim_ids: list[str]


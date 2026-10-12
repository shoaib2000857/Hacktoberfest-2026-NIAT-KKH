"""Explicit fictional structured fixtures. Never presented as Gemma output."""
import json
from datetime import date
from pathlib import Path

from promisegraph.advanced.matching import analyze
from promisegraph.advanced.provenance import fingerprint
from promisegraph.advanced.schemas import Claim, Criterion, Investigation, Scope, Source, Stage, now
from promisegraph.advanced.verification import validate_anchor


SAMPLES = Path(__file__).resolve().parents[3] / "examples" / "advanced"


def scope(purpose="registration", stage="registration"):
    return Scope(program="fictional nova 2026", audience="all registered applicants", purpose=purpose, period="2026 intake", application_stage=stage, contractual_condition="nova 2026 terms", qualifying_event="registration")


def spec(text, category, subject, predicate, **kwargs):
    return {"original_text": text, "normalized_statement": text, "category": category, "subject": subject, "predicate": predicate, "uncertainty": "low", **kwargs}


DATASETS = {
    "internship": [
        {"name": "internship-advertisement", "stage": "advertisement", "title": "Nova Internship • Advertisement", "claims": [
            spec("Registration is completely free.", "fee", "registration", "cost", amount="0", currency="INR", unit="one_time", modality="guaranteed", value_kind="exact", financial_role="fee"),
            spec("Guaranteed stipend ₹20,000 per month.", "compensation", "stipend", "payment", amount="20000", currency="INR", unit="month", modality="guaranteed", value_kind="exact", financial_role="compensation", scope=scope("stipend", "participation").model_dump()),
            spec("Certificate guaranteed to all registered applicants.", "certificate", "certificate", "issuance", modality="guaranteed", scope=scope("certificate", "completion").model_dump())]},
        {"name": "internship-registration", "stage": "registration", "title": "Nova Internship • Registration", "claims": [
            spec("A mandatory processing fee of ₹499 is due upfront for registration.", "fee", "registration", "cost", amount="499", currency="INR", unit="one_time", modality="mandatory", value_kind="exact", financial_role="fee", payment_timing="upfront")]},
        {"name": "internship-offer", "stage": "offer", "title": "Nova Internship • Offer terms", "claims": [
            spec("Stipend up to ₹20,000 per month, subject to performance evaluation.", "compensation", "stipend", "payment", amount="20000", currency="INR", unit="month", modality="conditional", value_kind="maximum", conditions=["Performance evaluation"], financial_role="compensation", scope=scope("stipend", "participation").model_dump()),
            spec("Certificates issued only after successful evaluation and 80% attendance.", "certificate", "certificate", "issuance", modality="conditional", conditions=["Successful evaluation", "80% attendance"], scope=scope("certificate", "completion").model_dump())]}],
    "scholarship": [
        {"name": "scholarship-advertisement", "stage": "advertisement", "title": "Nova Scholarship • Advertisement", "claims": [spec("Guaranteed 100% tuition coverage for all registered applicants.", "scholarship", "tuition", "coverage", amount="100", unit="percent", modality="guaranteed", value_kind="exact", scope=scope("tuition", "award").model_dump())]},
        {"name": "scholarship-terms", "stage": "agreement", "title": "Nova Scholarship • Terms", "claims": [
            spec("Tuition coverage is capped at ₹100,000; applicable course tuition is ₹150,000.", "scholarship", "tuition", "coverage", amount="100000", currency="INR", unit="one_time", applicable_cost="150000", modality="conditional", value_kind="maximum", conditions=["Funding cap ₹100,000"], financial_role="coverage", scope=scope("tuition", "award").model_dump()),
            spec("Applicants must be in year 4 of their degree.", "eligibility", "applicant", "year", modality="mandatory", criteria=[Criterion(field="year_of_study", operator="equals", value="4").model_dump()], conditions=["Year 4 of degree"])]}],
    "optional": [
        {"name": "optional-advertisement", "stage": "advertisement", "title": "Nova Workshop • Advertisement", "claims": [spec("Registration is free.", "fee", "registration", "cost", amount="0", currency="INR", unit="one_time", modality="guaranteed", value_kind="exact", financial_role="fee")]},
        {"name": "optional-terms", "stage": "agreement", "title": "Nova Workshop • Optional extras", "claims": [spec("An optional printed certificate costs ₹200.", "fee", "printed certificate", "cost", amount="200", currency="INR", unit="one_time", modality="optional", value_kind="exact", financial_role="fee", scope=scope("printed certificate", "completion").model_dump())]}],
    "deadline": [
        {"name": "deadline-v1", "stage": "advertisement", "date": "2026-10-01", "title": "Nova announcement • Version 1", "claims": [spec("Application deadline is October 15, 2026.", "deadline", "application", "deadline", date_value="2026-10-15", modality="mandatory")]},
        {"name": "deadline-v2", "stage": "advertisement", "date": "2026-10-05", "title": "Nova announcement • Version 2", "claims": [spec("Application deadline is October 20, 2026.", "deadline", "application", "deadline", date_value="2026-10-20", modality="mandatory")]}],
}


def document(item):
    return "FICTIONAL SAMPLE — NOT A REAL ORGANIZATION OR OFFER\n\n" + item["title"] + "\n\n" + "\n\n".join(c["original_text"] for c in item["claims"]) + "\n\nScope: Nova 2026 program, all registered applicants, 2026 intake, Nova 2026 terms.\nUnless explicitly qualified above, all statements refer to the same qualifying event: registration.\nNo publication or effective date is claimed unless supplied in the sample metadata.\n"


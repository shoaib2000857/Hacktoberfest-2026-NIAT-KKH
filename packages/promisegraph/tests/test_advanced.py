from datetime import date
from decimal import Decimal

import pytest

from promisegraph.advanced.schemas import Scope

def scope():
    return Scope(program="nova",audience="all",purpose="registration",period="2026",application_stage="registration",contractual_condition="terms",qualifying_event="registration")

from promisegraph.advanced.contradictions import compare
from promisegraph.advanced.financial import calculate
from promisegraph.advanced.normalization import normalize, parse_money
from promisegraph.advanced.provenance import fingerprint
from promisegraph.advanced.schemas import Claim, Finding, Scope, Source
from promisegraph.advanced.simulation import simulate
from promisegraph.advanced.verification import validate_anchor, validate_finding


def claim(source="a", text="Registration is free.", **kwargs):
    defaults = dict(source_id=source, original_text=text, normalized_statement=text, category="fee", subject="registration", predicate="cost", amount=0, currency="INR", unit="one_time", modality="guaranteed", value_kind="exact", scope=scope(), uncertainty="low", evidence_quality="exact", value_verified=True, financial_role="fee")
    return Claim(**{**defaults, **kwargs})


def fee():
    return claim("b", "Mandatory registration fee ₹499.", amount=499, modality="mandatory", payment_timing="upfront")


def test_real_fee_contradiction():
    assert compare(claim(), fee()).classification == "contradiction"


def test_optional_certificate_is_not_registration_contradiction():
    optional = fee().model_copy(deep=True)
    optional.subject = "printed certificate"
    optional.modality = "optional"
    optional.scope.purpose = "printed certificate"
    assert compare(claim(), optional).classification == "insufficient_evidence"
    assert "Different" in " ".join(compare(claim(), optional).scope.reasons)


def test_optional_same_purpose_does_not_establish_mandatory_fee():
    b = fee()
    b.modality = "optional"
    assert compare(claim(), b).classification != "contradiction"


def test_conditional_certificate_is_qualification():
    a = claim(category="certificate", subject="certificate", predicate="issuance", amount=None, currency=None, financial_role=None, modality="possible")
    b = claim("b", category="certificate", subject="certificate", predicate="issuance", amount=None, currency=None, financial_role=None, modality="conditional", conditions=["80% attendance"])
    assert compare(a, b).classification == "material_qualification"


def test_guarantee_to_conditional_change():
    a = claim(category="compensation", subject="stipend", predicate="payment", amount=20000, unit="month")
    b = claim("b", category="compensation", subject="stipend", predicate="payment", amount=20000, unit="month", modality="conditional", value_kind="maximum", conditions=["Evaluation"])
    assert compare(a, b).classification == "contradiction"


def test_deadline_version_change():
    a = claim(category="deadline", amount=None, currency=None, date_value=date(2026, 10, 15), effective_date=date(2026, 10, 1), version_group="v")
    b = claim("b", category="deadline", amount=None, currency=None, date_value=date(2026, 10, 20), effective_date=date(2026, 10, 5), version_group="v")
    assert compare(a, b).classification == "changed_term"


def test_unknown_audience_prevents_definitive_contradiction():
    a = claim(scope=Scope(program="nova"))
    b = fee()
    b.scope = Scope(program="nova")
    assert compare(a, b).classification == "potential_conflict"


def test_simulation_does_not_mutate_evidence():
    a, b = claim(), fee()
    original = b.model_dump_json()
    assert simulate(a, b).classification == "contradiction"
    hypothetical = b.model_copy(deep=True)
    hypothetical.modality = "optional"
    hypothetical.subject = "printed certificate"
    hypothetical.scope.purpose = "printed certificate"
    assert simulate(a, hypothetical).classification == "insufficient_evidence"
    assert b.model_dump_json() == original


def test_integrity_byte_different():
    assert fingerprint(b"a") != fingerprint(b"b")
    assert fingerprint(b"a") == fingerprint(b"a")


def test_invalid_source_citation_rejected():
    source = Source(id="x", filename="a.txt", mime="text/plain", sha256=fingerprint(b"x"), text="x")
    with pytest.raises(ValueError, match="different source"):
        validate_anchor(claim(), source)
    f = compare(claim(), fee())
    with pytest.raises(ValueError, match="nonexistent claim"):
        validate_finding(f, {})


def test_unlocated_text_downgraded():
    a = claim()
    a.evidence_quality = "unavailable"
    assert compare(a, fee()).classification == "insufficient_evidence"


def test_visual_text_does_not_get_exact_anchor():
    source = Source(id="a", filename="a.png", mime="image/png", sha256="x")
    c = validate_anchor(claim(page=99, text_offset=17), source)
    assert c.page is None and c.text_offset is None and c.evidence_quality == "approximate"
    assert compare(c, fee()).classification == "potential_conflict"


def test_financial_conditional_not_guaranteed():
    c = claim(category="compensation", subject="stipend", predicate="payment", amount=20000, modality="conditional", value_kind="maximum", unit="month", financial_role="compensation", conditions=["Evaluation"])
    result = calculate([fee(), c])
    assert result["currencies"]["INR"]["mandatory_upfront_cost"] == "499"
    assert result["currencies"]["INR"]["guaranteed_compensation"] == []
    assert result["currencies"]["INR"]["conditional_compensation"][0]["amount"] == "20000"


def test_missing_refund_unknown():
    assert calculate([fee()])["refund_policy"].startswith("Unknown")


def test_duplicate_obligation_not_added_twice():
    assert calculate([fee(), fee()])["currencies"]["INR"]["mandatory_upfront_cost"] == "499"


def test_currency_normalization_and_decimal():
    assert parse_money("cost ₹20,000.50") == (Decimal("20000.50"), "INR")
    assert normalize(claim(currency="₹", unit="one-time")).unit == "one_time"


def test_identically_qualified_guarantees_are_not_conflicts():
    a = claim(conditions=["80% attendance"])
    b = claim("b", conditions=["80% attendance"])
    assert compare(a, b).classification == "consistent"


def test_different_payment_conditions_not_definite_amount_conflict():
    a = claim(conditions=["With housing"], modality="mandatory", amount=100)
    b = fee()
    b.conditions = ["Without housing"]
    assert compare(a, b).classification == "material_qualification"


def test_hallucinated_financial_number_not_calculated():
    b = fee()
    b.amount = Decimal(999)
    s = Source(id="b", filename="fee.txt", mime="text/plain", sha256="x", text=b.original_text)
    b = validate_anchor(b,s)
    assert b.value_verified is False
    assert calculate([b])["currencies"] == {}

@pytest.mark.parametrize('cost,expected',[(None,'material_qualification'),(50000,'consistent'),(150000,'contradiction')])
def test_scholarship_cap_requires_applicable_tuition(cost,expected):
    a=claim(category='scholarship',subject='tuition',predicate='coverage',amount=100,currency=None,unit='percent',financial_role=None)
    b=claim('b',category='scholarship',subject='tuition',predicate='coverage',amount=100000,unit='one_time',modality='conditional',value_kind='maximum',applicable_cost=cost,financial_role='coverage')
    assert compare(a,b).classification==expected

def test_different_currencies_and_rates_not_combined():
    euro=fee().model_copy(update={'id':'euro','currency':'EUR','amount':Decimal('30')})
    monthly=fee().model_copy(update={'id':'monthly','unit':'month','amount':Decimal('100')})
    result=calculate([fee(),euro,monthly])
    assert result['currencies']['INR']['mandatory_upfront_cost']=='499'
    assert result['currencies']['EUR']['mandatory_upfront_cost']=='30'
    assert any('rate' in note for note in result['uncertainties'])

def test_unstated_refund_and_payment_schedule_not_assumed():
    c=fee();c.refund_terms='Fully refundable';c.refundable=True
    source=Source(id='b',filename='fee.txt',mime='text/plain',sha256='x',text=c.original_text)
    checked=validate_anchor(c,source)
    assert checked.payment_timing is None and checked.refund_terms is None and checked.refundable is None
    assert calculate([checked])['refund_policy'].startswith('Unknown')
    assert calculate([checked])['currencies']['INR']['mandatory_upfront_cost']=='0'


def test_supported_refund_and_timing_retained():
    c=claim('b','Mandatory registration fee ₹499 is due upfront and is non-refundable.',amount=499,modality='mandatory',payment_timing='upfront',refund_terms='non-refundable',refundable=True)
    source=Source(id='b',filename='fee.txt',mime='text/plain',sha256='x',text=c.original_text)
    checked=validate_anchor(c,source)
    assert checked.payment_timing=='upfront' and checked.refundable is False
    assert calculate([checked])['currencies']['INR']['mandatory_upfront_cost']=='499'

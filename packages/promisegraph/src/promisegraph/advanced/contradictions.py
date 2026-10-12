from .normalization import normalize
from .schemas import Claim, Finding
from .scopeguard import compare_scope
from .verification import validate_finding


def compare(left: Claim, right: Claim, hypothetical: bool = False) -> Finding:
    a, b = normalize(left), normalize(right)
    scope = compare_scope(a, b)
    classification, rule = "consistent", "same_attributes"
    explanation = "The compared attributes are consistent; this does not verify claims beyond the supplied evidence."
    if not scope.comparable:
        classification, rule = "insufficient_evidence", "scope_mismatch"
        explanation = "No contradiction established. " + " ".join(scope.reasons)
    else:
        versioned = bool(a.version_group and a.version_group == b.version_group and a.effective_date and b.effective_date and a.effective_date != b.effective_date)
        changed_value = (a.amount != b.amount) or (a.date_value != b.date_value) or (a.modality != b.modality) or (a.conditions != b.conditions)
        if versioned and changed_value:
            classification, rule = "changed_term", "dated_version_update"
            explanation = "Dated versions in the same declared version group have different terms. This is a documented change, not evidence of simultaneous contradiction."
        elif a.category == "scholarship" and {a.unit, b.unit} == {"percent", "one_time"}:
            percent, cap = (a, b) if a.unit == "percent" else (b, a)
            if cap.applicable_cost is None or percent.amount is None or cap.amount is None or cap.value_kind != "maximum":
                classification, rule = "material_qualification", "coverage_cap_unknown_tuition"
                explanation = "The advertised percentage has a funding cap. Applicable tuition is not established, so the cap does not establish a contradiction."
            elif percent.amount * cap.applicable_cost / 100 > cap.amount:
                classification, rule = "contradiction", "coverage_cap_below_documented_cost"
                explanation = f"At the explicitly documented tuition of {cap.applicable_cost} {cap.currency}, {percent.amount}% coverage exceeds the {cap.amount} cap."
            else:
                classification, rule = "consistent", "coverage_cap_sufficient"
                explanation = "The cap covers the advertised percentage of the explicitly documented applicable tuition."
        elif a.amount is not None and b.amount is not None and a.currency == b.currency and a.unit == b.unit and a.value_kind == b.value_kind == "exact" and a.amount != b.amount and a.conditions == b.conditions and a.modality not in {"optional", "conditional", "possible", "unspecified"} and b.modality not in {"optional", "conditional", "possible", "unspecified"}:
            classification, rule = "contradiction", "equivalent_fixed_value"
            explanation = f"Equivalent fixed commitments disagree: {a.amount} versus {b.amount} {a.currency or a.unit or ''}."
        elif ((a.modality == "guaranteed" and not a.conditions and (b.modality in {"conditional", "prohibited"} or b.conditions or b.value_kind == "maximum")) or (b.modality == "guaranteed" and not b.conditions and (a.modality in {"conditional", "prohibited"} or a.conditions or a.value_kind == "maximum"))):
            classification, rule = "contradiction", "guarantee_qualified"
            explanation = "An unconditional guarantee is qualified or restricted by the other comparable statement. Confirm whether both terms apply together."
        elif a.conditions != b.conditions or a.modality != b.modality or a.value_kind != b.value_kind:
            classification, rule = "material_qualification", "documented_condition"
            explanation = "A documented qualifier changes how the benefit is obtained. A condition alone does not establish deception."
        elif a.date_value and b.date_value and a.date_value != b.date_value:
            classification, rule = "contradiction", "equivalent_deadline"
            explanation = "Comparable statements give different deadlines without an established version sequence."
        elif a.amount != b.amount or a.normalized_statement != b.normalized_statement:
            classification, rule = "insufficient_evidence", "semantic_ambiguity"
            explanation = "No decisive deterministic rule applies. Semantic equivalence or missing numerical qualifiers requires review."
        if classification == "contradiction" and (not scope.certain or a.uncertainty == "high" or b.uncertainty == "high"):
            classification = "potential_conflict"
            explanation += " Scope or extraction uncertainty prevents a definitive contradiction."
    f = Finding(title=f"{a.category.replace('_', ' ').title()}: {rule.replace('_', ' ')}", category=a.category, classification=classification, claim_ids=[a.id, b.id], explanation=explanation, scope=scope, evidence_state="hypothetical" if hypothetical else "verified_text", rule=rule)
    return f if hypothetical else validate_finding(f, {a.id: a, b.id: b})


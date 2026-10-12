from decimal import Decimal, InvalidOperation

from .schemas import Claim


def dependencies(claims: list[Claim]) -> list[dict]:
    active = [c for c in claims if c.review_status != "rejected"]
    from .scopeguard import compare_scope
    groups=[]
    for c in active:
        if not c.conditions:
            continue
        advertised=[a for a in active if a.stage=='advertisement' and compare_scope(a,c).comparable]
        groups.append({'benefit':c.normalized_statement,'claim_id':c.id,'evidence_quality':c.evidence_quality,'advertisement_comparison':'available' if advertised else 'unknown','conditions':[{'text':text,'claim_id':c.id,'required':c.modality!='optional','not_in_advertisement':bool(advertised) and not any(text.casefold() in ' '.join(a.conditions).casefold() for a in advertised)} for text in c.conditions],'ordering':'Requirements feed into the benefit; their sequence is not established.'})
    return groups


def eligibility(claims: list[Claim], profile: dict) -> list[dict]:
    results = []
    for c in claims:
        if c.review_status == "rejected":
            continue
        for rule in c.criteria:
            actual = profile.get(rule.field)
            status = "unknown"
            if actual is not None and str(actual).strip():
                if rule.operator == "equals":
                    status = "satisfied" if str(actual).strip().casefold() == rule.value.strip().casefold() else "not_satisfied"
                elif rule.operator == "one_of":
                    status = "satisfied" if str(actual).strip().casefold() in [v.strip().casefold() for v in rule.value.split("|")] else "not_satisfied"
                else:
                    try:
                        status = "satisfied" if Decimal(str(actual)) >= Decimal(rule.value) else "not_satisfied"
                    except InvalidOperation:
                        pass
            if c.evidence_quality == "unavailable":
                status = "unknown"
            results.append({"criterion": rule.model_dump(), "status": status, "claim_id": c.id, "evidence_quality": c.evidence_quality})
    return results


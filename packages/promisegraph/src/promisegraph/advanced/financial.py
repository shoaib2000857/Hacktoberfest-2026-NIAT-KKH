from collections import defaultdict
from decimal import Decimal

from .normalization import normalize
from .schemas import Claim


def calculate(claims: list[Claim]) -> dict:
    rows, uncertainties, groups = [], [], defaultdict(list)
    active = [normalize(c) for c in claims if c.review_status != "rejected"]
    for c in active:
        if c.financial_role:
            rows.append({"claim_id": c.id, "source_id": c.source_id, "role": c.financial_role, "amount": str(c.amount) if c.amount is not None else None, "currency": c.currency, "unit": c.unit, "modality": c.modality, "value_kind": c.value_kind, "conditions": c.conditions, "payment_timing": c.payment_timing, "refund_terms": c.refund_terms, "evidence_quality": c.evidence_quality})
        if c.amount is not None and c.currency and c.financial_role:
            groups[(c.scope.program, c.scope.audience, c.subject, c.predicate, c.scope.purpose, c.scope.period, c.scope.application_stage, c.scope.contractual_condition, c.scope.qualifying_event, c.financial_role, c.currency, c.unit)].append(c)
    totals = defaultdict(lambda: {"mandatory_upfront_cost": Decimal(0), "optional_fees": Decimal(0), "deposits": Decimal(0), "fixed_deductions": Decimal(0), "guaranteed_compensation": [], "conditional_compensation": [], "potential_compensation": [], "claim_ids": []})
    for key, items in groups.items():
        currency, unit = key[-2:]
        usable = [c for c in items if c.evidence_quality != "unavailable" and c.value_verified]
        if not usable:
            uncertainties.append("An unlocated financial excerpt or unverified extracted amount was excluded from calculations.")
            continue
        if any(c.evidence_quality != "exact" or c.review_status != "confirmed" for c in usable):
            uncertainties.append("Some extracted values require source review; totals are provisional until confirmed.")
        amounts = {c.amount for c in usable}
        roles = {c.modality for c in usable}
        total = totals[currency]
        total["claim_ids"].extend(c.id for c in usable)
        c = usable[-1]
        if c.financial_role in {"fee", "deposit", "deduction"}:
            positive = [v for v in usable if v.amount > 0]
            if positive and any(v.amount == 0 for v in usable):
                uncertainties.append(f"A free-cost promise conflicts with a documented charge for {c.subject}; the positive charge is shown provisionally.")
                usable = positive
                amounts, roles = {v.amount for v in usable}, {v.modality for v in usable}
                c = usable[-1]
            if len(amounts) != 1 or ("optional" in roles and "mandatory" in roles):
                uncertainties.append(f"Conflicting cost values or obligations for {c.subject}; excluded from subtotal.")
                continue
            if c.unit != "one_time":
                uncertainties.append(f"The {c.unit or 'unknown-unit'} charge for {c.subject} is shown as a rate, not added to one-time cost totals.")
                continue
            if c.financial_role == "fee" and c.modality == "mandatory" and c.payment_timing == "upfront" and c.value_kind == "exact":
                total["mandatory_upfront_cost"] += c.amount
            elif c.financial_role == "fee" and c.modality == "optional" and c.value_kind == "exact":
                total["optional_fees"] += c.amount
            elif c.financial_role == "deposit" and c.modality == "mandatory" and c.value_kind == "exact":
                total["deposits"] += c.amount
            elif c.financial_role == "deduction" and c.modality == "mandatory" and c.value_kind == "exact":
                total["fixed_deductions"] += c.amount
            else:
                uncertainties.append(f"Payment timing, obligation or fixed amount for {c.subject} is not established.")
        elif c.financial_role == "compensation":
            group_guarantee_added = False
            for v in usable:
                row = {"amount": str(v.amount), "unit": unit, "claim_id": v.id, "conditions": v.conditions}
                if v.modality == "guaranteed" and v.value_kind == "exact" and not v.conditions and roles == {"guaranteed"} and len(amounts) == 1:
                    if not group_guarantee_added:
                        total["guaranteed_compensation"].append(row)
                        group_guarantee_added = True
                elif v.modality == "conditional":
                    total["conditional_compensation"].append(row)
                else:
                    total["potential_compensation"].append(row)
            if "guaranteed" in roles and roles != {"guaranteed"}:
                uncertainties.append(f"The advertised guarantee for {c.subject} is qualified elsewhere; guaranteed payment is not established.")
    for currency, total in totals.items():
        for k in ("mandatory_upfront_cost", "optional_fees", "deposits", "fixed_deductions"):
            total[k] = str(total[k])
        total["claim_ids"] = list(dict.fromkeys(total["claim_ids"]))
    return {"currencies": dict(totals), "values": rows, "uncertainties": list(dict.fromkeys(uncertainties)), "refund_policy": "Documented terms: " + "; ".join(c.refund_terms for c in active if c.refund_terms) if any(c.refund_terms for c in active) else "Unknown — no refund terms provided.", "method": "Decimal arithmetic; duplicate obligations grouped by scope, purpose, currency and unit. Conflicting costs excluded. No currency conversion, tax estimate, duration multiplication or assumed refundability."}


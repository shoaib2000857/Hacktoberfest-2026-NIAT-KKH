from .normalization import normalize
from .schemas import Claim, ScopeResult


def compare_scope(left: Claim, right: Claim) -> ScopeResult:
    a, b = normalize(left), normalize(right)
    reasons, unknowns = [], []
    if a.category != b.category:
        reasons.append("Different benefits or payment categories.")
    if a.subject != b.subject or a.predicate != b.predicate:
        reasons.append("Different subjects or attributes; semantic equivalence is not established.")
    for field in type(a.scope).model_fields:
        av, bv = getattr(a.scope, field), getattr(b.scope, field)
        if av and bv and av != bv:
            reasons.append(f"Different {field.replace('_', ' ')}: {av} versus {bv}.")
        elif not av or not bv:
            unknowns.append(f"{field.replace('_', ' ')} is not established in both claims.")
    if a.effective_date and b.effective_date and a.effective_date != b.effective_date and not (a.version_group and a.version_group == b.version_group):
        unknowns.append("Different effective dates without a documented version relationship; simultaneous applicability is unestablished.")
    # Optional charges never establish a mandatory charge for an advertised free service.
    if a.category == b.category == "fee" and ((a.amount == 0 and b.modality == "optional") or (b.amount == 0 and a.modality == "optional")):
        reasons.append("An optional charge does not establish a mandatory fee.")
    if a.currency and b.currency and a.currency != b.currency:
        reasons.append("Different currencies; no exchange rate is available.")
    coverage_pair = a.category == b.category == "scholarship" and {a.unit, b.unit} == {"percent", "one_time"}
    if a.unit != b.unit and (a.unit or b.unit) and not coverage_pair:
        reasons.append("Different measurement or payment units.")
    if reasons:
        return ScopeResult(comparable=False, certain=False, reasons=reasons, unknowns=unknowns)
    return ScopeResult(comparable=True, certain=not unknowns, reasons=["The documented subjects, attributes and known scope dimensions match."], unknowns=unknowns)


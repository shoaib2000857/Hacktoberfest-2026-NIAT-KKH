from itertools import combinations

from .contradictions import compare
from .normalization import normalize
from .schemas import Claim, Finding


def candidates(claims: list[Claim]):
    for a, b in combinations([normalize(c) for c in claims if c.review_status != "rejected"], 2):
        if a.source_id != b.source_id and a.category == b.category:
            yield a, b


def analyze(claims: list[Claim]) -> list[Finding]:
    return [compare(a, b) for a, b in candidates(claims)]


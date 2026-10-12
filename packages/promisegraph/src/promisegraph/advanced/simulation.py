from .contradictions import compare
from .normalization import normalize
from .schemas import Claim


def simulate(a: Claim, b: Claim):
    return compare(normalize(a.model_copy(deep=True)), normalize(b.model_copy(deep=True)), hypothetical=True)


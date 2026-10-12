import re
from decimal import Decimal

from .schemas import Claim


def canonical(value: str | None) -> str | None:
    return re.sub(r"\s+", " ", value.strip().casefold()) if value else None


def normalize(claim: Claim) -> Claim:
    c = claim.model_copy(deep=True)
    for field in ("subject", "predicate", "unit"):
        setattr(c, field, canonical(getattr(c, field)))
    if c.currency:
        c.currency = {"₹": "INR", "RS": "INR", "RUPEES": "INR", "$": "USD", "€": "EUR"}.get(c.currency.upper(), c.currency.upper())
    if c.unit:
        c.unit = {"per month": "month", "monthly": "month", "/month": "month", "one time": "one_time", "one-time": "one_time"}.get(c.unit, c.unit)
    for field in type(c.scope).model_fields:
        setattr(c.scope, field, canonical(getattr(c.scope, field)))
    c.conditions = list(dict.fromkeys(x.strip() for x in c.conditions if x.strip()))
    return c


def monetary_values(text: str) -> list[tuple[Decimal, str]]:
    values = []
    for match in re.finditer(r"(₹|INR|Rs\.?|USD|\$|EUR|€)\s*([0-9]+(?:,[0-9]{2,3})*(?:\.[0-9]{1,2})?)", text, re.I):
        currency = {"₹": "INR", "rs": "INR", "rs.": "INR", "$": "USD", "€": "EUR"}.get(match[1].lower(), match[1].upper())
        values.append((Decimal(match[2].replace(",", "")), currency))
    return values


def parse_money(text: str) -> tuple[Decimal, str] | None:
    values = monetary_values(text)
    return values[0] if values else None


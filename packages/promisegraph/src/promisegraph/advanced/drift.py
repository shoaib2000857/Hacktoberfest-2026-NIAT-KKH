from .schemas import Investigation, Stage


def journey(inv: Investigation) -> dict:
    dated = bool(inv.sources) and all(s.publication_date for s in inv.sources)
    stages = list(Stage)
    sources = sorted(inv.sources, key=lambda s: (s.publication_date.isoformat() if dated else f"{stages.index(s.stage):02}", s.filename))
    return {"label": "Publication timeline" if dated else "Document Sequence", "note": "Publication dates were supplied by the user." if dated else "Grouped by application stage. Upload order does not establish chronology.", "stages": [{"source": s.model_dump(mode="json"), "claim_ids": [c.id for c in inv.claims if c.source_id == s.id], "finding_ids": [f.id for f in inv.findings if any(c.id in f.claim_ids and c.source_id == s.id for c in inv.claims)]} for s in sources]}


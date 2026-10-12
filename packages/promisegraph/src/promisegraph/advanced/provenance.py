import hashlib

from .schemas import Investigation, now


def fingerprint(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def graph(inv: Investigation) -> dict:
    nodes = [{"id": s.id, "kind": "source", "label": s.filename} for s in inv.sources]
    nodes += [{"id": c.id, "kind": "claim", "label": c.normalized_statement} for c in inv.claims]
    nodes += [{"id": f.id, "kind": "finding", "label": f.classification.replace("_", " "), "classification": f.classification} for f in inv.findings]
    edges = [{"from": c.source_id, "to": c.id, "relation": "contains"} for c in inv.claims]
    relation = {"contradiction": "contradicts", "potential_conflict": "potential conflict", "changed_term": "updates", "material_qualification": "qualifies", "consistent": "repeats", "insufficient_evidence": "unresolved", "missing_disclosure": "missing disclosure"}
    for f in inv.findings:
        edges.extend({"from": cid, "to": f.id, "relation": "supports"} for cid in f.claim_ids)
        if len(f.claim_ids) == 2:
            edges.append({"from": f.claim_ids[0], "to": f.claim_ids[1], "relation": relation[f.classification], "finding_id": f.id})
    return {"nodes": nodes, "edges": edges}


def receipt(inv: Investigation) -> dict:
    return {"investigation_id": inv.id, "generated_at": now(), "sources": [s.model_dump(mode="json", exclude={"text", "pages"}) for s in inv.sources], "notice": "Fingerprints record content received by this application and compare bytes. They do not establish origin, authorship or historical authenticity."}


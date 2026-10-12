# PromiseGraph methodology

1. Hash and preserve each uploaded source. Record actual upload timestamps and user-supplied publication dates separately.
2. Gemma 4 receives text and image/PDF page content with an explicit untrusted-document boundary. It extracts typed claims, quotes, conditions, modalities and scope.
3. Validate response structure and source references. Assign claim IDs from source, exact quote, subject and predicate; deduplicate identical claims.
4. Normalize numeric/currency fields and common subject/predicate aliases. Index claims by comparable category, subject and predicate.
5. Compare cross-source candidates. Skip explicit audience/stage mismatch, optional services and incompatible numeric units/currencies. Different conditions require scope review; explicit guaranteed-vs-conditional benefits are examined as discrepancies.
6. For dated sources in the same version group, classify differing comparable terms as changed terms. Dates are not invented from upload order.
7. Verify exact quotes against extracted text. Missing quotes, nonexistent sources and image-only quotes cannot create an automatically verified contradiction.
8. Gemma reviews up to 20 ambiguous findings, with a constrained classification vocabulary and validated explanation. Deterministic findings remain with a visible limitation if semantic review fails.
9. Persist results and human review. Export provenance and limitations together.

Classifications: contradiction, potential conflict, changed term, missing disclosure, consistent, insufficient evidence. Absence of a term is not proof of contradiction. Severity means materiality, not fraud likelihood. No model confidence number is presented as calibrated probability.

Candidate recall depends on consistent extraction field names. Semantic matching beyond deterministic buckets is deferred. A quotation occurring in extracted text verifies transcription, not authenticity or truth. A publication date and version group are supplied metadata, not independently authenticated facts.

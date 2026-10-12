# Evaluation — 12 October 2026

The current `promisetrap` integration passes **77 pytest tests**, `npm run typecheck`, and `npm run build` (Next.js 16.4.0 / React 19). Baseline: all 36 existing tests passed before enhancement. CI remains the existing Python 3.12 / Node 22 workflow. Upstream Starlette/httpx and PyMuPDF deprecation warnings remain; there are no test failures.

## What was actually tested

- Independent deterministic engine: structured scope, amount/currency/unit handling, optional services, guarantees versus qualifiers, dated revisions, unknown scope, scholarship caps with unknown/sufficient/insufficient tuition, Decimal financial totals, duplicate obligations, refund unknowns, eligibility and hypothetical isolation.
- Real FastAPI + SQLite + local files via TestClient: ingestion, source bytes/hash verification, valid PDF ingestion/rasterization, all four advanced fixtures, review persistence, claim rejection, receipt equality/differences, reports, clarification templates, and original routes.
- Mocked model adapters: JSON repair, malicious instructions kept in source data, invalid citations, explicit model selection, successful/failed/partial extraction, caching, alternative interpretations retaining original rules. These tests do **not** validate actual Google/Ollama inference or model injection resistance.
- Real Chrome against running Next.js and Uvicorn: internship fixtures produced three findings; Evidence Lens showed exact highlighted source quotes; PromiseLab optional-certificate edit returned no mandatory-fee contradiction; calculator showed INR 499 upfront and no established stipend guarantee; graph filter/selection highlighted five connected nodes; clarification generated a sourced editable draft. A 390×844 layout showed no horizontal page overflow. Screenshot artifacts are in `docs/screenshots/`.
- Report response content and source raster endpoints are integration-tested. The five-page extended PDF was rendered locally and visually inspected; heading/spacer grouping was repaired to avoid orphan headings. Browser download notification automation timed out; report controls now use direct server links instead of blob downloads.

## Live model status

`python scripts/smoke_gemma.py` was actually run and failed with **GEMINI_API_KEY is not configured**. No cloud request was made and no Gemma result was invented. Default allowlisted model: `gemma-4-26b-a4b-it`; optional alternative: `gemma-4-31b-it`. Dedicated `scripts/validate_gemma.py` loads genuine fictional PNGs and performs actual Gemini-hosted Gemma extraction when configured. Its results are not assumed identical to authored fixtures; image-only anchors need visual review.

Older branch documentation recorded a READY response and a local Ollama run in another environment. Those notes are not evidence of current-host access, and their extraction results were not reproduced during this release. No benchmark precision/recall, fraud detection rate, or latency promise is claimed.

## Reproduce

```sh
.venv/bin/python -m pytest -q
npm run typecheck
npm run build
.venv/bin/python scripts/evaluate_fixtures.py --output /tmp/promisetrap-evaluation.json
```

The fixture evaluator exercises real routes and comparison logic in an isolated temporary database; it makes no model calls. [Recorded output](evaluation-results.json) and [expected outputs](../examples/advanced/expected.json) distinguish the optional service (no matched issue) from a hypothetical cross-service comparison (insufficient comparable evidence).

## Requested twelve scenarios

| Scenario | Coverage |
|---|---|
| Matched registration fee conflict | `test_real_fee_contradiction`, authored internship API fixture |
| Optional certificate false-positive avoidance | optional engine tests and API fixture |
| Possible certificate with attendance | `test_conditional_certificate_is_qualification` |
| Guarantee becomes conditional maximum | `test_guarantee_to_conditional_change` |
| Dated changed deadline | `test_deadline_version_change`, deadline API fixture |
| Unknown applicant scope | `test_unknown_audience_prevents_definitive_contradiction` |
| PromiseLab changes result, preserves evidence | independent simulation + API isolation test + Chrome |
| Different recorded bytes | fingerprint and receipt equality/difference API tests |
| Source prompt injection | `test_injection_stays_document_data` (mock prompt separation only) |
| Invalid source/claim citation | adapter, verification and challenge API rejection tests |
| Upfront fee with conditional stipend | financial unit tests, API calculator and Chrome |
| Missing refund data | `test_missing_refund_unknown`, calculator API |

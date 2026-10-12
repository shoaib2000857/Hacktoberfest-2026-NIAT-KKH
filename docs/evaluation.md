# Evaluation

Initial local verification, 12 October 2026:

- `python -m pytest -q`: 23 tests passed (two upstream dependency deprecation warnings).
- `npm.cmd run typecheck`: passed.
- `npm.cmd run build`: production build passed.
- Frontend `GET /`: HTTP 200; backend `GET /api/v1/health`: HTTP 200.
- Live Gemma: not executed; no API key configured.
- Browser rendering/E2E: unavailable; connected browser inventory was empty.

Tests cover numeric/currency normalization, comparable fee conflict, non-conflicting optional certificate, different audience/stage, incompatible currency, explicit guarantee vs conditions, possibility vs qualification, unverified quotes, image-only evidence, invalid source/duplicate IDs, dated updates, undated version handling, mismatched conditions, investigation lifecycle, source hash/bytes, synthetic workflow, graph/timeline, reviews, PDF/Markdown/JSON exports, real PDF text ingestion, batch dates, mocked Gemma pipeline and failure handling.

The authored fixture and mocked provider outputs are not live inference. The example's three findings are calculated by the original engine from supplied authored claims. Live accuracy needs an independently labeled dataset and actual model runs. No precision/recall or fraud-detection performance is claimed.

Before judging, run the live smoke test, upload an actual synthetic poster image plus terms, inspect every extracted quotation, show the optional-certificate negative case, and record model identifier and timestamp. Verify desktop/mobile rendering, keyboard dialog behavior, source-upload UI, graph interactions, and browser download behavior on a real browser. Capture screenshots only after this visual check.

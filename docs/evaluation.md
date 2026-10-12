# Evaluation

Initial local verification, 12 October 2026:

- Final `python -m pytest -q`: 36 tests passed (two upstream dependency deprecation warnings).
- `npm.cmd run typecheck`: passed.
- `npm.cmd run build`: production build passed.
- Frontend `GET /`: HTTP 200; backend `GET /api/v1/health`: HTTP 200.
- Live Gemma 4 smoke test: `gemma-4-26b-a4b-it` returned `READY` using the user-configured backend key. This verifies access, not extraction accuracy.
- Real local Ollama extraction: `gemma3:4b` extracted 14 claims from three synthetic internship text documents. After explicit-quotation normalization was improved, replaying those real extracted claims through PromiseGraph produced three text-verified contradictions (fee, stipend, certificate). JSON/Markdown/PDF exports succeeded. No authored claims or mocked model were used for this run.
- Browser rendering/E2E: unavailable; connected browser inventory was empty.

Tests cover numeric/currency normalization, comparable fee conflict, non-conflicting optional certificate, different audience/stage, incompatible currency, explicit guarantee vs conditions, possibility vs qualification, unverified quotes, image-only evidence, invalid source/duplicate IDs, dated updates, undated version handling, mismatched conditions, investigation lifecycle, source hash/bytes, synthetic workflow, graph/timeline, reviews, PDF/Markdown/JSON exports, real PDF text ingestion, batch dates, mocked Gemma pipeline and failure handling.

The authored fixture and mocked provider outputs are not live inference. The example's three findings are calculated by the original engine from supplied authored claims. The separately saved Ollama validation case uses real inference. A small local model initially returned generic field names and null quantities; original quotation-based normalization recovered explicit values and modalities conservatively. New negative-case tests ensure optional services remain distinct. Live accuracy needs an independently labeled dataset and actual model runs. No precision/recall or fraud-detection performance is claimed.

Before judging, run the live smoke test, upload an actual synthetic poster image plus terms, inspect every extracted quotation, show the optional-certificate negative case, and record model identifier and timestamp. Verify desktop/mobile rendering, keyboard dialog behavior, source-upload UI, graph interactions, and browser download behavior on a real browser. Capture screenshots only after this visual check.

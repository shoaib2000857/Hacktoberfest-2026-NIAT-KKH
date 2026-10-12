# PromiseTrap enhancement release — `promisetrap`

This release extends the existing application on `promisetrap`. It is verified locally; live cloud extraction and event publication/submission are not complete.

## 1. Existing features found and preserved

Next.js/TypeScript/React Flow workspace, FastAPI, SQLite dossier persistence, original UUID file storage, typed claims, original deterministic engine, source uploads/previews, original nine-claim internship example, analyst reviews/notes, report exports, Gemma SDK integration and explicit Ollama provider. Baseline 36 tests passed before integration. The organizer `main` branch was not changed.

## 2. Implemented features and verification

| Feature | Implemented behavior | Verification |
|---|---|---|
| ScopeGuard | Program, audience, purpose, period, process, contract and qualifying-event checks; optional/unit/currency/version guards; unknown scope downgrades certainty | Engine/API tests |
| Evidence Lens | Exact excerpt highlighting, condition/scope details, source navigation, actual images and bounded PDF raster pages; approximate image labels | API + real Chrome text Lens |
| Promise Journey | Stage grouping, actual supplied dates, source/claim navigation, findings/condition dependencies; Document Sequence if dates unknown | API/engine tests; integrated UI |
| Reality Calculator | Decimal values, mandatory upfront/optional fees, deposits/deductions, guarantees versus conditional/maximum/potential benefits, source links, review, unknown refunds | Engine/API + Chrome desktop/mobile |
| FinePrint Radar / ConditionChain | Benefits with documented qualifiers and parallel prerequisite cards; no fabricated order; compare extracted advertised conditions | Engine/API tests; integrated UI |
| Personal Reality | Minimal explicit criteria, satisfied/not-satisfied/unknown; transient profile | API tests; integrated UI |
| Devil’s Advocate | Separate provider prompt, typed referenced alternatives, suggested classification, original rule retained, collapsible panel | Mock adapter + API tests; live provider pending |
| PromiseLab | Editable structured sandbox, real normalization/comparison, classification/reason/field changes, reset, originals preserved | Unit/API + Chrome optional-certificate scenario |
| Clarification Copilot | Sourced respectful editable/copyable questions, offline template or selected provider, never sends | API + Chrome offline; live model pending |
| Promise Receipt | Stable IDs, original hashes/type/timestamps/model metadata, downloadable receipt and byte comparison | API hash/equality/difference tests |
| Evidence graph | Existing React Flow enhanced with filters, connected evidence, details, source navigation | API + Chrome five-node selection |
| Human review / history | Claim corrections/rejection, source metadata, analyst review, before/after audit, unchanged review preservation | API tests |
| Reliability / privacy | Validated cache, recorded-byte integrity before extraction, partial failures, real stages/retries, duplicate-analysis guard, local Host/origin protections | API/adapter tests |

## 3. Files changed

Core API/adapter/store; retained engine/schema; Next page, shared types, graph, new InvestigationTools component and palette-compatible styles. Added independent advanced modules and bridge, integration tests, four PNG/text scenarios and expected outputs, sample/evaluation/live scripts, screenshots and updated docs. Detailed file manifest follows below.

## 4. Startup commands (repository root)

Python 3.12+ and Node 22+. Install `requirements.txt` and `npm ci`. Copy `.env.example` to local `.env`.

```sh
.venv/bin/python -m uvicorn app.main:app --app-dir apps/api --host 127.0.0.1 --port 8000
npm run dev
```

Use separate terminals; browser http://127.0.0.1:3000 and API http://127.0.0.1:8000/docs. Windows equivalents: `.\.venv\Scripts\python.exe` and `npm.cmd`. Production frontend: `npm run build`, then `npm run start --workspace apps/web`.

## 5. Gemma connectivity

Default `gemma-4-26b-a4b-it`, allowlisted alternative `gemma-4-31b-it`, official google-genai. Backend-only key. Actual smoke test attempted: blocked by missing `GEMINI_API_KEY`. No cloud success has been fabricated, and no fallback provider runs silently. Ollama remains explicitly labeled and does not count as Gemini-hosted Gemma 4.

Configure the key locally and restart the backend, then run:

```sh
.venv/bin/python scripts/smoke_gemma.py
.venv/bin/python scripts/validate_gemma.py --scenario internship --output data/live-gemma.json
```

## 6. Deterministic PromiseGraph

Independent credential-free normalization, candidate matching, scoped contradiction/qualification/version rules, anchor/value validation, Decimal financial calculations, eligibility, condition dependencies, provenance and hypothetical simulation. Numeric differences are not automatically contradictions. Model semantic suggestions and alternatives remain separate from original classifications.

## 7–8. Tests and real-versus-mocked results

**77 pytest tests pass**; TypeScript checks and production build pass. Existing CI is retained. All four offline API fixtures match expected outcomes: internship three contradictions, scholarship cap contradiction only with documented tuition, optional service no issue, dated deadline changed term. Actual Chrome interaction and mobile checks are recorded in [evaluation](evaluation.md). The extended PDF was rendered and inspected; browser download-notification automation timed out, so direct server download links were used and API export bytes validated.

Mocked provider tests prove schema/reference handling, caching and failure behavior; they do not prove actual inference quality or prompt-injection resistance. Authored fixtures exercise the real comparison engine. No current live Google/Ollama model result was obtained here.

## 9–10. Unfinished work and limits

Live cloud access/extraction accuracy, actual saved cloud fallback, published release visibility, team identities/timing, demo recording and entry evidence remain open. URL ingestion, public deployment/auth, sharing, embeddings, monitoring, multilingual validation and extensions are deferred. Local single-user/one-worker app; original bytes remain unencrypted. Image-only wording is approximate and requires source review. Claims with unfamiliar wording may be missed by bucket matching. Clarification edits remain local until copied; generated drafts persist. Full limitations: [known limits](limitations.md).

## 11. Repository/license readiness

Connected remote: `shoaib2000857/Hacktoberfest-2026-NIAT-KKH`, application branch `promisetrap`. MIT license already exists and is preserved; Gemma model terms and third-party dependencies retain separate licensing. New changes are local and have not been pushed. Public anonymous access could not be confirmed from the available fetch; verify links before entry. No organizer PR or MLH entry was created. Attribution accurately records existing code and Codex assistance; no TattvaDrishti code was copied.

## 12. Demo

See [120-second script](demo-script.md). Home → Four fictional evaluation scenarios → Use internship fixtures gives the tested offline product demo. To demonstrate actual multimodal Gemma, choose Load internship images and run the real provider after smoke/quality checks. Never relabel authored claims as inference. PromiseLab optional-certificate edit is the tested signature interaction.

## 13. Submission readiness

Best Open-Source AI: original deterministic modules, reproducible setup/tests, MIT and model attribution are ready locally; public release and real open-weight model/demo evidence must be attached. Best Use of Gemma 4: code paths and genuine PNG inputs are ready; actual Gemini-hosted multimodal results are still required. [Organizer draft](organizer-submission-draft.md) follows its template. Confirm entering both categories, build-window rules, current form/deadline and team identity. Neither entry is represented as submitted.

## File manifest

- `README.md`
- `apps/api/app/advanced_samples.py`
- `apps/api/app/gemma.py`
- `apps/api/app/main.py`
- `apps/api/app/store.py`
- `apps/api/tests/test_advanced_api.py`
- `apps/api/tests/test_gemma.py`
- `apps/web/app/globals.css`
- `apps/web/app/page.tsx`
- `apps/web/components/EvidenceGraph.tsx`
- `apps/web/components/InvestigationTools.tsx`
- `apps/web/lib/types.ts`
- `docs/architecture.md`
- `docs/demo-script.md`
- `docs/evaluation-results.json`
- `docs/evaluation.md`
- `docs/gemma-integration.md`
- `docs/implementation-checklist.md`
- `docs/limitations.md`
- `docs/organizer-submission-draft.md`
- `docs/release-report.md`
- `docs/screenshots/evidence-graph.jpg`
- `docs/screenshots/evidence-lens.jpg`
- `docs/screenshots/mobile-calculator.jpg`
- `docs/screenshots/promiselab.jpg`
- `docs/screenshots/reality-calculator.jpg`
- `docs/submission.md`
- `examples/advanced/deadline-v1.png`
- `examples/advanced/deadline-v1.txt`
- `examples/advanced/deadline-v2.png`
- `examples/advanced/deadline-v2.txt`
- `examples/advanced/expected.json`
- `examples/advanced/internship-advertisement.png`
- `examples/advanced/internship-advertisement.txt`
- `examples/advanced/internship-offer.png`
- `examples/advanced/internship-offer.txt`
- `examples/advanced/internship-registration.png`
- `examples/advanced/internship-registration.txt`
- `examples/advanced/optional-advertisement.png`
- `examples/advanced/optional-advertisement.txt`
- `examples/advanced/optional-terms.png`
- `examples/advanced/optional-terms.txt`
- `examples/advanced/scholarship-advertisement.png`
- `examples/advanced/scholarship-advertisement.txt`
- `examples/advanced/scholarship-terms.png`
- `examples/advanced/scholarship-terms.txt`
- `packages/promisegraph/src/promisegraph/advanced/__init__.py`
- `packages/promisegraph/src/promisegraph/advanced/conditions.py`
- `packages/promisegraph/src/promisegraph/advanced/contradictions.py`
- `packages/promisegraph/src/promisegraph/advanced/drift.py`
- `packages/promisegraph/src/promisegraph/advanced/financial.py`
- `packages/promisegraph/src/promisegraph/advanced/matching.py`
- `packages/promisegraph/src/promisegraph/advanced/normalization.py`
- `packages/promisegraph/src/promisegraph/advanced/provenance.py`
- `packages/promisegraph/src/promisegraph/advanced/schemas.py`
- `packages/promisegraph/src/promisegraph/advanced/scopeguard.py`
- `packages/promisegraph/src/promisegraph/advanced/simulation.py`
- `packages/promisegraph/src/promisegraph/advanced/verification.py`
- `packages/promisegraph/src/promisegraph/engine.py`
- `packages/promisegraph/src/promisegraph/extensions.py`
- `packages/promisegraph/src/promisegraph/schemas.py`
- `packages/promisegraph/tests/test_advanced.py`
- `packages/promisegraph/tests/test_engine.py`
- `scripts/evaluate_fixtures.py`
- `scripts/generate_samples.py`
- `scripts/validate_gemma.py`

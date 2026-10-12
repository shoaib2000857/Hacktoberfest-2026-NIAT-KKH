# PromiseTrap

**Every promise deserves evidence.**

PromiseTrap investigates differences between advertisements, registration forms, offer letters, and other source documents. Gemma 4 performs multimodal structured extraction; the original **PromiseGraph** package normalizes and compares claims, verifies quotations, and builds evidence provenance. The product investigates claims, not people, and never produces a fraud probability.

The interface pairs matte noir with antique bronze and editorial typography. Evidence views stay calm and functional: source records, side-by-side highlighted quotations, analyst review, interactive provenance, Promise Journey, Reality Calculator, condition dependencies, PromiseLab, clarification drafts, receipts, and downloadable dossiers.

## Run on Windows

Requirements: Python 3.12+ and Node.js 22+. Docker and WSL are not required. Commands run from this repository root. Use `npm.cmd` if PowerShell blocks `npm.ps1`.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
npm.cmd ci
Copy-Item .env.example .env
```

Edit `.env` locally with your own `GEMINI_API_KEY`. Keep it out of Git and browser code. The default `GEMMA_MODEL` is `gemma-4-26b-a4b-it`; the only alternative is `gemma-4-31b-it`. There is no silent Gemini substitution. A key is not required to inspect the authored synthetic example.

Terminal 1:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir apps/api --host 127.0.0.1 --port 8000
```

Terminal 2:

```powershell
npm.cmd run dev
```

Open http://127.0.0.1:3000. API documentation: http://127.0.0.1:8000/docs. Next.js proxies `/api/v1` to the backend; the API key stays in Python. Optional `API_URL` configures the server-side proxy destination. Restart the API after changing its environment; restart Next.js after changing its proxy destination.

## Run on macOS / Linux

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
npm ci
cp .env.example .env
```

Set the backend key in the local `.env` for live Gemma. Then use two terminals:

```sh
.venv/bin/python -m uvicorn app.main:app --app-dir apps/api --host 127.0.0.1 --port 8000
npm run dev
```

```sh
.venv/bin/python -m pytest -q
npm run typecheck
npm run build
.venv/bin/python scripts/evaluate_fixtures.py
.venv/bin/python scripts/validate_gemma.py --scenario internship --output data/live-gemma.json
```

The last command is a separately identified live image test, requires the running backend and a key, and saves actual model output locally. It has no mock fallback. [Release report](docs/release-report.md) records implemented features, verification, limitations and submission gaps. [Demo script](docs/demo-script.md) includes a disclosed offline fallback.

## Try the workflow

1. Start an investigation and name the question.
2. Add at least two original sources (PNG, JPEG, WebP, PDF, UTF-8 text, Markdown, or a JSON batch).
3. Use Methodology & help → Verify live Gemma access, or run the smoke test below.
4. Run Gemma analysis. Actual extraction/verification stages appear while the persisted background job runs.
5. Inspect findings and exact quotes; open original source previews. Accept, reject, or leave findings unresolved, with analyst notes.
6. Assign document stages/dates in Sources; explore Promise Journey, condition requirements, and the graph's filters/connected evidence.
7. Review financial values in Reality Calculator. Conditional/maximum compensation stays separate from guarantees; unknown refund terms stay unknown.
8. Open a finding → Test in PromiseLab → Try optional certificate. The actual engine reruns hypothetical structured fields; original evidence remains unchanged.
9. Challenge This Finding requests an independent interpretation from the selected provider. Suggestions never overwrite the rule classification.
10. In Report, generate evidence-template questions offline or choose the selected model; edit/copy without sending. Download receipts and compare another copy's hash; export PDF, Markdown or JSON.

Home → **Four fictional evaluation scenarios** provides internship, scholarship, optional-service, and dated-deadline fixtures. **Load images** adds actual PNGs without authored extraction. You must separately run real Gemma to infer those images. Fixtures and live provenance are visibly distinct.

**Explore example** creates a synthetic internship dossier containing nine authored claims. The actual PromiseGraph engine identifies three discrepancies. The interface and model provenance explicitly disclose that this example uses authored claims, not live inference. The optional ₹200 printed certificate is a distinct optional service and is not treated as a registration-fee contradiction. Matching deadlines generate no finding.

## Live Gemma smoke test

```powershell
.\.venv\Scripts\python.exe scripts\smoke_gemma.py
```

Google's [official API documentation](https://ai.google.dev/gemma/docs/core/gemma_on_gemini_api) documents these Gemma models and image inputs. This repository uses the official `google-genai` Python SDK. Source images and rendered PDF pages are sent with source text. Responses are parsed and validated with Pydantic; malformed output gets one bounded repair attempt. Transient provider failures receive bounded backoff and explicit timeouts. No successful response is fabricated.

**Current verification (12 October 2026):** 77 engine/API tests pass, TypeScript checks pass, and the production build passes. Real Chrome interaction checks cover source quotations, PromiseLab, the calculator, graph selection, and mobile layout. See [evaluation](docs/evaluation.md). The live Gemma smoke command was attempted on this host and stopped because `GEMINI_API_KEY` is not configured. No current cloud success or accuracy claim is made. Previously recorded branch notes about READY/Ollama runs are historical and were not reproduced here.

## Ollama local validation

The investigation toolbar offers two explicit providers: **Gemma 4 · Gemini API** and **Ollama · local validation**. Local Ollama is the initial selection while cloud access is being configured. The model selector lists installed completion models; models marked vision support image inputs. Default: `gemma3:4b`. Set `OLLAMA_MODEL` and the loopback-only `OLLAMA_BASE_URL` in the backend environment if needed. There is no silent fallback between providers.

```powershell
.\.venv\Scripts\python.exe scripts\validate_ollama.py --model gemma3:4b
```

This sends synthetic text sources through actual local inference, persists the investigation, and verifies JSON/Markdown/PDF exports. `--vision` adds a synthetic poster image. `--provider gemma` uses the configured cloud Gemma 4 model instead. Ollama uses schema-constrained JSON and the same Pydantic/evidence checks as Gemma. Its output is recorded as `ollama:<model>`. Local runs do not establish eligibility for the dedicated Gemma 4 track. See [Ollama structured-output documentation](https://docs.ollama.com/capabilities/structured-outputs).

## Original engine contribution

`packages/promisegraph` is independently installable and does not depend on Google, FastAPI or an API key. It provides:

- Currency/numeric and claim-field normalization.
- Bucketed candidate matching by category, subject and predicate.
- Audience, stage, optional-service, condition, currency/unit and effective-period checks.
- Numeric and guarantee/condition discrepancies, added-condition disclosures, and dated version changes.
- Exact excerpt verification and conservative downgrades for unsupported quotations.
- Stable finding identifiers and source → claim → finding provenance.

Gemma semantic comparison reviews bounded ambiguous rule findings. An LLM cannot promote an unverified quotation into a verified contradiction. Review decisions remain attached when stable findings retain the same classification, explanation, scope and evidence state; changed findings require fresh review. Prior states are recorded in review history. This is an original comparison harness, not a renamed third-party harness. It does not expose private chain-of-thought; the graph shows evidence provenance.

## Repository

```text
apps/web/              Next.js, TypeScript, React Flow, custom design system
apps/api/app/          FastAPI, Gemma adapter, ingestion, persistence, reports
apps/api/tests/        API and mocked inference tests
packages/promisegraph/ Independent Python comparison package and tests
examples/              Synthetic source batches and demo inputs
docs/                  Architecture, methodology, limitations, submission draft
scripts/               Optional live smoke test
.github/workflows/     Python tests and frontend build CI
```

Persistence uses a versioned SQLite document table; the first schema migration runs at startup. Source bytes are stored separately under UUID filenames in the local `data/` directory. An in-process worker persists stages and results. Interrupted jobs are marked failed on API restart rather than remaining stuck. This compact architecture is designed for local development, not multi-worker deployment.

## Verify

```powershell
.\.venv\Scripts\python.exe -m pytest -q
npm.cmd run typecheck
npm.cmd run build
```

CI uses deterministic mock model adapters; the synthetic example uses authored claims. Live inference requires a separate smoke test and real-source evaluation. Dependency versions for the frontend are locked by `package-lock.json`; Python versions validated locally are recorded in `requirements.lock.txt`.

## Limits and privacy

Files: 12 MB each; 12 sources per investigation; PDFs: at most 20 unencrypted pages; text: 60,000 characters; images: at most 20 megapixels. Exact text evidence can be verified automatically. Image-only quotes are approximate and require visual review. PDF page citations are assigned only when quotations occur in page text. Unknown publication dates remain unknown; upload order is never represented as publication chronology.

This is a local, single-user workspace without authentication. Bind both servers to loopback. Do not expose it publicly as-is. Original evidence is unencrypted on this machine. Running live analysis transmits the supplied content to Google. Graphs, notes and reports stay local; exports may contain sensitive original quotations. Deletion removes the dossier and its source files. There is no share feature or hidden telemetry in application code. Web fonts may load from Google Fonts; system/Georgia fallbacks work when unavailable.

Safe URL fetching, source deletion within an active dossier, authentication, public sharing, background queues, scheduled monitoring, embeddings, AI-text detection and browser extensions are deferred. URL ingestion is deliberately absent until a DNS-pinned, redirect-safe SSRF implementation can be validated. No unavailable feature has a pretend action button. Review all [known limitations](docs/limitations.md).

## Attribution and licensing

Application and PromiseGraph: MIT ([LICENSE](LICENSE)). Gemma 4 is an open-weight Google model; its licensing is separate from this application. See the [official model card](https://ai.google.dev/gemma/docs/core/model_card_4) and [official Gemma 4 repository/license](https://huggingface.co/google/gemma-4-26B-A4B-it). Dependencies retain their own licenses.

TattvaDrishti inspired multimodal ingestion, batch analysis, source tracing and descriptive pattern analysis. No TattvaDrishti source code or model weights were supplied or copied. This enhancement extends the existing PromiseTrap application on the `promisetrap` branch; the Next.js/FastAPI/SQLite/PromiseGraph architecture and explicit Ollama provider are retained. Contributors: PromiseTrap project team, with Codex-assisted implementation. Record team names and actual development timing before publishing.

## Hackathon readiness

Built for MLH Hacktoberfest Hack Day 2026, Hyderabad, targeting Best Use of Gemma 4 and Best Open-Source AI Project. The team must attest to the organizer-authorized build window and development timing. A local implementation is not proof of submission or eligibility: verify event-specific timing and demonstrate live Gemma multimodal extraction. Verify public access to the connected application branch, capture a real Gemma demo, and complete [the submission draft](docs/submission.md). No repository was published and no entry was submitted by this implementation task.

Future engineering priorities: real-model extraction evaluation, semantic candidate recall, authenticated deployment and worker infrastructure. Contribute via [CONTRIBUTING.md](CONTRIBUTING.md).

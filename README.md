# PromiseTrap

**Every promise deserves evidence.**

PromiseTrap investigates differences between advertisements, registration forms, offer letters, and other source documents. Gemma 4 performs multimodal structured extraction; the original **PromiseGraph** package normalizes and compares claims, verifies quotations, and builds evidence provenance. The product investigates claims, not people, and never produces a fraud probability.

The interface pairs matte noir with antique bronze and editorial typography. Evidence views stay calm and functional: source records, side-by-side highlighted quotations, analyst review, interactive provenance, promise drift, and downloadable dossiers.

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

## Try the workflow

1. Start an investigation and name the question.
2. Add at least two original sources (PNG, JPEG, WebP, PDF, UTF-8 text, Markdown, or a JSON batch).
3. Use Methodology & help → Verify live Gemma access, or run the smoke test below.
4. Run Gemma analysis. Actual extraction/verification stages appear while the persisted background job runs.
5. Inspect findings and exact quotes; open original source previews. Accept, reject, or leave findings unresolved, with analyst notes.
6. Explore the graph and timeline; export PDF, Markdown or JSON.

**Explore example** creates a synthetic internship dossier containing nine authored claims. The actual PromiseGraph engine identifies three discrepancies. The interface and model provenance explicitly disclose that this example uses authored claims, not live inference. The optional ₹200 printed certificate is a distinct optional service and is not treated as a registration-fee contradiction. Matching deadlines generate no finding.

## Live Gemma smoke test

```powershell
.\.venv\Scripts\python.exe scripts\smoke_gemma.py
```

Google's [official API documentation](https://ai.google.dev/gemma/docs/core/gemma_on_gemini_api) documents these Gemma models and image inputs. This repository uses the official `google-genai` Python SDK. Source images and rendered PDF pages are sent with source text. Responses are parsed and validated with Pydantic; malformed output gets one bounded repair attempt. Transient provider failures receive bounded backoff and explicit timeouts. No successful response is fabricated.

**Initial verification status:** all local engine/API tests and frontend checks passed. Live Gemma inference was not run because no API key was configured. Successful local tests do not establish live model access or extraction quality. Browser visual/E2E verification was unavailable in the connected environment. See [evaluation](docs/evaluation.md).

## Original engine contribution

`packages/promisegraph` is independently installable and does not depend on Google, FastAPI or an API key. It provides:

- Currency/numeric and claim-field normalization.
- Bucketed candidate matching by category, subject and predicate.
- Audience, stage, optional-service, condition, currency/unit and effective-period checks.
- Numeric and guarantee/condition discrepancies, added-condition disclosures, and dated version changes.
- Exact excerpt verification and conservative downgrades for unsupported quotations.
- Stable finding identifiers and source → claim → finding provenance.

Gemma semantic comparison reviews bounded ambiguous rule findings. An LLM cannot promote an unverified quotation into a verified contradiction. Review decisions remain attached to stable IDs when equivalent claims recur. This is an original comparison harness, not a renamed third-party harness. It does not expose private chain-of-thought; the graph shows evidence provenance.

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

TattvaDrishti inspired multimodal ingestion, batch analysis, source tracing and descriptive pattern analysis. No TattvaDrishti source code or model weights were supplied or copied. The implementation was created in this initially empty workspace. Contributors: PromiseTrap project team, with Codex-assisted implementation. Record team names and actual development timing before publishing.

## Hackathon readiness

Built for MLH Hacktoberfest Hack Day 2026, Hyderabad, targeting Best Use of Gemma 4 and Best Open-Source AI Project. The user confirmed the organizer-authorized build window had started. A local implementation is not proof of submission or eligibility: verify event-specific timing and demonstrate live Gemma multimodal extraction. Publish to a public repository with this license, capture a real demo, and complete [the submission draft](docs/submission.md). No repository was published and no entry was submitted by this implementation task.

Future engineering priorities: real-model extraction evaluation, visual/browser QA, semantic candidate recall, scope normalization, authenticated deployment and worker infrastructure. Contribute via [CONTRIBUTING.md](CONTRIBUTING.md).

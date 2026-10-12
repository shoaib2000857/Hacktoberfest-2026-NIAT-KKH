# Known limitations

- Live Gemma has not been verified without a configured API key. Mocked tests validate pipeline behavior, not model accuracy.
- No connected browser was available for visual QA, responsive screenshots, or browser E2E verification. CSS and build checks do not substitute for these checks.
- Local single-user application; no login, public sharing, encryption at rest or deployment hardening. Use loopback only.
- SQLite persists versioned dossier JSON rather than normalized SQLAlchemy/Alembic models. Use one API worker. Mutating a source during analysis is blocked, but concurrent multi-client ingestion is not a supported deployment topology.
- Models may extract inconsistent subject names, omit claims, or misread images. Candidate retrieval is bucketed and does not use embeddings. Unknown scope still needs manual equivalence checks.
- Image-only quotes receive approximate locations and insufficient-evidence findings. No bounding boxes or coordinates are fabricated. Quotes in PDF text receive actual page references.
- Input PDF limit is 20 pages and total text is 60,000 characters. All PDF pages are rendered for Gemma; this may reach provider image/token limits before application file limits. No background OCR engine is installed.
- Stable review preservation requires equivalent source, quote, subject and predicate. Semantically equivalent but differently extracted wording may yield a new ID. Old findings are replaced on successful reanalysis; an audit-version archive is a future requirement.
- Drift requires dated sources within an explicit shared version group. Undated evidence is document sequence. There is no URL monitoring.
- Timeline exposes source-associated claims and detected version changes, not an automated reconstruction of history.
- Graph uses deterministic column placement, not a force-directed layout. Full graph finding filters are deferred; Findings has classification/search filters.
- PDF reports use ReportLab base fonts and replace rupee signs with INR. Broader Unicode scripts require an embedded licensed Unicode font. JSON/Markdown retain the original Unicode quotes.
- No URL extraction, email-export parser, source deletion within a dossier, auth, share links, browser extension, AI-text detector, embeddings, or deployed service. Images of emails and pasted email text work.
- No public GitHub repository or event submission has been created. Submission readiness still requires live model verification, multimodal demo, visual QA, public code/license access and team information.

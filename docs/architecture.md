# Architecture

```mermaid
flowchart LR
  UI[Next.js evidence workspace] -->|same-origin /api/v1| API[FastAPI local API]
  API --> Store[Versioned SQLite dossier records]
  API --> Files[Original bytes under UUID filenames]
  API --> Job[Persisted in-process analysis stages]
  Job --> Gemma[Gemma 4 via google-genai]
  Gemma --> Validate[Pydantic extraction validation]
  Validate --> PG[PromiseGraph normalization and candidate matching]
  PG --> Rules[Scope-aware deterministic rules]
  Rules --> Semantic[Bounded Gemma review of ambiguous findings]
  Semantic --> Evidence[Quote verification and conservative classification]
  Evidence --> Store
  Store --> Graph[Source / claim / finding provenance]
  Store --> Reports[JSON / Markdown / PDF reports]
```

The API stores source bytes outside the database and persists complete typed analysis records in a single versioned document table. This deliberately avoids a premature distributed system. The database migration is idempotent. A multi-tenant version should migrate normalized records through Alembic, add authorization and authenticated file storage, and move jobs to a worker queue.

React Flow shows the supplied evidence chain. It supports pan/zoom, draggable nodes, selection, and accessible evidence-list equivalents. Findings filters are in the Findings view; graph filtering is deferred. Selecting a source or claim opens its source record; selecting a finding opens the comparison dialog.

Native Windows development is supported. The frontend proxies to Python on loopback. There is no browser-side API credential and no external connector dependency.

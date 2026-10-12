# PromiseTrap

## Team / attendee

- Team name: PromiseTrap
- Members and GitHub usernames:
  - Shoaib - [shoaib2000857](https://github.com/shoaib2000857)
  - Omar - [DevXOmar](https://github.com/DevXOmar)
  - Jinal - [jinaljpt](https://github.com/jinaljpt)
  - Hansika - [a-hansika](https://github.com/a-hansika)

## Challenge

- [x] Best Open-Source AI Project
- [x] Best Use of Gemma 4

The team targets both categories in one MLH entry; organizers determine final eligibility.

## Project links

- Public GitHub repository: https://github.com/shoaib2000857/PromiseTrap
- Open-source license: https://github.com/shoaib2000857/PromiseTrap/blob/main/LICENSE (MIT)
- Hosted frontend preview: https://promisetrap.vercel.app (frontend only; full workflow runs locally)
- Screenshots: https://github.com/shoaib2000857/PromiseTrap/tree/main/docs/screenshots
- Demo instructions: https://github.com/shoaib2000857/PromiseTrap/blob/main/docs/demo-script.md
- Demo video: not yet supplied; team will add separately.

## Problem and solution

Advertisements, registration forms, and offer letters can make different promises about the same opportunity. PromiseTrap helps students, applicants, and consumers inspect conflicting fees, conditions, guarantees, and changing terms before committing money or time.

Original screenshots, images, PDFs, emails, or text become structured claims through Gemma 4. The original PromiseGraph engine normalizes values, checks scope, compares claims, verifies quotations, and builds source-to-claim-to-finding provenance. Users inspect side-by-side evidence, interactive graphs, promise timelines, and financial summaries, then review findings and export a dossier. The product investigates claims, not people, and does not produce a fraud probability.

## Approach and technologies

Next.js, React, TypeScript, React Flow, Lucide, Python, FastAPI, Pydantic, SQLite, Google GenAI Python SDK, Gemini API, Gemma 4, Ollama, PyMuPDF, Pillow, ReportLab, pytest, and Vercel (frontend).

The MIT-licensed PromiseGraph package is independently installable and has no Google or FastAPI dependency. Its ScopeGuard distinguishes audiences, periods, optional services, conditions, and units. Reality Calculator separates mandatory costs and guaranteed compensation from conditional or maximum benefits. PromiseLab compares hypothetical structured changes without modifying original evidence; hashed receipts record source integrity.

Development was assisted by Codex with GPT-6.1 Sol, as disclosed by the team. The enhancement builds on the team's existing PromiseTrap implementation and retains its architecture and explicit local Ollama adapter. TattvaDrishti inspired multimodal ingestion, batch analysis, source tracing, and descriptive pattern analysis; no supplied TattvaDrishti source code or weights were copied. Third-party dependencies and model licensing are described in the README.

## Challenge evidence

### Best Open-Source AI Project

- Open-weight AI component and role: Gemma 4 extracts structured claims and reviews bounded ambiguous comparisons; an explicit Ollama provider supports local inference with gemma3:4b by default. There is no silent provider fallback.
- Integration: https://github.com/shoaib2000857/PromiseTrap/blob/main/apps/api/app/gemma.py and https://github.com/shoaib2000857/PromiseTrap/blob/main/apps/api/app/ollama.py
- Agent Skill Open Standard: not applicable; this entry is an application and original comparison engine.
- Original harness: https://github.com/shoaib2000857/PromiseTrap/tree/main/packages/promisegraph - normalization, scope-aware matching, financial calculations, condition dependencies, quotation checks, stable findings, and evidence provenance. Engine tests run without model credentials.

### Best Use of Gemma 4

- Model: gemma-4-26b-a4b-it through the Gemini API using the official Google GenAI Python SDK. Alternative supported Gemma model: gemma-4-31b-it. No Gemini-model substitution.
- Integration: https://github.com/shoaib2000857/PromiseTrap/blob/main/apps/api/app/gemma.py
- Multimodal value: direct image inputs and rendered PDF pages allow extraction from visual source material rather than relying solely on pasted text. Structured claims feed explainable comparisons and source-linked review.
- Actual validation: a real run completed on 12 October 2026 at 14:53 IST, processing three fictional internship PNG sources and extracting six claims. PromiseGraph produced three findings. The result is actual model output, not authored fixture extraction: https://github.com/shoaib2000857/PromiseTrap/blob/main/docs/live-gemma-internship.json
- Limitation: image-only quotations are approximate and require visual review. One fictional scenario does not establish general accuracy or source authenticity.

## Current status

- What works: local original-file ingestion, persistence, explicit providers, structured extraction, comparison, evidence graph, analyst review, Promise Journey, Reality Calculator, conditions, PromiseLab, clarification drafts, receipts, and PDF/Markdown/JSON export. 77 engine/API tests passed; TypeScript checks and production builds passed. The frontend is publicly deployed.
- Demo: follow the public README to start the Python API and Next.js. Load the fictional image scenario and run Gemma for actual extraction. The authored example is explicitly labeled and does not claim model inference.
- Known limitations: hosted site is frontend only; full investigations run locally. Local single-user persistence lacks authentication and a production job queue. Image evidence needs review. No public sharing, safe URL ingestion, or general accuracy claim. Video is pending.
- Next improvements: broader real-model evaluation, authenticated deployment, durable worker infrastructure, and candidate recall improvements.

## Submission checklist

- [x] Project repository is public and links work.
- [x] Required challenge evidence is included.
- [x] Project uses an open-source license where required by the challenge.
- [x] Work and reused materials are represented honestly.
- [x] No API keys, tokens, passwords, or private data are included.
- [x] The team confirmed that the organizer-authorized build window had started; final submission will follow the announced deadline and process.

Prepared submission details only. The final organizer PR and separate MLH platform entry have not been submitted.

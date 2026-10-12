# PromiseTrap

## Team / attendee

- Team name (if applicable): PromiseTrap — confirm team name.
- Members and GitHub usernames: To be completed by the team.
- Profile links (optional): To be completed.

## Challenge

- [x] Best Open-Source AI Project
- [x] Best Use of Gemma 4

Intent to enter both; final eligibility and live model evidence require confirmation.

## Project links

- Public GitHub repository: Connected application branch https://github.com/shoaib2000857/Hacktoberfest-2026-NIAT-KKH/tree/promisetrap — public access/release commit still needs verification.
- Open-source license (link to the license file): MIT, `LICENSE`; public source link must reference the published release commit.

## Problem and solution

Students and applicants compare promises in advertisements with details in forms and offer letters. PromiseTrap accepts multiple documents, extracts typed claims with Gemma 4, checks scope-aware discrepancies with PromiseGraph, and returns traceable findings, side-by-side evidence, provenance, version comparisons, analyst reviews, and downloadable reports.

## Approach and technologies

Next.js, TypeScript, React Flow, Lucide; Python, FastAPI, Pydantic, SQLite, PyMuPDF, Pillow, ReportLab; official Google GenAI SDK. Original PromiseGraph comparison engine. Synthetic test evidence is authored and labeled. TattvaDrishti supplied conceptual inspiration only; no code was copied. Codex-assisted enhancements to the existing PromiseTrap application on `promisetrap`, preserving its architecture and original features. Add team-specific contributions and actual event timing before submission.

## Challenge evidence

### Best Open-Source AI Project

- Open-source/open-weight AI component and its role: Gemma 4 for multimodal extraction and semantic comparison. Separate official model license linked in README.
- Code link showing the integration: `apps/api/app/gemma.py`; public source link must reference the published release commit.
- Agent Skill Open Standard compliance (if applicable): Not applicable.
- Original harness implementation or meaningful changes (if applicable): `packages/promisegraph/src/promisegraph/engine.py`, including normalization, candidate matching, scope checks, discrepancy rules, quote validation and provenance.

### Best Use of Gemma 4

- Gemma 4 model identifier and Gemini API integration: `gemma-4-26b-a4b-it` via official `google-genai` SDK. Live access still must be verified.
- Code link showing the integration: `apps/api/app/gemma.py`; public source link must reference the published release commit.
- Input and useful output; multimodal value where applicable: Images/PDF pages and text → structured source-linked claims → original comparison rules and evidence-backed investigation. Attach actual live image extraction demo before submitting.

## Current status

- What works: Local ingestion, persistence, engine comparisons, graph data, review, timeline classification, PDF/Markdown/JSON exports; frontend typechecks/builds; deterministic calculator, Journey, FinePrint/conditions, receipts, eligibility, isolated PromiseLab and offline clarification are integrated. Chrome checks cover Evidence Lens, calculator, PromiseLab and graph, including a mobile viewport.
- Known limitations / incomplete features: No current-host live Gemma inference without a key; public visibility/release links still require verification; image-only quotes require visual verification; local single-user app; URL ingestion and sharing deferred.
- What you would improve next: Live multimodal evaluation, semantic candidate retrieval, authenticated deployment.

## Submission checklist

- [ ] Project repository is public and links work.
- [ ] Required challenge evidence is included.
- [x] Project uses an open-source license where required by the challenge.
- [x] Work and reused materials are represented honestly.
- [ ] No API keys, tokens, passwords, or private data are included. Recheck the published commit.
- [ ] I followed the organizers' build window and submission instructions. Team to attest before submission.

Draft follows the headings in the [organizer template](https://github.com/niat-KKH/Hacktoberfest-2026-NIAT-KKH/blob/main/SUBMISSION_TEMPLATE.md). It is incomplete and has not been submitted.


## Enhancement release evidence

- See [release report](release-report.md), [evaluation](evaluation.md), [recorded offline fixture results](evaluation-results.json), [demo script](demo-script.md) and [screenshots](screenshots/).
- Original modules: `packages/promisegraph/src/promisegraph/advanced/`, with API compatibility bridge `extensions.py`. ScopeGuard, financial calculations and isolated simulations operate without model credentials.
- Dedicated real multimodal validation: `scripts/validate_gemma.py`; current host has no configured key. Authored/mocked tests cannot establish the Gemma prize requirement.
- Organizer main branch contains submission records; the application remains on the team's separate application branch. Do not merge application code into the organizer submission repository. The organizer PR and MLH form are separate operations and neither has been submitted here.
- Intent is to target both categories. Confirm whether simultaneous category entry is allowed, official build window/deadline, exact current MLH form and demo timing with organizers. Markdown challenge links were checked against the actual `Gemma_4_Challenge.pdf`, `Open_Source_AI_Challenge.pdf` and `Submission_Guide.pdf`; the guide includes an older platform URL, so do not assume it is the current form.

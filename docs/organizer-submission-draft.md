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

- Public GitHub repository: Pending publication.
- Open-source license (link to the license file): MIT, `LICENSE`; public link pending.

## Problem and solution

Students and applicants compare promises in advertisements with details in forms and offer letters. PromiseTrap accepts multiple documents, extracts typed claims with Gemma 4, checks scope-aware discrepancies with PromiseGraph, and returns traceable findings, side-by-side evidence, provenance, version comparisons, analyst reviews, and downloadable reports.

## Approach and technologies

Next.js, TypeScript, React Flow, Lucide; Python, FastAPI, Pydantic, SQLite, PyMuPDF, Pillow, ReportLab; official Google GenAI SDK. Original PromiseGraph comparison engine. Synthetic test evidence is authored and labeled. TattvaDrishti supplied conceptual inspiration only; no code was copied. Significant Codex-assisted engineering and design in an initially empty workspace. Add team-specific contributions and actual event timing before submission.

## Challenge evidence

### Best Open-Source AI Project

- Open-source/open-weight AI component and its role: Gemma 4 for multimodal extraction and semantic comparison. Separate official model license linked in README.
- Code link showing the integration: `apps/api/app/gemma.py`; public link pending.
- Agent Skill Open Standard compliance (if applicable): Not applicable.
- Original harness implementation or meaningful changes (if applicable): `packages/promisegraph/src/promisegraph/engine.py`, including normalization, candidate matching, scope checks, discrepancy rules, quote validation and provenance.

### Best Use of Gemma 4

- Gemma 4 model identifier and Gemini API integration: `gemma-4-26b-a4b-it` via official `google-genai` SDK. Live access still must be verified.
- Code link showing the integration: `apps/api/app/gemma.py`; public link pending.
- Input and useful output; multimodal value where applicable: Images/PDF pages and text → structured source-linked claims → original comparison rules and evidence-backed investigation. Attach actual live image extraction demo before submitting.

## Current status

- What works: Local ingestion, persistence, engine comparisons, graph data, review, timeline classification, PDF/Markdown/JSON exports; frontend compiles successfully.
- Known limitations / incomplete features: No live inference verified without a key, no browser QA, no public repository; image-only quotes require visual verification; local single-user app; URL ingestion and sharing deferred.
- What you would improve next: Live evaluation, browser verification, semantic candidate retrieval, authenticated deployment.

## Submission checklist

- [ ] Project repository is public and links work.
- [ ] Required challenge evidence is included.
- [x] Project uses an open-source license where required by the challenge.
- [x] Work and reused materials are represented honestly.
- [ ] No API keys, tokens, passwords, or private data are included. Recheck the published commit.
- [ ] I followed the organizers' build window and submission instructions. Team to attest before submission.

Draft follows the headings in the [organizer template](https://github.com/niat-KKH/Hacktoberfest-2026-NIAT-KKH/blob/main/SUBMISSION_TEMPLATE.md). It is incomplete and has not been submitted.

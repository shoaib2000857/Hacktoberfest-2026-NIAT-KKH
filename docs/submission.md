# Submission preparation — not submitted

Project: **PromiseTrap**  
Tagline: **Every promise deserves evidence.**  
Tracks: Best Use of Gemma 4; Best Open-Source AI Project

## Description draft

PromiseTrap is a multimodal evidence workspace for investigating differences between advertisements and the terms behind them. It preserves original sources, uses Gemma 4 for structured claim extraction and semantic review, and runs an original open-source PromiseGraph engine for scope-aware comparisons, quote validation, drift detection, and provenance. Users inspect side-by-side evidence, review findings, explore claim graphs and export an investigation dossier. It investigates claims without accusing people or producing unsupported scam probabilities.

## Original contribution

Independently installable PromiseGraph package: claim normalization, indexed comparable-pair matching, scope/condition checks, numeric/guarantee discrepancies, dated-version classification, quotation verification, and evidence graph construction. Custom editorial frontend and end-to-end local ingestion, persistent analysis, review and reporting.

## Gemma evidence to attach

- Actual model identifier and analysis timestamp from a successful live run.
- Screenshot/video of image evidence being ingested and structured claims extracted.
- Real side-by-side sourced result; explain image-only localization limitations.
- SDK adapter path: `apps/api/app/gemma.py`.

## Open-source evidence to attach

- Application branch URL: https://github.com/shoaib2000857/Hacktoberfest-2026-NIAT-KKH/tree/promisetrap — verify public visibility and the published enhancement commit before entry.
- MIT license at repository root and documented separate model terms.
- Package source, negative-case tests, reproducible setup and real working demo.
- Explain TattvaDrishti inspiration; no supplied TattvaDrishti code was copied.

## Submission blockers

Live multimodal model verification, confirmed public release links, team names, demo recording/link, and final event-template completion. Browser screenshots and local validation are now recorded; record actual development timing honestly and confirm organizer-specific eligibility. No entry has been submitted.

Official platform: https://www.mlh.com/events/hacktoberfest-hack-day-hyderabad-x-niat/submissions/new  
Organizer repository: https://github.com/niat-KKH/Hacktoberfest-2026-NIAT-KKH

The organizer PR and MLH platform entry are separate. Copy their current `SUBMISSION_TEMPLATE.md` before submitting. Only publish or submit after explicit user authorization.


## Enhancement release evidence

- See [release report](release-report.md), [evaluation](evaluation.md), [recorded offline fixture results](evaluation-results.json), [demo script](demo-script.md) and [screenshots](screenshots/).
- Original modules: `packages/promisegraph/src/promisegraph/advanced/`, with API compatibility bridge `extensions.py`. ScopeGuard, financial calculations and isolated simulations operate without model credentials.
- Dedicated real multimodal validation: `scripts/validate_gemma.py`; current host has no configured key. Authored/mocked tests cannot establish the Gemma prize requirement.
- Organizer main branch contains submission records; the application remains on the team's separate application branch. Do not merge application code into the organizer submission repository. The organizer PR and MLH form are separate operations and neither has been submitted here.
- Intent is to target both categories. Confirm whether simultaneous category entry is allowed, official build window/deadline, exact current MLH form and demo timing with organizers. Markdown challenge links were checked against the actual `Gemma_4_Challenge.pdf`, `Open_Source_AI_Challenge.pdf` and `Submission_Guide.pdf`; the guide includes an older platform URL, so do not assume it is the current form.

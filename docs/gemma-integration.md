# Gemma integration

Adapter: `apps/api/app/gemma.py`. Provider: official `google-genai` Python SDK. Default model `gemma-4-26b-a4b-it`, alternative `gemma-4-31b-it`. Both are explicitly allowlisted, with no fallback model.

Confirmed against [Google's current hosted Gemma documentation](https://ai.google.dev/gemma/docs/core/gemma_on_gemini_api): `client.models.generate_content`, `types.GenerateContentConfig(system_instruction=...)`, text and image inputs. The SDK installed in the initial validation was 2.29.0. Image bytes use `types.Part.from_bytes`; PDFs are rendered page-by-page with PyMuPDF and sent with extracted text. API access is account-dependent and must be verified live.

Extraction prompt v1 is the versioned `SYSTEM` string and schema instructions in this adapter. Output uses JSON instructions rather than assuming native structured-output availability. Legitimate fenced JSON is unwrapped, parsed, and validated with Pydantic. One repair attempt re-extracts from the same evidence. Source IDs cannot be invented. Stable claim IDs are assigned by the server.

The semantic prompt v1 compares typed candidate claims and explicitly checks scope, audience, stage, conditions and dates. Pydantic restricts the output vocabulary and requires explanation and limitations. The model never overrides text-verification flags.

Model requests have a 60-second HTTP timeout, up to three transient attempts with exponential backoff, and bounded output. Input and per-source claims are limited. Stages show real processing activity without fake percentages. Partial extraction failures preserve successful-source results and explicit errors. Provider exception details are sanitized so credentials and request payloads are not displayed or persisted.

Live smoke test: `python scripts/smoke_gemma.py`. Do not call a mock or the authored example a successful live Gemma run. Successful key configuration alone does not establish model availability. Reanalysis of the authored example uses live source documents and retains the explicit example label; model provenance records the actual provider model.

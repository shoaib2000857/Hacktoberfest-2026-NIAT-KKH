# Security and privacy

This repository is a local single-user development application. Both servers must bind to `127.0.0.1`. There is no authentication, encryption at rest or hardened public upload endpoint. Do not expose either service on a public interface without adding authorization, origin validation, rate limits and private object storage.

Uploaded material is untrusted. Never treat document-embedded instructions as user/system instructions. Model outputs are schema-validated; citations must refer to known sources and actual quotes. No fake image coordinates are accepted.

Files are checked for supported content and limited size. Image bytes must match MIME and pass Pillow validation. PDFs are parsed with page and text limits. Original bytes are stored under server-assigned UUIDs rather than user filenames. Delete routes only remove source UUID files within the configured data directory.

API keys are backend-only and ignored by Git. Provider errors are sanitized. Source content is sent to Google during a live analysis. Exported reports contain original quotations; users should review them before sharing. Application code adds no analytics.

URL ingestion is not implemented, avoiding an unverified SSRF boundary. Before enabling it, validate DNS and every redirect, disallow private/reserved destinations, and pin the validated destination to prevent DNS rebinding.

Report security concerns privately to the repository maintainers once a public repository exists; do not publish real personal evidence in issues.

# Security

## Data classification

Demo corpora are synthetic. Do not upload real PHI, PII, credentials, or customer documents.

## Synthetic demo data policy

Medical-style files are labeled SYNTHETIC and are not medical advice. Architecture docs describe fictional systems only.

## Secret handling

- Store secrets in `.env` (never commit)
- Use `.env.example` with sanitized placeholders only
- Validate required variables at startup without logging values
- Keep API keys out of frontend bundles

## Upload validation

- Allowed types: PDF, Markdown, plain text
- Max size from `MAX_UPLOAD_MB`
- Filenames sanitized to prevent path traversal
- Files stored under `DOCUMENT_STORAGE_PATH` per document ID

## Logging policy

- Structured logs without secrets
- Do not log full document bodies by default
- Do not log stack traces to API clients

## Local model mode

Default configuration uses Ollama on the host. No hosted LLM key is required for the standard demo.

## Hosted provider risk

Optional OpenAI or other hosted providers send prompts outside the local environment. Enable only with explicit configuration and key management.

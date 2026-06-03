# CLAUDE.md

This file provides project guidance for AI coding assistants working on the RAGOps Platform.

## Project Mission

Build a production style RAGOps Platform that demonstrates senior level AI software development, architecture judgment, test discipline, and deployment readiness.

The platform must go beyond a simple document chatbot. It must ingest documents, build searchable indexes, compare retrieval strategies, generate citation backed answers, evaluate answer quality, and expose the internal RAG pipeline clearly enough for senior engineers, architects, and hiring managers to inspect.

## Target Audience

This project is intended for a public portfolio at brianekane.com and should demonstrate readiness for AI software development roles, including senior software engineer, AI engineer, agentic AI engineer, and AI solutions architect roles.

## Core Principles

1. Prefer clear architecture over clever code.
2. Prefer deterministic, testable logic over hidden magic.
3. Prefer explicit contracts between frontend, backend, and AI services.
4. Prefer local, privacy conscious defaults.
5. Prefer citation backed answers over unsupported generated text.
6. Prefer measurable RAG quality over subjective demos.
7. Prefer small composable modules over large files.
8. Do not introduce unnecessary dependencies.
9. Do not hide failures from the user.
10. Do not fabricate answers when source evidence is insufficient.

## Package and runtime management

Use Yarn for all JavaScript and TypeScript package management. Do not use NPM commands for installation, scripts, lockfiles, or dependency updates.

Use UV for all Python package management. Do not use Pip commands for installation, dependency locking, virtual environment management, or project setup.

Python runtime should use Python 3.12 unless there is a clear technical reason to move to Python 3.13. Python 3.12 is preferred because it has broad library compatibility while still being modern and production appropriate.

Expected runtime choices:

- Frontend package manager: Yarn
- Backend package manager: UV
- Python version: 3.12
- Node version: current LTS
- Backend framework: FastAPI
- Frontend framework: Next.js with React and TypeScript

When adding dependencies:

- Add frontend dependencies with Yarn.
- Add backend dependencies with UV.
- Keep dependency changes minimal and explain why the dependency is needed.
- Do not add global installs.
- Do not mix lockfile systems.
- Do not create package-lock.json.
- Do not create requirements.txt unless explicitly requested for compatibility documentation.

## Environment variable management

Any change that adds, removes, or renames an environment variable must also update the example environment file.

The example environment file must use sanitized placeholder values. Show the beginning of the value and replace the remainder with asterisks.

Examples:

```env
DATABASE_URL=postg********
OPENAI_API_KEY=sk-p********
OLLAMA_BASE_URL=http********
JWT_SECRET=jwt_********
```

Rules:

1. Never commit real secrets.
2. Never expose tokens, keys, passwords, private endpoints, or credentials.
3. If a new secret is required, update the example environment file in the same change.
4. If a variable is optional, mark it clearly in documentation.
5. If a variable is required, backend startup validation must identify it clearly.
6. Keep local model configuration separate from hosted model configuration.
7. Prefer local Ollama defaults where practical.

## Required test coverage

Maintain a minimum of 90 percent test coverage for logic and UI.

Backend requirements:

- Unit tests for chunking logic.
- Unit tests for document parsing adapters.
- Unit tests for retrieval strategy selection.
- Unit tests for citation validation.
- Unit tests for groundedness scoring helpers.
- Unit tests for evaluation metric calculations.
- Integration tests for ingestion endpoints.
- Integration tests for query endpoints.
- Integration tests for health checks.
- Tests for error cases and insufficient evidence behavior.

Frontend requirements:

- Unit tests for reusable UI components.
- Tests for query input behavior.
- Tests for evidence panel rendering.
- Tests for evaluation dashboard rendering.
- Tests for loading, empty, and error states.
- Tests for API client behavior.
- Accessibility oriented tests where practical.

Coverage rules:

- Do not lower coverage thresholds to pass builds.
- Do not exclude meaningful business logic from coverage.
- Do not add superficial tests that only inflate coverage.
- Prefer meaningful assertions around behavior.
- Every bug fix should include a regression test unless impractical.

## Code quality standards

Backend:

- Use FastAPI with typed request and response models.
- Use Pydantic models for API contracts.
- Keep domain logic outside route handlers.
- Keep RAG pipeline logic in clearly named service modules.
- Use dependency injection for vector store, embedding provider, LLM provider, and reranker provider.
- Make retrieval strategies swappable.
- Make chunking strategies configurable.
- Make evaluation logic deterministic where possible.
- Avoid provider lock in.

Frontend:

- Use TypeScript.
- Use strongly typed API clients.
- Keep page components thin.
- Move complex UI logic into hooks or utility modules.
- Use accessible form controls.
- Show loading states, error states, and empty states.
- Avoid hiding RAG details behind a black box UI.

General:

- Avoid files that become too large.
- Prefer named functions over anonymous complex callbacks.
- Prefer explicit error handling.
- Prefer logs that explain what failed without leaking sensitive data.
- Do not introduce emojis.
- Do not use em dash characters.
- Do not use double hyphen punctuation as a substitute for an em dash in prose.

## RAG implementation expectations

The system must include a transparent RAG pipeline:

1. Document upload or document registration.
2. Document parsing.
3. Text normalization.
4. Chunking.
5. Metadata extraction.
6. Embedding generation.
7. Vector storage.
8. Retrieval.
9. Optional hybrid retrieval.
10. Optional reranking.
11. Context assembly.
12. Answer generation.
13. Citation validation.
14. Groundedness evaluation.
15. User visible answer with sources.

Do not build a generic chat app and call it RAG. The project must expose how retrieval works and how answer quality is measured.

## Required retrieval strategies

Implement the retrieval system so these strategies can be compared:

1. Basic vector similarity search.
2. Metadata filtered vector search.
3. Hybrid keyword plus vector retrieval.
4. Multi query retrieval.
5. Reranked retrieval.

The strategy interface should make it possible to add additional strategies later without changing API contracts.

Each retrieval result should include:

- Source document id.
- Source filename.
- Page number when available.
- Chunk id.
- Chunk text.
- Similarity score when available.
- Reranker score when available.
- Retrieval strategy name.
- Token count estimate when available.

## Required evaluation features

The platform must include an evaluation dashboard with at least these concepts:

- Answer relevance.
- Context relevance.
- Groundedness.
- Citation coverage.
- Retrieval latency.
- Generation latency.
- Total request latency.
- Number of retrieved chunks.
- Number of cited chunks.
- Insufficient evidence rate.

Evaluation logic should be separated from UI rendering and from LLM provider code.

## Required UI sections

The application should include these user facing sections:

1. Overview page.
2. Document ingestion page.
3. Ask page.
4. Evidence panel.
5. Evaluation dashboard.
6. Retrieval strategy comparison page.
7. Settings page.
8. Architecture or about page suitable for portfolio review.

The UI should help a reviewer understand the engineering work without reading every source file.

## Security and privacy requirements

- Use synthetic data for demo content.
- Do not include real PHI, PII, credentials, tokens, or customer data.
- Validate uploaded file types.
- Limit upload size.
- Sanitize filenames.
- Do not expose server stack traces to users.
- Do not log secrets.
- Do not log full documents by default.
- Provide clear local model configuration.
- Document when hosted model APIs are optional.

## Documentation requirements

Maintain high quality documentation because this project is for portfolio review.

Required documents:

- README.md
- REQUIREMENTS.md
- ARCHITECTURE.md
- API.md
- EVALUATION.md
- SECURITY.md
- .env.example

The README must explain:

- What the project does.
- Why it is more than a simple chatbot.
- Key architecture decisions.
- How to run locally.
- How to run tests.
- How to inspect RAG evidence.
- How to interpret evaluation metrics.

## Git and change discipline

Before making a major change:

1. Inspect existing structure.
2. Identify impacted files.
3. Make the smallest coherent change.
4. Update tests.
5. Update documentation.
6. Update sanitized environment examples if needed.

Do not rewrite unrelated areas of the project.

## Definition of done

A feature is not done until:

1. The implementation works.
2. Backend tests pass.
3. Frontend tests pass.
4. Coverage remains at or above 90 percent for logic and UI.
5. Relevant docs are updated.
6. New environment variables are reflected in the sanitized example environment file.
7. Errors are handled clearly.
8. The user experience exposes RAG evidence where appropriate.
9. No real secrets are present.
10. No emojis, em dash characters, or double hyphen prose punctuation are introduced.

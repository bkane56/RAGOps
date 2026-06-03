# RAGOps Platform Requirements

## 1. Project overview

RAGOps Platform is a production style retrieval augmented generation system built for a professional portfolio. The goal is to demonstrate practical AI engineering skills, strong software architecture, measurable RAG quality, privacy conscious design, test discipline, and deployment readiness.

This must not be a simple document chatbot. The platform must show the complete lifecycle of a RAG system, including document ingestion, chunking, embeddings, vector storage, retrieval strategy comparison, reranking, answer generation, citation validation, evaluation metrics, and user visible observability.

The project should be suitable for review by senior engineers, principal engineers, software architects, AI engineers, and hiring managers.

## 2. Primary goals

1. Build a polished portfolio grade RAGOps application.
2. Demonstrate modern full stack AI engineering.
3. Show transparent RAG internals, not just generated answers.
4. Compare multiple retrieval strategies.
5. Score answers for quality and groundedness.
6. Require citation backed responses.
7. Support privacy conscious local model defaults.
8. Include strong automated tests with at least 90 percent coverage for logic and UI.
9. Include documentation that explains architecture and tradeoffs clearly.
10. Make the system easy to run locally and easy to evaluate.

## 3. Non goals

1. Do not build a generic chatbot only.
2. Do not build a medical diagnostic tool.
3. Do not include real PHI, PII, customer data, credentials, or private documents.
4. Do not require hosted LLM APIs for the default local demo.
5. Do not hide retrieval details from the reviewer.
6. Do not make the architecture depend on a single LLM vendor.
7. Do not skip testing for AI related logic.
8. Do not commit secrets.

## 4. Recommended technology stack

### 4.1 Frontend

- Next.js
- React
- TypeScript
- Tailwind for CSS
- Yarn for package management
- React Testing Library for UI tests
- Playwright or equivalent for end to end tests if added
- Accessible component patterns
- Strongly typed API client

### 4.2 Backend

- Python 3.12
- FastAPI
- Pydantic
- UV for package management
- Pytest for tests
- Coverage tooling with minimum threshold of 90 percent
- Structured logging
- Provider interfaces for embeddings, LLMs, vector stores, and rerankers

### 4.3 Data and retrieval

#### Database Recommendation

The primary hosted database should be Supabase Postgres with pgvector enabled.

Use Postgres for application data, document metadata, chunk metadata, RAG run logs, retrieval results, evaluation scores, and audit logs.

Use pgvector for document chunk embeddings.

Local development should use Docker Compose with Postgres and pgvector so the project can run without requiring a hosted database.

The architecture should keep vector storage behind a repository or adapter interface so Qdrant or another vector database can be added later for comparison experiments.

Preferred options:

- PostgreSQL(Supabase) with pgvector for production style persistence
- Qdrant as an acceptable alternative vector store
- SQLite only for lightweight local metadata if needed

The design should allow the vector store implementation to be swapped through an interface.

### 4.4 Model providers

The system should support local first configuration.

Required provider types:

- Local LLM provider using Ollama
- Local embedding provider when practical
- Optional hosted LLM provider through configuration
- Optional hosted embedding provider through configuration

Hosted provider support must be optional and must not be required for the default demo.

## 5. Package and runtime management

Use Yarn for JavaScript and TypeScript package management. Do not use NPM.

Use UV for Python package management. Do not use Pip.

Use Python 3.12 as the default runtime because it has strong ecosystem support while remaining modern and production appropriate.

Expected project commands should be documented using Yarn and UV only.

Examples of acceptable command intent:

- Use Yarn to install frontend dependencies.
- Use Yarn to run frontend tests.
- Use Yarn to run frontend development server.
- Use UV to sync backend dependencies.
- Use UV to run backend tests.
- Use UV to run the FastAPI application.

Do not create or depend on package-lock.json.

Do not create or depend on Pip based setup instructions unless explicitly requested for compatibility notes.

## 6. Environment variable requirements

The project must include a sanitized example environment file.

Any code change that adds, removes, or renames an environment variable must update the sanitized example file in the same change.

Sanitized values must show the first few characters and replace the rest with asterisks.

Example:

```env
DATABASE_URL=postg********
VECTOR_STORE_URL=http********
OLLAMA_BASE_URL=http********
OPENAI_API_KEY=sk-p********
APP_SECRET=app_********
```

Required environment categories:

### 6.1 Application

- APP_ENV
- APP_NAME
- APP_BASE_URL
- API_BASE_URL
- LOG_LEVEL

### 6.2 Backend

- DATABASE_URL
- VECTOR_STORE_PROVIDER
- VECTOR_STORE_URL
- DOCUMENT_STORAGE_PATH
- MAX_UPLOAD_MB

### 6.3 Local model settings

- OLLAMA_BASE_URL
- OLLAMA_CHAT_MODEL
- OLLAMA_EMBEDDING_MODEL

### 6.4 Optional hosted model settings

- HOSTED_LLM_PROVIDER
- HOSTED_LLM_MODEL
- HOSTED_EMBEDDING_MODEL
- OPENAI_API_KEY or equivalent provider key when used

### 6.5 Evaluation settings

- EVAL_ENABLED
- EVAL_SAMPLE_SET_PATH
- EVAL_MAX_CASES

Rules:

1. Never include real secrets.
2. Validate required environment variables at startup.
3. Error messages should identify missing variables without exposing values.
4. Documentation must clearly mark optional variables.
5. The default local demo should work without hosted LLM keys when local Ollama is configured.

## 7. System architecture

The project should use a clean layered architecture.

### 7.1 Frontend layers

1. App routes and pages.
2. Feature components.
3. Shared UI components.
4. Hooks.
5. API client.
6. Types.
7. Test utilities.

Suggested frontend folders:

```txt
frontend/
  app/
  components/
  features/
    documents/
    ask/
    evidence/
    evaluation/
    strategies/
    settings/
  lib/
    api/
    types/
    utils/
  tests/
```

### 7.2 Backend layers

1. API routes.
2. Request and response schemas.
3. Application services.
4. Domain models.
5. Provider interfaces.
6. Infrastructure adapters.
7. Evaluation services.
8. Test fixtures.

Suggested backend folders:

```txt
backend/
  app/
    api/
      routes/
    core/
      config/
      logging/
      errors/
    domain/
      documents/
      retrieval/
      generation/
      evaluation/
    services/
      ingestion/
      chunking/
      embeddings/
      retrieval/
      reranking/
      generation/
      citation_validation/
      evaluation/
    providers/
      llm/
      embeddings/
      vector_store/
      document_store/
    infrastructure/
      database/
      vector_stores/
      file_storage/
    tests/
```

### 7.3 Cross cutting concerns

- Configuration validation.
- Structured logging.
- Error handling.
- Test fixtures.
- Type safety.
- Security checks.
- Metrics collection.

## 8. Core user journeys

### 8.1 Document ingestion

As a user, I can upload or register documents so the platform can parse, chunk, embed, and index them.

Requirements:

1. Accept PDF, markdown, and plain text initially.
2. Validate file type.
3. Validate file size.
4. Sanitize filenames.
5. Extract text and metadata.
6. Preserve source document id.
7. Preserve page number when available.
8. Store ingestion status.
9. Show ingestion progress or status.
10. Show parsing errors clearly.
11. Allow reindexing a document.
12. Allow deleting a document and its chunks.

### 8.2 Chunk inspection

As a reviewer, I can inspect how documents were chunked.

Requirements:

1. Show chunk id.
2. Show source document.
3. Show page number when available.
4. Show chunk text.
5. Show token count estimate.
6. Show chunking strategy.
7. Show created timestamp.
8. Allow filtering by document.

### 8.3 Asking questions

As a user, I can ask a question and receive a citation backed answer.

Requirements:

1. User enters a natural language question.
2. User selects a retrieval strategy.
3. User can optionally select document filters.
4. Backend retrieves relevant chunks.
5. Backend optionally reranks retrieved chunks.
6. Backend assembles context.
7. LLM generates an answer using only the provided context.
8. Answer includes citations.
9. If evidence is insufficient, the answer must say so clearly.
10. UI shows answer, citations, retrieved evidence, and evaluation metrics.

### 8.4 Evidence inspection

As a reviewer, I can inspect the evidence used to answer a question.

Requirements:

1. Show each retrieved chunk.
2. Show source document name.
3. Show page number when available.
4. Show similarity score when available.
5. Show reranker score when available.
6. Show retrieval strategy.
7. Highlight cited chunks.
8. Allow expanding and collapsing chunk text.
9. Allow copying citation details.

### 8.5 Strategy comparison

As a reviewer, I can compare retrieval strategies for the same question.

Required strategies:

1. Basic vector retrieval.
2. Metadata filtered vector retrieval.
3. Hybrid keyword plus vector retrieval.
4. Multi query retrieval.
5. Reranked retrieval.

Comparison output:

1. Strategy name.
2. Retrieved chunks.
3. Answer.
4. Citation coverage.
5. Groundedness score.
6. Answer relevance score.
7. Context relevance score.
8. Retrieval latency.
9. Generation latency.
10. Total latency.

### 8.6 Evaluation dashboard

As a reviewer, I can see whether the RAG system is working well.

Dashboard requirements:

1. Show summary metrics.
2. Show latest queries.
3. Show average groundedness.
4. Show average answer relevance.
5. Show average context relevance.
6. Show insufficient evidence rate.
7. Show citation coverage rate.
8. Show latency trends.
9. Show per strategy comparison.
10. Show failed or low confidence examples.

## 9. RAG pipeline requirements

### 9.1 Document parsing

The parsing layer must convert supported files into normalized text and metadata.

Required metadata:

- Document id.
- Filename.
- File type.
- Page number when available.
- Section heading when available.
- Created timestamp.
- Content hash.

### 9.2 Chunking

Support configurable chunking.

Minimum required chunking strategy:

- Recursive text chunking with configurable chunk size and overlap.

Recommended additional strategies:

- Markdown heading aware chunking.
- Page aware PDF chunking.
- Semantic chunking if practical.

Chunk records must include:

- Chunk id.
- Document id.
- Chunk text.
- Metadata.
- Token count estimate.
- Chunking strategy.
- Content hash.

### 9.3 Embeddings

Embedding generation must be abstracted behind a provider interface.

Requirements:

1. Generate embeddings for chunks.
2. Store embedding model name.
3. Store embedding dimension when known.
4. Avoid recomputing embeddings when content hash has not changed.
5. Support local and optional hosted embedding providers.
6. Handle provider failure clearly.

### 9.4 Vector storage

Vector storage must be abstracted behind a provider interface.

Requirements:

1. Upsert chunk embeddings.
2. Search by query embedding.
3. Filter by metadata.
4. Delete by document id.
5. Return scores and metadata.
6. Support future replacement of vector database.

### 9.5 Retrieval

Implement retrieval as strategy classes or strategy functions behind a stable interface.

Each retrieval strategy should accept:

- Query text.
- Top k value.
- Optional document filters.
- Optional metadata filters.
- Optional strategy specific settings.

Each retrieval strategy should return:

- Retrieved chunks.
- Scores.
- Strategy name.
- Timing information.

### 9.6 Reranking

Reranking should be optional and modular.

Requirements:

1. Accept retrieved chunks and query.
2. Return reordered chunks.
3. Include reranker score when available.
4. Support no reranker fallback.
5. Keep reranker provider separate from retrieval provider.

### 9.7 Context assembly

Context assembly should be deterministic and testable.

Requirements:

1. Use token budget limits.
2. Preserve citation identifiers.
3. Avoid duplicate chunks.
4. Prioritize higher scoring chunks.
5. Keep source metadata attached.
6. Produce a final context object used by generation.

### 9.8 Answer generation

The generation layer must instruct the model to answer only from retrieved context.

Requirements:

1. Use a controlled prompt template.
2. Include context with citation identifiers.
3. Require citations in the answer.
4. Instruct model to say when evidence is insufficient.
5. Return structured output when practical.
6. Include model provider and model name in response metadata.
7. Track generation latency.

### 9.9 Citation validation

Citation validation must run after generation.

Requirements:

1. Identify citations in answer text.
2. Verify cited chunk ids exist in retrieved context.
3. Compute citation coverage.
4. Flag unsupported answer segments when practical.
5. Mark answers invalid when citations are missing for factual claims.
6. Surface validation status in the UI.

### 9.10 Insufficient evidence behavior

The system must explicitly handle questions that cannot be answered from the available documents.

Requirements:

1. Return a clear insufficient evidence response.
2. Avoid guessing.
3. Show the closest retrieved chunks if useful.
4. Mark the answer as low confidence.
5. Include evaluation metadata explaining the failure mode.

## 10. Evaluation requirements

The evaluation system should support both single query evaluation and batch evaluation.

### 10.1 Required metrics

1. Answer relevance.
2. Context relevance.
3. Groundedness.
4. Citation coverage.
5. Retrieval latency.
6. Generation latency.
7. Total latency.
8. Retrieved chunk count.
9. Cited chunk count.
10. Insufficient evidence rate.

### 10.2 Evaluation dataset

Include a synthetic evaluation dataset.

Each evaluation case should include:

- Question.
- Expected answer summary.
- Expected source document ids or chunk ids when known.
- Expected behavior.
- Difficulty level.
- Category.

Categories should include:

1. Direct answer present in one chunk.
2. Answer requires multiple chunks.
3. Ambiguous question.
4. No supporting evidence.
5. Citation required.
6. Metadata filtered question.

### 10.3 Evaluation output

Batch evaluation should produce:

1. Per case results.
2. Aggregate metrics.
3. Strategy comparison.
4. Failed cases.
5. Exportable JSON report.
6. UI summary.

## 11. API requirements

The backend should expose clear API endpoints.

Suggested endpoints:

```txt
GET /health
GET /ready
POST /documents
GET /documents
GET /documents/{document_id}
DELETE /documents/{document_id}
POST /documents/{document_id}/reindex
GET /documents/{document_id}/chunks
POST /ask
POST /compare-strategies
GET /evaluations
POST /evaluations/run
GET /settings/runtime
```

API responses must be typed with Pydantic models.

Errors must use consistent structured error responses.

Do not expose stack traces to the frontend.

## 12. Frontend requirements

### 12.1 Overview page

The overview page should explain the platform and why it is more than a chatbot.

Must include:

1. RAG pipeline summary.
2. Current document count.
3. Current chunk count.
4. Available retrieval strategies.
5. Recent evaluation summary.

### 12.2 Documents page

Must include:

1. Upload area.
2. Document list.
3. Ingestion status.
4. Reindex action.
5. Delete action.
6. Chunk inspection link.

### 12.3 Ask page

Must include:

1. Question input.
2. Retrieval strategy selector.
3. Document filter selector when available.
4. Top k setting.
5. Submit button.
6. Answer area.
7. Citation list.
8. Evidence panel.
9. Evaluation summary.
10. Error and insufficient evidence states.

### 12.4 Evidence panel

Must include:

1. Retrieved chunk cards.
2. Source filename.
3. Page number when available.
4. Score display.
5. Citation status.
6. Expand and collapse behavior.

### 12.5 Strategy comparison page

Must include:

1. Shared question input.
2. Strategy selection.
3. Side by side or stacked comparison.
4. Answer per strategy.
5. Retrieved chunks per strategy.
6. Metrics per strategy.
7. Latency per strategy.

### 12.6 Evaluation dashboard

Must include:

1. Aggregate metric cards.
2. Results table.
3. Strategy comparison table.
4. Failed case list.
5. Low confidence answer list.
6. Export button if practical.

### 12.7 Settings page

Must include:

1. Runtime provider display.
2. LLM model display.
3. Embedding model display.
4. Vector store provider display.
5. Upload limits.
6. Environment validation status.

## 13. Testing requirements

Minimum test coverage is 90 percent for logic and UI.

### 13.1 Backend tests

Required tests:

1. Config validation tests.
2. Document parser tests.
3. Chunking tests.
4. Embedding provider interface tests using mocks.
5. Vector store interface tests using mocks or test container.
6. Retrieval strategy tests.
7. Reranking tests using mocks.
8. Context assembly tests.
9. Citation validation tests.
10. Evaluation metric tests.
11. Ingestion endpoint tests.
12. Ask endpoint tests.
13. Compare strategies endpoint tests.
14. Error handling tests.
15. Insufficient evidence behavior tests.

### 13.2 Frontend tests

Required tests:

1. Overview page rendering.
2. Documents page rendering.
3. Upload form behavior.
4. Ask form behavior.
5. Strategy selector behavior.
6. Answer rendering.
7. Citation rendering.
8. Evidence panel rendering.
9. Evaluation dashboard rendering.
10. Error states.
11. Empty states.
12. Loading states.
13. API client success and failure paths.

### 13.3 End to end tests

Recommended tests:

1. Upload a small document.
2. Ask a supported question.
3. Verify answer contains citations.
4. Verify evidence panel is populated.
5. Ask an unsupported question.
6. Verify insufficient evidence behavior.
7. Run strategy comparison.
8. Verify metrics are displayed.

## 14. Security and privacy requirements

1. Use synthetic demo documents only.
2. Do not include real PHI or PII.
3. Do not include real credentials.
4. Do not log full uploaded documents by default.
5. Validate upload type and size.
6. Sanitize filenames.
7. Store documents in a controlled path.
8. Avoid path traversal vulnerabilities.
9. Keep secrets out of frontend bundles.
10. Do not expose stack traces.
11. Add security documentation.
12. Add privacy conscious local model documentation.

## 15. Observability requirements

The system should collect enough metadata to explain RAG behavior.

Capture:

1. Query id.
2. Request timestamp.
3. Retrieval strategy.
4. Top k.
5. Document filters.
6. Retrieved chunk ids.
7. Scores.
8. Reranker scores.
9. Retrieval latency.
10. Generation latency.
11. Total latency.
12. Model provider.
13. Model name.
14. Evaluation metrics.
15. Citation validation status.

Logs must not leak secrets or full private document content.

## 16. Demo content requirements

Include synthetic demo content that makes the project easy to evaluate.

Recommended demo document sets:

### 16.1 Software architecture documents

- Architecture decision records.
- API design notes.
- Deployment notes.
- Incident review notes.
- Environment variable documentation.

### 16.2 Medical style synthetic documents

- Synthetic care policy document.
- Synthetic progress note structure guide.
- Synthetic CPT documentation summary.

These must be clearly labeled as synthetic and not medical advice.

### 16.3 Portfolio documents

Optional later phase:

- Resume summary.
- Project summaries.
- Public README content.

This can connect the platform to brianekane.com without duplicating the separate Digital Twin app.

## 17. Documentation requirements

Required files:

```txt
README.md
REQUIREMENTS.md
ARCHITECTURE.md
API.md
EVALUATION.md
SECURITY.md
.env.example
```

### 17.1 README requirements

The README must include:

1. Project summary.
2. Why this is more than a chatbot.
3. Architecture diagram or text diagram.
4. Feature list.
5. Tech stack.
6. Local setup using Yarn and UV.
7. Environment variable setup.
8. Test commands.
9. Coverage expectations.
10. Demo workflow.
11. Screenshots when available.
12. Known limitations.

### 17.2 ARCHITECTURE.md requirements

Must include:

1. System overview.
2. Frontend architecture.
3. Backend architecture.
4. RAG pipeline.
5. Provider abstraction design.
6. Vector store design.
7. Evaluation design.
8. Security and privacy considerations.
9. Deployment architecture.
10. Tradeoffs and future improvements.

### 17.3 EVALUATION.md requirements

Must include:

1. Evaluation philosophy.
2. Metrics definitions.
3. Test dataset format.
4. How to run evaluations.
5. How to interpret results.
6. Known limitations.

### 17.4 SECURITY.md requirements

Must include:

1. Data classification assumptions.
2. Synthetic demo data policy.
3. Secret handling.
4. Upload validation.
5. Logging policy.
6. Local model mode.
7. Hosted provider risk notes.

## 18. Deployment requirements

The project should support local development first and deployment later.

Recommended deployment shape:

- Frontend on Vercel.
- Backend on Render or Railway.
- Vector store on managed PostgreSQL with pgvector or Qdrant.
- Optional local Docker Compose for full local demo.

Docker Compose should include:

1. Backend service.
2. Frontend service if practical.
3. Database service.
4. Vector store service if separate.
5. Optional Ollama documentation for local model runtime.

Deployment documentation must explain which secrets are needed and how to sanitize the example environment file.

## 19. Acceptance criteria

The project is acceptable when:

1. A user can upload a supported document.
2. The system chunks and indexes the document.
3. A user can ask a question.
4. The answer includes citations.
5. Retrieved evidence is visible.
6. At least three retrieval strategies are implemented.
7. Strategy comparison is available.
8. Evaluation metrics are visible.
9. Unsupported questions produce insufficient evidence responses.
10. Backend logic is covered by meaningful tests.
11. Frontend UI is covered by meaningful tests.
12. Test coverage for logic and UI is at least 90 percent.
13. Environment variables are documented with sanitized examples.
14. README and architecture documentation are complete.
15. The system runs locally using Yarn and UV.
16. No NPM or Pip instructions are used.
17. No real secrets are present.
18. No emojis are present.
19. No em dash characters are present.
20. No double hyphen prose punctuation is present.

## 20. Suggested implementation phases

### Phase 1: Foundation

1. Create frontend and backend project structure.
2. Add Yarn and UV based setup.
3. Add config validation.
4. Add health endpoints.
5. Add base UI shell.
6. Add test tooling and coverage thresholds.

### Phase 2: Ingestion

1. Add document upload endpoint.
2. Add PDF, markdown, and text parsing.
3. Add chunking.
4. Add metadata storage.
5. Add document list UI.
6. Add chunk inspection UI.

### Phase 3: Basic RAG

1. Add embedding provider interface.
2. Add vector store provider interface.
3. Add basic vector retrieval.
4. Add answer generation.
5. Add citation formatting.
6. Add Ask UI.

### Phase 4: Evidence and validation

1. Add evidence panel.
2. Add citation validation.
3. Add insufficient evidence behavior.
4. Add query logging.
5. Add latency tracking.

### Phase 5: Strategy comparison

1. Add metadata filtered retrieval.
2. Add hybrid retrieval.
3. Add multi query retrieval.
4. Add reranked retrieval.
5. Add comparison API.
6. Add comparison UI.

### Phase 6: Evaluation dashboard

1. Add evaluation dataset format.
2. Add single query metrics.
3. Add batch evaluation.
4. Add dashboard cards.
5. Add failed case display.
6. Add exportable report.

### Phase 7: Portfolio polish

1. Add screenshots.
2. Add architecture documentation.
3. Add security documentation.
4. Add public demo dataset.
5. Add deployment documentation.
6. Add case study page content for brianekane.com.

## 21. Portfolio case study requirements

The final project should support a strong case study on brianekane.com.

The case study should explain:

1. The problem with naive RAG demos.
2. The architecture of this platform.
3. How documents are ingested.
4. How retrieval strategies differ.
5. How answers are grounded.
6. How evaluation works.
7. How privacy conscious local inference works.
8. What tradeoffs were made.
9. What future improvements are planned.

The case study should make it easy for a hiring manager to understand the project in two minutes and easy for a senior engineer to inspect the architecture in depth.

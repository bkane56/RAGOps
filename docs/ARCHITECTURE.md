# Architecture

## System overview

RAGOps Platform is a monorepo with a Next.js frontend and FastAPI backend. Application data, chunk metadata, embeddings, and RAG run logs live in PostgreSQL with the pgvector extension.

## Frontend architecture

- App Router pages per feature area
- Typed API client in `frontend/lib/api/`
- Shared UI primitives and feature components
- Client-side data fetching with loading, empty, and error states

## Backend architecture

Layers:

1. API routes (thin handlers)
2. Pydantic schemas
3. Application services (RAG pipeline, ingestion, evaluation)
4. Domain models (dataclasses)
5. Provider interfaces (LLM, embeddings, vector store, reranker)
6. Infrastructure adapters (Postgres, local files)

## RAG pipeline

1. Parse uploaded document
2. Chunk with recursive splitter
3. Embed chunks via Ollama
4. Upsert vectors to pgvector
5. Retrieve with selected strategy
6. Optionally rerank
7. Assemble context within token budget
8. Generate answer with citation instructions
9. Validate citations
10. Compute metrics and persist observability row

## Provider abstraction

Swappable interfaces allow future hosted LLM, OpenAI embeddings, or Qdrant vector store without API contract changes.

## Vector store design

Default: `PgVectorStore` using cosine distance (`<=>`) on `chunk_embeddings.embedding`. Document-scoped delete on reindex or document removal.

## Evaluation design

Synthetic cases in `demo-data/eval/sample_cases.json`. Batch runner executes `/ask` logic per case and aggregates pass rate, groundedness, citation coverage, and latency.

## Security and privacy

Synthetic demo data only. Upload validation, filename sanitization, no stack traces to clients, secrets server-side only.

## Deployment shape

- Frontend: Vercel
- Backend: Render or Railway
- Database: Supabase Postgres with pgvector or self-hosted Postgres

## Tradeoffs

- pgvector simplifies local demo versus dedicated vector DB
- Ollama avoids hosted API keys but adds host setup
- Deterministic evaluation metrics trade judge quality for reproducibility

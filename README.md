# RAGOps Platform

Production-style retrieval augmented generation platform for portfolio demonstration. This project exposes the full RAG lifecycle: ingestion, chunking, embeddings, vector search, retrieval strategy comparison, citation validation, and evaluation metrics.

## Why this is more than a chatbot

- Transparent pipeline stages visible in the UI and API
- Five comparable retrieval strategies
- Citation-backed answers with validation status
- Explicit insufficient evidence responses
- Evaluation dashboard with batch metrics
- Local-first Ollama defaults for privacy-conscious demos

## Architecture

```text
frontend/ (Next.js, Yarn)
    |
    v
backend/ (FastAPI, UV, Python 3.12)
    |
    +-- Postgres + pgvector (metadata and embeddings)
    +-- Local file storage (uploads)
    +-- Ollama (chat and embeddings)
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for details.

## Tech stack

| Layer | Stack |
|-------|-------|
| Frontend | Next.js, React, TypeScript, Tailwind, Yarn |
| Backend | FastAPI, Pydantic, SQLAlchemy, UV, Python 3.12 |
| Database | PostgreSQL with pgvector |
| Models | Ollama (local default) |

## Local setup

### Prerequisites

- Docker (for Postgres)
- [UV](https://docs.astral.sh/uv/) for Python
- [Yarn](https://yarnpkg.com/) for Node
- [Ollama](https://ollama.com/) for local inference (optional for UI-only exploration)

### 1. Start database

```bash
make db-up
cp .env.example .env
```

### 2. Backend

```bash
cd backend
uv sync --extra dev
uv run uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
yarn install
yarn dev
```

Open http://localhost:3000

### 4. Ollama models (for ask and ingestion)

```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

## Demo workflow

1. Upload a file from `demo-data/` on the Documents page
2. Inspect chunks for the document
3. Ask a question on the Ask page with a retrieval strategy
4. Review evidence, citations, and metrics
5. Compare strategies on the Compare page
6. Run batch evaluation on the Evaluation page

## Tests and coverage

```bash
make test-backend   # pytest, 90% minimum on app/
make test-frontend  # vitest, 90% minimum on lib/ and components/
```

## Environment variables

Copy `.env.example` and adjust values. Sanitized placeholders show the required shape. Never commit real secrets.

## Documentation

- [REQUIREMENTS.md](REQUIREMENTS.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/API.md](docs/API.md)
- [docs/EVALUATION.md](docs/EVALUATION.md)
- [docs/SECURITY.md](docs/SECURITY.md)

## Known limitations

- Reranker uses keyword overlap heuristic until a hosted reranker is configured
- Evaluation metrics are deterministic helpers, not LLM-as-judge
- PDF parsing quality depends on document structure
- Full RAG ask flow requires Ollama and indexed documents

## License

Portfolio demonstration project.

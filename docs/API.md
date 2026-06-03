# API Reference

Base URL: `http://localhost:8000` (configurable via `API_BASE_URL`)

## Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness check |
| GET | `/ready` | Readiness including database |

## Documents

| Method | Path | Description |
|--------|------|-------------|
| POST | `/documents` | Upload file (multipart) |
| GET | `/documents` | List documents |
| GET | `/documents/{id}` | Get document |
| DELETE | `/documents/{id}` | Delete document and chunks |
| POST | `/documents/{id}/reindex` | Reindex document |
| GET | `/documents/{id}/chunks` | List chunks |

## RAG

| Method | Path | Description |
|--------|------|-------------|
| POST | `/ask` | Run RAG pipeline |
| POST | `/compare-strategies` | Compare strategies for one question |

### Ask request body

```json
{
  "question": "string",
  "retrieval_strategy": "basic_vector",
  "top_k": 5,
  "document_ids": ["uuid optional"]
}
```

## Evaluation

| Method | Path | Description |
|--------|------|-------------|
| GET | `/overview` | Platform stats |
| GET | `/evaluations` | List evaluation runs |
| POST | `/evaluations/run` | Run batch evaluation |

## Settings

| Method | Path | Description |
|--------|------|-------------|
| GET | `/settings/runtime` | Runtime provider configuration |

## Errors

All errors return:

```json
{
  "error": {
    "code": "error_code",
    "message": "Human readable message"
  }
}
```

Stack traces are not exposed to clients.

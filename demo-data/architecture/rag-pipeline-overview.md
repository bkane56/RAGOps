# RAG Pipeline Overview

## Purpose

The RAGOps Platform demonstrates a full retrieval augmented generation lifecycle for portfolio review.

## Pipeline stages

1. Document upload and validation
2. Parsing for PDF, Markdown, and plain text
3. Recursive text chunking with overlap
4. Embedding generation via Ollama
5. Vector storage in Postgres with pgvector
6. Retrieval using selectable strategies
7. Optional reranking
8. Context assembly within token budget
9. Answer generation with citation markers
10. Citation validation and evaluation metrics

## Retrieval strategies

- basic_vector: cosine similarity search
- metadata_filtered_vector: vector search with document filters
- hybrid_keyword_vector: keyword overlap plus vector fusion
- multi_query: multiple query variants merged
- reranked: retrieve then rerank by relevance

## Environment variables

Backend requires DATABASE_URL, DOCUMENT_STORAGE_PATH, and Ollama settings for local demo mode.

# Evaluation

## Philosophy

RAG quality must be measurable for portfolio review. This platform combines per-query metrics on every `/ask` call and batch evaluation over a synthetic dataset.

## Metrics

| Metric | Meaning |
|--------|---------|
| Answer relevance | Proxy from context match when evidence exists |
| Context relevance | Average retrieval similarity |
| Groundedness | Citation coverage when answering |
| Citation coverage | Fraction of retrieved chunks cited |
| Retrieval latency | Time to retrieve chunks (ms) |
| Generation latency | LLM generation time (ms) |
| Total latency | End-to-end request time (ms) |
| Insufficient evidence rate | Share of cases flagged as unsupported |

## Test dataset format

`demo-data/eval/sample_cases.json`:

```json
{
  "question": "...",
  "expected_answer_summary": "...",
  "category": "direct_answer | no_supporting_evidence | ...",
  "difficulty": "easy | medium | hard",
  "expected_behavior": "insufficient_evidence | answer_with_citations"
}
```

## Running evaluations

```bash
curl -X POST http://localhost:8000/evaluations/run \
  -H "Content-Type: application/json" \
  -d '{"strategy_name": "basic_vector"}'
```

Or use the Evaluation page in the UI.

## Interpreting results

- High insufficient evidence rate on unsupported categories is expected
- Low citation coverage on citation_required cases indicates pipeline gaps
- Compare strategies using `/compare-strategies` before batch runs

## Limitations

Metrics use deterministic heuristics, not LLM judges. Scores are relative indicators for demos, not production SLAs.

"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api/client";
import { EvidencePanel } from "@/components/features/evidence/EvidencePanel";
import { CitationList } from "@/components/features/ask/CitationList";
import { MetricsSummary } from "@/components/features/ask/MetricsSummary";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import type { AskResponse } from "@/lib/types/api";

export default function AskPage() {
  const [question, setQuestion] = useState("");
  const [strategy, setStrategy] = useState("basic_vector");
  const [topK, setTopK] = useState(5);
  const [strategies, setStrategies] = useState<string[]>(["basic_vector"]);
  const [result, setResult] = useState<AskResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.runtimeSettings().then((s) => setStrategies(s.retrieval_strategies));
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!question.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await api.ask({
        question: question.trim(),
        retrieval_strategy: strategy,
        top_k: topK,
      });
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold">Ask</h1>

      <form onSubmit={handleSubmit} className="mb-8 space-y-4 rounded-lg border border-slate-800 bg-panel p-6">
        <div>
          <label htmlFor="question" className="mb-1 block text-sm text-muted">
            Question
          </label>
          <textarea
            id="question"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            rows={3}
            className="w-full rounded border border-slate-700 bg-surface px-3 py-2 text-white"
            data-testid="question-input"
          />
        </div>
        <div className="flex flex-wrap gap-4">
          <div>
            <label htmlFor="strategy" className="mb-1 block text-sm text-muted">
              Retrieval strategy
            </label>
            <select
              id="strategy"
              value={strategy}
              onChange={(e) => setStrategy(e.target.value)}
              className="rounded border border-slate-700 bg-surface px-3 py-2 text-white"
              data-testid="strategy-select"
            >
              {strategies.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="topk" className="mb-1 block text-sm text-muted">
              Top K
            </label>
            <input
              id="topk"
              type="number"
              min={1}
              max={20}
              value={topK}
              onChange={(e) => setTopK(Number(e.target.value))}
              className="w-20 rounded border border-slate-700 bg-surface px-3 py-2 text-white"
            />
          </div>
        </div>
        <button
          type="submit"
          disabled={loading}
          className="rounded bg-accent px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {loading ? "Running pipeline..." : "Ask"}
        </button>
      </form>

      {loading && <LoadingState label="Running RAG pipeline..." />}
      {error && <ErrorState message={error} />}

      {result && (
        <div className="space-y-6">
          <section
            className={`rounded-lg border p-6 ${
              result.insufficient_evidence
                ? "border-amber-700 bg-amber-950/30"
                : "border-slate-800 bg-panel"
            }`}
            data-testid="answer-area"
          >
            <h2 className="mb-2 text-lg font-medium">Answer</h2>
            {result.insufficient_evidence && (
              <p className="mb-2 text-sm text-amber-300">Insufficient evidence</p>
            )}
            <p className="whitespace-pre-wrap text-slate-200">{result.answer}</p>
            <CitationList citations={result.citations} />
            <p className="mt-2 text-xs text-muted">
              Validation: {result.citation_validation.status} (coverage{" "}
              {(result.citation_validation.coverage * 100).toFixed(0)}%)
            </p>
          </section>

          <section>
            <h2 className="mb-3 text-lg font-medium">Evaluation metrics</h2>
            <MetricsSummary metrics={result.metrics} />
          </section>

          <section>
            <h2 className="mb-3 text-lg font-medium">Evidence</h2>
            <EvidencePanel chunks={result.evidence} />
          </section>
        </div>
      )}
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api/client";
import { EvidencePanel } from "@/components/features/evidence/EvidencePanel";
import { MetricsSummary } from "@/components/features/ask/MetricsSummary";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import type { StrategyComparison } from "@/lib/types/api";

const DEFAULT_STRATEGIES = [
  "basic_vector",
  "metadata_filtered_vector",
  "hybrid_keyword_vector",
  "multi_query",
  "reranked",
];

export default function ComparePage() {
  const [question, setQuestion] = useState("");
  const [selected, setSelected] = useState<string[]>(DEFAULT_STRATEGIES);
  const [comparisons, setComparisons] = useState<StrategyComparison[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [available, setAvailable] = useState<string[]>(DEFAULT_STRATEGIES);

  useEffect(() => {
    api.runtimeSettings().then((s) => setAvailable(s.retrieval_strategies));
  }, []);

  function toggleStrategy(name: string) {
    setSelected((prev) =>
      prev.includes(name) ? prev.filter((s) => s !== name) : [...prev, name],
    );
  }

  async function handleCompare(e: React.FormEvent) {
    e.preventDefault();
    if (!question.trim() || !selected.length) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.compareStrategies({
        question: question.trim(),
        strategies: selected,
        top_k: 5,
      });
      setComparisons(res.comparisons);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Comparison failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold">Strategy comparison</h1>

      <form onSubmit={handleCompare} className="mb-8 space-y-4 rounded-lg border border-slate-800 bg-panel p-6">
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          rows={2}
          placeholder="Enter a question to compare strategies"
          className="w-full rounded border border-slate-700 bg-surface px-3 py-2 text-white"
          data-testid="compare-question"
        />
        <div className="flex flex-wrap gap-2">
          {available.map((s) => (
            <label key={s} className="flex items-center gap-1 text-sm">
              <input
                type="checkbox"
                checked={selected.includes(s)}
                onChange={() => toggleStrategy(s)}
              />
              <span className="font-mono text-accent">{s}</span>
            </label>
          ))}
        </div>
        <button
          type="submit"
          disabled={loading}
          className="rounded bg-accent px-4 py-2 text-sm text-white disabled:opacity-50"
        >
          Compare
        </button>
      </form>

      {loading && <LoadingState />}
      {error && <ErrorState message={error} />}

      <div className="space-y-8">
        {comparisons.map((c) => (
          <section
            key={c.strategy_name}
            className="rounded-lg border border-slate-800 bg-panel p-6"
            data-testid="comparison-block"
          >
            <h2 className="mb-2 font-mono text-accent">{c.strategy_name}</h2>
            <p className="mb-4 text-sm text-slate-200">{c.answer}</p>
            <MetricsSummary metrics={c.metrics} />
            <div className="mt-4">
              <EvidencePanel chunks={c.evidence} />
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api/client";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import type { Overview } from "@/lib/types/api";

export default function OverviewPage() {
  const [data, setData] = useState<Overview | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .overview()
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;
  if (!data) return null;

  const evalSummary = data.latest_evaluation as Record<string, number>;

  return (
    <div>
      <h1 className="mb-2 text-2xl font-semibold">RAGOps Platform</h1>
      <p className="mb-8 max-w-2xl text-muted">
        A production-style retrieval augmented generation system that exposes ingestion,
        chunking, retrieval strategies, citation validation, and evaluation metrics.
        This is not a black-box chatbot.
      </p>

      <section className="mb-8 rounded-lg border border-slate-800 bg-panel p-6">
        <h2 className="mb-4 text-lg font-medium">RAG pipeline</h2>
        <ol className="list-decimal space-y-1 pl-5 text-sm text-slate-300">
          <li>Document upload and parsing</li>
          <li>Chunking and metadata extraction</li>
          <li>Embedding generation</li>
          <li>Vector storage (pgvector)</li>
          <li>Retrieval strategy selection</li>
          <li>Optional reranking</li>
          <li>Context assembly</li>
          <li>Answer generation with citations</li>
          <li>Citation validation and evaluation</li>
        </ol>
      </section>

      <div className="mb-8 grid gap-4 sm:grid-cols-3">
        <StatCard label="Documents" value={data.document_count} />
        <StatCard label="Chunks" value={data.chunk_count} />
        <StatCard label="Queries logged" value={data.query_count} />
      </div>

      <section className="mb-8">
        <h2 className="mb-3 text-lg font-medium">Retrieval strategies</h2>
        <ul className="flex flex-wrap gap-2">
          {data.retrieval_strategies.map((s) => (
            <li key={s} className="rounded bg-surface px-3 py-1 text-sm font-mono text-accent">
              {s}
            </li>
          ))}
        </ul>
      </section>

      {evalSummary && Object.keys(evalSummary).length > 0 && (
        <section className="rounded-lg border border-slate-800 bg-panel p-6">
          <h2 className="mb-3 text-lg font-medium">Latest evaluation</h2>
          <dl className="grid gap-2 text-sm sm:grid-cols-2">
            {evalSummary.pass_rate != null && (
              <Metric label="Pass rate" value={`${(evalSummary.pass_rate * 100).toFixed(0)}%`} />
            )}
            {evalSummary.avg_groundedness != null && (
              <Metric label="Avg groundedness" value={String(evalSummary.avg_groundedness)} />
            )}
            {evalSummary.insufficient_evidence_rate != null && (
              <Metric
                label="Insufficient evidence rate"
                value={`${(evalSummary.insufficient_evidence_rate * 100).toFixed(0)}%`}
              />
            )}
          </dl>
        </section>
      )}
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border border-slate-800 bg-panel p-4">
      <p className="text-muted text-sm">{label}</p>
      <p className="text-2xl font-semibold">{value}</p>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-muted text-xs">{label}</dt>
      <dd className="font-mono">{value}</dd>
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api/client";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import type { EvaluationRun } from "@/lib/types/api";

export default function EvaluationPage() {
  const [runs, setRuns] = useState<{ id: string; aggregate_metrics: Record<string, unknown>; created_at: string }[]>([]);
  const [latest, setLatest] = useState<EvaluationRun | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.listEvaluations().then(setRuns).catch(() => {});
  }, [latest]);

  async function runBatch() {
    setLoading(true);
    setError(null);
    try {
      const result = await api.runEvaluation("basic_vector");
      setLatest(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Evaluation failed");
    } finally {
      setLoading(false);
    }
  }

  function exportReport() {
    const data = latest || runs[0]?.aggregate_metrics;
    if (!data) return;
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "evaluation-report.json";
    a.click();
    URL.revokeObjectURL(url);
  }

  const metrics = latest || (runs[0]?.aggregate_metrics as EvaluationRun | undefined);

  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold">Evaluation dashboard</h1>

      <div className="mb-6 flex gap-3">
        <button
          type="button"
          onClick={runBatch}
          disabled={loading}
          className="rounded bg-accent px-4 py-2 text-sm text-white disabled:opacity-50"
        >
          Run batch evaluation
        </button>
        <button
          type="button"
          onClick={exportReport}
          className="rounded border border-slate-600 px-4 py-2 text-sm text-muted hover:text-white"
          data-testid="export-button"
        >
          Export JSON
        </button>
      </div>

      {loading && <LoadingState />}
      {error && <ErrorState message={error} />}

      {metrics && (
        <>
          <div
            className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4"
            data-testid="evaluation-dashboard"
          >
            <Card label="Cases" value={String(metrics.case_count ?? 0)} />
            <Card
              label="Pass rate"
              value={`${((metrics.pass_rate ?? 0) * 100).toFixed(0)}%`}
            />
            <Card label="Avg groundedness" value={String(metrics.avg_groundedness ?? 0)} />
            <Card
              label="Insufficient evidence"
              value={`${((metrics.insufficient_evidence_rate ?? 0) * 100).toFixed(0)}%`}
            />
            <Card label="Avg citation coverage" value={String(metrics.avg_citation_coverage ?? 0)} />
            <Card label="Avg latency ms" value={String(metrics.avg_total_latency_ms ?? 0)} />
          </div>

          {metrics.failed_cases && metrics.failed_cases.length > 0 && (
            <section className="rounded-lg border border-slate-800 bg-panel p-6">
              <h2 className="mb-3 text-lg font-medium">Failed cases</h2>
              <ul className="space-y-2 text-sm">
                {metrics.failed_cases.map((fc, i) => (
                  <li key={i} className="text-red-300">
                    {fc.question}: {fc.reason}
                  </li>
                ))}
              </ul>
            </section>
          )}
        </>
      )}

      {!metrics && !loading && (
        <p className="text-muted text-sm">No evaluation runs yet. Run batch evaluation to populate metrics.</p>
      )}
    </div>
  );
}

function Card({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-slate-800 bg-panel p-4">
      <p className="text-muted text-xs">{label}</p>
      <p className="text-xl font-semibold">{value}</p>
    </div>
  );
}

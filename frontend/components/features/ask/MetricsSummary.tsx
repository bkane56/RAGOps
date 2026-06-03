import type { QueryMetrics } from "@/lib/types/api";

export function MetricsSummary({ metrics }: { metrics: QueryMetrics }) {
  const items = [
    { label: "Answer relevance", value: metrics.answer_relevance },
    { label: "Context relevance", value: metrics.context_relevance },
    { label: "Groundedness", value: metrics.groundedness },
    { label: "Citation coverage", value: metrics.citation_coverage },
    { label: "Retrieval ms", value: metrics.retrieval_latency_ms },
    { label: "Generation ms", value: metrics.generation_latency_ms },
    { label: "Total ms", value: metrics.total_latency_ms },
  ];
  return (
    <dl
      className="grid grid-cols-2 gap-2 text-sm sm:grid-cols-4"
      data-testid="metrics-summary"
    >
      {items.map((item) => (
        <div key={item.label} className="rounded bg-panel p-2">
          <dt className="text-muted text-xs">{item.label}</dt>
          <dd className="font-mono text-white">
            {typeof item.value === "number" && item.value < 1
              ? (item.value * 100).toFixed(0) + "%"
              : item.value}
          </dd>
        </div>
      ))}
    </dl>
  );
}

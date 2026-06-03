"use client";

import { useState } from "react";
import type { EvidenceChunk } from "@/lib/types/api";

interface EvidencePanelProps {
  chunks: EvidenceChunk[];
}

export function EvidencePanel({ chunks }: EvidencePanelProps) {
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  if (!chunks.length) {
    return <p className="text-muted text-sm">No retrieved evidence.</p>;
  }

  return (
    <div className="space-y-3" data-testid="evidence-panel">
      {chunks.map((chunk) => {
        const isOpen = expanded[chunk.chunk_id];
        return (
          <article
            key={chunk.chunk_id}
            className={`rounded border p-3 ${
              chunk.cited ? "border-accent/60 bg-accent/5" : "border-slate-700 bg-surface"
            }`}
            data-testid="evidence-card"
          >
            <header className="mb-2 flex flex-wrap items-center gap-2 text-xs text-muted">
              <span className="font-medium text-white">{chunk.filename}</span>
              {chunk.page_number != null && <span>page {chunk.page_number}</span>}
              <span>{chunk.strategy_name}</span>
              {chunk.similarity_score != null && (
                <span>sim {(chunk.similarity_score * 100).toFixed(0)}%</span>
              )}
              {chunk.reranker_score != null && (
                <span>rerank {chunk.reranker_score.toFixed(2)}</span>
              )}
              {chunk.cited && (
                <span className="rounded bg-accent/20 px-1.5 text-accent">cited</span>
              )}
            </header>
            <p className={`text-sm text-slate-200 ${isOpen ? "" : "line-clamp-3"}`}>
              {chunk.chunk_text}
            </p>
            <button
              type="button"
              aria-expanded={isOpen}
              aria-label={isOpen ? "Collapse chunk" : "Expand chunk"}
              className="mt-2 text-xs text-accent hover:underline"
              onClick={() =>
                setExpanded((e) => ({ ...e, [chunk.chunk_id]: !e[chunk.chunk_id] }))
              }
            >
              {isOpen ? "Collapse" : "Expand"}
            </button>
          </article>
        );
      })}
    </div>
  );
}

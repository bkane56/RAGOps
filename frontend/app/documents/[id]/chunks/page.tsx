"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api/client";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import type { Chunk } from "@/lib/types/api";

export default function ChunksPage() {
  const params = useParams();
  const id = params.id as string;
  const [chunks, setChunks] = useState<Chunk[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .listChunks(id)
      .then(setChunks)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold">Chunk inspection</h1>
      {loading && <LoadingState />}
      {error && <ErrorState message={error} />}
      <div className="space-y-4">
        {chunks.map((chunk) => (
          <article
            key={chunk.id}
            className="rounded border border-slate-800 bg-panel p-4"
            data-testid="chunk-card"
          >
            <header className="mb-2 flex flex-wrap gap-2 text-xs text-muted">
              <span className="font-mono text-accent">{chunk.id.slice(0, 8)}</span>
              {chunk.page_number != null && <span>page {chunk.page_number}</span>}
              <span>{chunk.chunking_strategy}</span>
              <span>{chunk.token_estimate} tokens</span>
            </header>
            <p className="text-sm text-slate-200">{chunk.text}</p>
          </article>
        ))}
      </div>
    </div>
  );
}

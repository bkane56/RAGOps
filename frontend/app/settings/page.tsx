"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api/client";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import type { RuntimeSettings } from "@/lib/types/api";

export default function SettingsPage() {
  const [settings, setSettings] = useState<RuntimeSettings | null>(null);
  const [ready, setReady] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.runtimeSettings(), api.ready()])
      .then(([s, r]) => {
        setSettings(s);
        setReady(`${r.status} (${r.database})`);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;
  if (!settings) return null;

  const rows = [
    ["Environment", settings.app_env],
    ["LLM provider", settings.llm_provider],
    ["LLM model", settings.llm_model],
    ["Embedding model", settings.embedding_model],
    ["Vector store", settings.vector_store_provider],
    ["Max upload MB", String(settings.max_upload_mb)],
    ["Ollama URL", settings.ollama_base_url],
    ["Eval enabled", String(settings.eval_enabled)],
    ["Readiness", ready ?? "unknown"],
  ];

  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold">Settings</h1>
      <dl className="max-w-xl space-y-3 rounded-lg border border-slate-800 bg-panel p-6 text-sm">
        {rows.map(([label, value]) => (
          <div key={label} className="flex justify-between gap-4">
            <dt className="text-muted">{label}</dt>
            <dd className="font-mono text-right text-white">{value}</dd>
          </div>
        ))}
      </dl>
      <p className="mt-4 text-sm text-muted">
        Hosted LLM keys are optional. Local Ollama is the default for the demo.
      </p>
    </div>
  );
}

"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api/client";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { EmptyState } from "@/components/ui/EmptyState";
import type { Document } from "@/lib/types/api";

export default function DocumentsPage() {
  const [docs, setDocs] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    api
      .listDocuments()
      .then(setDocs)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      await api.uploadDocument(file);
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  }

  async function handleDelete(id: string) {
    await api.deleteDocument(id);
    load();
  }

  async function handleReindex(id: string) {
    await api.reindexDocument(id);
    load();
  }

  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold">Documents</h1>

      <label className="mb-8 flex cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed border-slate-600 bg-panel p-8 hover:border-accent">
        <span className="mb-2 text-sm text-muted">Upload PDF, Markdown, or plain text</span>
        <span className="text-accent text-sm">{uploading ? "Uploading..." : "Choose file"}</span>
        <input
          type="file"
          accept=".pdf,.md,.markdown,.txt,.text"
          className="hidden"
          onChange={handleUpload}
          disabled={uploading}
          data-testid="file-upload"
        />
      </label>

      {error && <ErrorState message={error} />}
      {loading && <LoadingState />}
      {!loading && !docs.length && <EmptyState message="No documents indexed yet." />}

      {!loading && docs.length > 0 && (
        <table className="w-full text-left text-sm" data-testid="document-table">
          <thead>
            <tr className="border-b border-slate-700 text-muted">
              <th className="py-2">Filename</th>
              <th>Status</th>
              <th>Chunks</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {docs.map((doc) => (
              <tr key={doc.id} className="border-b border-slate-800">
                <td className="py-3">{doc.filename}</td>
                <td>
                  <StatusBadge status={doc.status} />
                  {doc.error_message && (
                    <p className="mt-1 text-xs text-red-400">{doc.error_message}</p>
                  )}
                </td>
                <td>{doc.chunk_count}</td>
                <td className="space-x-2">
                  <Link
                    href={`/documents/${doc.id}/chunks`}
                    className="text-accent hover:underline"
                  >
                    Chunks
                  </Link>
                  <button
                    type="button"
                    className="text-muted hover:text-white"
                    onClick={() => handleReindex(doc.id)}
                  >
                    Reindex
                  </button>
                  <button
                    type="button"
                    className="text-red-400 hover:underline"
                    onClick={() => handleDelete(doc.id)}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

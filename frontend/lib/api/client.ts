import type {
  AskResponse,
  Chunk,
  Document,
  EvaluationRun,
  Overview,
  RuntimeSettings,
  StrategyComparison,
} from "@/lib/types/api";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    public code: string,
    public status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        ...(options?.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
        ...options?.headers,
      },
    });
  } catch {
    throw new ApiError(
      `Cannot reach API at ${API_BASE}. Check that the backend is running on port 8000.`,
      "network_error",
      0,
    );
  }
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    let code = "http_error";
    try {
      const body = await response.json();
      message = body?.error?.message || message;
      code = body?.error?.code || code;
    } catch {
      /* ignore */
    }
    throw new ApiError(message, code, response.status);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<{ status: string; app_name: string }>("/health"),
  ready: () => request<{ status: string; database: string }>("/ready"),
  overview: () => request<Overview>("/overview"),
  listDocuments: () => request<Document[]>("/documents"),
  getDocument: (id: string) => request<Document>(`/documents/${id}`),
  uploadDocument: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<Document>("/documents", { method: "POST", body: form });
  },
  deleteDocument: (id: string) =>
    request<void>(`/documents/${id}`, { method: "DELETE" }),
  reindexDocument: (id: string) =>
    request<Document>(`/documents/${id}/reindex`, { method: "POST" }),
  listChunks: (id: string) => request<Chunk[]>(`/documents/${id}/chunks`),
  ask: (body: {
    question: string;
    retrieval_strategy: string;
    top_k: number;
    document_ids?: string[];
  }) =>
    request<AskResponse>("/ask", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  compareStrategies: (body: {
    question: string;
    strategies: string[];
    top_k: number;
  }) =>
    request<{ question: string; comparisons: StrategyComparison[] }>(
      "/compare-strategies",
      { method: "POST", body: JSON.stringify(body) },
    ),
  runtimeSettings: () => request<RuntimeSettings>("/settings/runtime"),
  listEvaluations: () =>
    request<{ id: string; aggregate_metrics: Record<string, unknown>; created_at: string }[]>(
      "/evaluations",
    ),
  runEvaluation: (strategy_name: string) =>
    request<EvaluationRun>("/evaluations/run", {
      method: "POST",
      body: JSON.stringify({ strategy_name }),
    }),
};

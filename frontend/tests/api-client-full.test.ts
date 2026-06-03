import { describe, expect, it, vi, afterEach } from "vitest";
import { api } from "@/lib/api/client";

function mockFetch(body: unknown, ok = true, status = 200) {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok,
      status,
      json: async () => body,
    }),
  );
}

describe("api client methods", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("ready", async () => {
    mockFetch({ status: "ready", database: "connected" });
    const r = await api.ready();
    expect(r.database).toBe("connected");
  });

  it("overview", async () => {
    mockFetch({ document_count: 0, chunk_count: 0, query_count: 0, retrieval_strategies: [], latest_evaluation: {} });
    const r = await api.overview();
    expect(r.document_count).toBe(0);
  });

  it("listDocuments", async () => {
    mockFetch([]);
    expect(await api.listDocuments()).toEqual([]);
  });

  it("uploadDocument", async () => {
    mockFetch({ id: "1", filename: "a.txt", file_type: "text", status: "ready", content_hash: null, chunk_count: 1, created_at: "", error_message: null });
    const file = new File(["hi"], "a.txt", { type: "text/plain" });
    const r = await api.uploadDocument(file);
    expect(r.filename).toBe("a.txt");
  });

  it("deleteDocument 204", async () => {
    mockFetch(undefined, true, 204);
    await expect(api.deleteDocument("id")).resolves.toBeUndefined();
  });

  it("ask", async () => {
    mockFetch({
      query_id: "q",
      answer: "a",
      citations: [],
      insufficient_evidence: false,
      evidence: [],
      metrics: {
        answer_relevance: 1,
        context_relevance: 1,
        groundedness: 1,
        citation_coverage: 1,
        retrieval_latency_ms: 1,
        generation_latency_ms: 1,
        total_latency_ms: 2,
        retrieved_chunk_count: 1,
        cited_chunk_count: 1,
        insufficient_evidence: false,
      },
      citation_validation: { coverage: 1, status: "valid", unsupported_segments: [] },
      model_provider: "ollama",
      model_name: "test",
    });
    const r = await api.ask({ question: "q", retrieval_strategy: "basic_vector", top_k: 5 });
    expect(r.answer).toBe("a");
  });

  it("compareStrategies", async () => {
    mockFetch({ question: "q", comparisons: [] });
    const r = await api.compareStrategies({ question: "q", strategies: ["basic_vector"], top_k: 5 });
    expect(r.comparisons).toEqual([]);
  });

  it("runtimeSettings", async () => {
    mockFetch({
      app_env: "development",
      llm_provider: "ollama",
      llm_model: "m",
      embedding_model: "e",
      vector_store_provider: "pgvector",
      max_upload_mb: 10,
      ollama_base_url: "http://localhost:11434",
      eval_enabled: true,
      retrieval_strategies: ["basic_vector"],
    });
    const r = await api.runtimeSettings();
    expect(r.llm_provider).toBe("ollama");
  });

  it("getDocument", async () => {
    mockFetch({ id: "1", filename: "a.txt", file_type: "text", status: "ready", content_hash: null, chunk_count: 0, created_at: "", error_message: null });
    const r = await api.getDocument("1");
    expect(r.id).toBe("1");
  });

  it("reindexDocument", async () => {
    mockFetch({ id: "1", filename: "a.txt", file_type: "text", status: "processing", content_hash: null, chunk_count: 0, created_at: "", error_message: null });
    const r = await api.reindexDocument("1");
    expect(r.status).toBe("processing");
  });

  it("listChunks", async () => {
    mockFetch([]);
    expect(await api.listChunks("1")).toEqual([]);
  });

  it("listEvaluations", async () => {
    mockFetch([]);
    expect(await api.listEvaluations()).toEqual([]);
  });

  it("runEvaluation", async () => {
    mockFetch({
      run_id: "1",
      case_count: 1,
      pass_rate: 1,
      avg_groundedness: 0,
      avg_answer_relevance: 0,
      avg_context_relevance: 0,
      insufficient_evidence_rate: 0,
      avg_citation_coverage: 0,
      avg_total_latency_ms: 0,
      failed_cases: [],
    });
    const r = await api.runEvaluation("basic_vector");
    expect(r.case_count).toBe(1);
  });
});

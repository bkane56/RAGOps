export interface Document {
  id: string;
  filename: string;
  file_type: string;
  status: string;
  content_hash: string | null;
  chunk_count: number;
  created_at: string;
  error_message: string | null;
}

export interface Chunk {
  id: string;
  document_id: string;
  text: string;
  page_number: number | null;
  section_heading: string | null;
  token_estimate: number;
  chunking_strategy: string;
  content_hash: string;
}

export interface EvidenceChunk {
  chunk_id: string;
  document_id: string;
  filename: string;
  page_number: number | null;
  chunk_text: string;
  similarity_score: number | null;
  reranker_score: number | null;
  strategy_name: string;
  token_estimate: number;
  cited: boolean;
}

export interface QueryMetrics {
  answer_relevance: number;
  context_relevance: number;
  groundedness: number;
  citation_coverage: number;
  retrieval_latency_ms: number;
  generation_latency_ms: number;
  total_latency_ms: number;
  retrieved_chunk_count: number;
  cited_chunk_count: number;
  insufficient_evidence: boolean;
}

export interface CitationValidation {
  coverage: number;
  status: string;
  unsupported_segments: string[];
}

export interface AskResponse {
  query_id: string;
  answer: string;
  citations: { chunk_id: string; label: string }[];
  insufficient_evidence: boolean;
  evidence: EvidenceChunk[];
  metrics: QueryMetrics;
  citation_validation: CitationValidation;
  model_provider: string;
  model_name: string;
}

export interface StrategyComparison {
  strategy_name: string;
  answer: string;
  insufficient_evidence: boolean;
  evidence: EvidenceChunk[];
  metrics: QueryMetrics;
  citation_validation: CitationValidation;
}

export interface RuntimeSettings {
  app_env: string;
  llm_provider: string;
  llm_model: string;
  embedding_model: string;
  vector_store_provider: string;
  max_upload_mb: number;
  ollama_base_url: string;
  eval_enabled: boolean;
  retrieval_strategies: string[];
}

export interface Overview {
  document_count: number;
  chunk_count: number;
  query_count: number;
  retrieval_strategies: string[];
  latest_evaluation: Record<string, unknown>;
}

export interface EvaluationRun {
  run_id: string | null;
  case_count: number;
  pass_rate: number;
  avg_groundedness: number;
  avg_answer_relevance: number;
  avg_context_relevance: number;
  insufficient_evidence_rate: number;
  avg_citation_coverage: number;
  avg_total_latency_ms: number;
  failed_cases: { question?: string; reason?: string }[];
}

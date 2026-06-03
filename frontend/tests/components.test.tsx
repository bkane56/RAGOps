import { describe, expect, it } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { EvidencePanel } from "@/components/features/evidence/EvidencePanel";
import { CitationList } from "@/components/features/ask/CitationList";
import { MetricsSummary } from "@/components/features/ask/MetricsSummary";
import type { EvidenceChunk, QueryMetrics } from "@/lib/types/api";

describe("UI components", () => {
  it("renders StatusBadge", () => {
    render(<StatusBadge status="ready" />);
    expect(screen.getByText("ready")).toBeInTheDocument();
  });

  it("renders EmptyState", () => {
    render(<EmptyState message="No data" />);
    expect(screen.getByText("No data")).toBeInTheDocument();
  });

  it("renders ErrorState", () => {
    render(<ErrorState message="Failed" />);
    expect(screen.getByRole("alert")).toHaveTextContent("Failed");
  });

  it("renders LoadingState", () => {
    render(<LoadingState label="Wait" />);
    expect(screen.getByText("Wait")).toBeInTheDocument();
  });
});

describe("EvidencePanel", () => {
  const chunk: EvidenceChunk = {
    chunk_id: "c1",
    document_id: "d1",
    filename: "doc.md",
    page_number: 1,
    chunk_text: "Sample evidence text for testing.",
    similarity_score: 0.85,
    reranker_score: null,
    strategy_name: "basic_vector",
    token_estimate: 10,
    cited: true,
  };

  it("renders evidence cards", () => {
    render(<EvidencePanel chunks={[chunk]} />);
    expect(screen.getByTestId("evidence-panel")).toBeInTheDocument();
    expect(screen.getByText("doc.md")).toBeInTheDocument();
    expect(screen.getByText("cited")).toBeInTheDocument();
  });

  it("expands chunk text", () => {
    const { getByLabelText } = render(<EvidencePanel chunks={[chunk]} />);
    fireEvent.click(getByLabelText("Expand chunk"));
    expect(getByLabelText("Collapse chunk")).toBeInTheDocument();
  });

  it("shows empty message", () => {
    render(<EvidencePanel chunks={[]} />);
    expect(screen.getByText("No retrieved evidence.")).toBeInTheDocument();
  });
});

describe("CitationList", () => {
  it("renders citations", () => {
    render(
      <CitationList
        citations={[{ chunk_id: "abc-123", label: "[1]" }]}
      />,
    );
    expect(screen.getByTestId("citation-list")).toBeInTheDocument();
    expect(screen.getByText(/\[1\]/)).toBeInTheDocument();
  });
});

describe("MetricsSummary", () => {
  const metrics: QueryMetrics = {
    answer_relevance: 0.8,
    context_relevance: 0.7,
    groundedness: 0.9,
    citation_coverage: 0.5,
    retrieval_latency_ms: 100,
    generation_latency_ms: 200,
    total_latency_ms: 300,
    retrieved_chunk_count: 5,
    cited_chunk_count: 2,
    insufficient_evidence: false,
  };

  it("renders metrics", () => {
    render(<MetricsSummary metrics={metrics} />);
    expect(screen.getByTestId("metrics-summary")).toBeInTheDocument();
    expect(screen.getByText("Answer relevance")).toBeInTheDocument();
  });
});

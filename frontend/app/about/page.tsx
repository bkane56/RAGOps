export default function AboutPage() {
  return (
    <div className="prose prose-invert max-w-none">
      <h1 className="text-2xl font-semibold text-white">About this platform</h1>
      <p className="text-muted">
        RAGOps Platform demonstrates production-style RAG engineering for portfolio review.
        It addresses limitations of naive chatbot demos by exposing the full pipeline.
      </p>

      <h2 className="mt-8 text-lg font-medium text-white">Problem with naive RAG demos</h2>
      <p className="text-slate-300">
        Many demos hide retrieval, skip citation validation, and provide no measurable quality
        signals. Reviewers cannot assess architecture judgment or operational readiness.
      </p>

      <h2 className="mt-8 text-lg font-medium text-white">Architecture highlights</h2>
      <ul className="list-disc pl-5 text-slate-300">
        <li>Layered FastAPI backend with provider interfaces</li>
        <li>Postgres and pgvector for metadata and embeddings</li>
        <li>Five comparable retrieval strategies</li>
        <li>Citation validation and insufficient evidence handling</li>
        <li>Evaluation dashboard with batch metrics</li>
        <li>Privacy-conscious Ollama defaults</li>
      </ul>

      <h2 className="mt-8 text-lg font-medium text-white">Tradeoffs</h2>
      <p className="text-slate-300">
        Local inference reduces cost and privacy risk but requires Ollama on the host.
        pgvector keeps operations simple versus a dedicated vector database. Evaluation metrics
        use deterministic helpers alongside pipeline observability rather than expensive LLM judges.
      </p>

      <h2 className="mt-8 text-lg font-medium text-white">Future improvements</h2>
      <ul className="list-disc pl-5 text-slate-300">
        <li>Qdrant adapter for vector store comparison experiments</li>
        <li>Hosted reranker integration</li>
        <li>Semantic chunking strategies</li>
        <li>Portfolio document connector for brianekane.com</li>
      </ul>
    </div>
  );
}

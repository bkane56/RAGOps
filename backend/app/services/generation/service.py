import re

from app.domain.generation.models import AssembledContext, CitationRef, GeneratedAnswer
from app.providers.llm.base import LLMProvider

SYSTEM_PROMPT = """You are a RAG assistant. Answer ONLY using the provided context.
Include citation labels like [1], [2] that match the context blocks.
If the context does not support an answer, respond with: INSUFFICIENT_EVIDENCE
Do not guess or use outside knowledge."""

GENERATION_PROMPT = """Context:
{context}

Question: {question}

Answer with citations:"""


class GenerationService:
    def __init__(self, llm: LLMProvider) -> None:
        self._llm = llm

    async def generate(self, question: str, context: AssembledContext) -> GeneratedAnswer:
        if not context.context_text.strip():
            return GeneratedAnswer(
                text="Insufficient evidence in the indexed documents to answer this question.",
                citations=[],
                model_provider=self._llm.provider_name,
                model_name=self._llm.model_name,
                generation_latency_ms=0.0,
                insufficient_evidence=True,
            )

        prompt = GENERATION_PROMPT.format(context=context.context_text, question=question)
        response = await self._llm.generate(prompt, system=SYSTEM_PROMPT)
        insufficient = "INSUFFICIENT_EVIDENCE" in response.text.upper()
        text = response.text.replace("INSUFFICIENT_EVIDENCE", "").strip()
        if insufficient and not text:
            text = "Insufficient evidence in the indexed documents to answer this question."

        citations = self._extract_citations(response.text, context)
        return GeneratedAnswer(
            text=text,
            citations=citations,
            model_provider=response.model_provider,
            model_name=response.model_name,
            generation_latency_ms=response.latency_ms,
            insufficient_evidence=insufficient,
        )

    def _extract_citations(self, answer: str, context: AssembledContext) -> list[CitationRef]:
        labels = re.findall(r"\[(\d+)\]", answer)
        refs: list[CitationRef] = []
        for label in labels:
            key = f"[{label}]"
            chunk_id = context.citation_map.get(key)
            if chunk_id:
                refs.append(CitationRef(chunk_id=chunk_id, label=key))
        return refs

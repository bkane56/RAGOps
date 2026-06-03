import re
from uuid import UUID

from app.domain.generation.models import CitationValidationResult, GeneratedAnswer
from app.domain.retrieval.models import RetrievedChunk


class CitationValidationService:
    def validate(
        self,
        answer: GeneratedAnswer,
        retrieved: list[RetrievedChunk],
    ) -> CitationValidationResult:
        retrieved_ids = {str(c.chunk_id) for c in retrieved}
        cited_ids: list[UUID] = []
        for ref in answer.citations:
            if ref.chunk_id in retrieved_ids:
                try:
                    cited_ids.append(UUID(ref.chunk_id))
                except ValueError:
                    pass

        labels_in_answer = re.findall(r"\[(\d+)\]", answer.text)
        factual_claims = len(re.split(r"[.!?]\s+", answer.text.strip())) if answer.text.strip() else 0

        if answer.insufficient_evidence:
            return CitationValidationResult(
                coverage=0.0,
                status="insufficient_evidence",
                cited_chunk_ids=[],
                unsupported_segments=[],
            )

        if factual_claims > 1 and not labels_in_answer and not answer.insufficient_evidence:
            return CitationValidationResult(
                coverage=0.0,
                status="invalid",
                cited_chunk_ids=cited_ids,
                unsupported_segments=["Answer lacks citation markers for factual claims"],
            )

        coverage = len(cited_ids) / max(len(retrieved), 1)
        status = "valid" if coverage > 0 or answer.insufficient_evidence else "partial"

        return CitationValidationResult(
            coverage=min(1.0, coverage),
            status=status,
            cited_chunk_ids=cited_ids,
            unsupported_segments=[],
        )

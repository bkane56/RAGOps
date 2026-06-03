from app.core.config import get_settings
from app.domain.generation.models import AssembledContext
from app.domain.retrieval.models import RetrievedChunk


class ContextAssemblyService:
    def __init__(self) -> None:
        self._token_budget = get_settings().context_token_budget

    def assemble(self, chunks: list[RetrievedChunk]) -> AssembledContext:
        seen: set = set()
        selected: list[RetrievedChunk] = []
        tokens = 0
        sorted_chunks = sorted(
            chunks,
            key=lambda c: (c.reranker_score or 0, c.similarity_score or 0),
            reverse=True,
        )
        for chunk in sorted_chunks:
            if chunk.chunk_id in seen:
                continue
            est = chunk.token_estimate or max(1, len(chunk.chunk_text) // 4)
            if tokens + est > self._token_budget:
                break
            seen.add(chunk.chunk_id)
            selected.append(chunk)
            tokens += est

        parts: list[str] = []
        citation_map: dict[str, str] = {}
        for idx, chunk in enumerate(selected, start=1):
            label = f"[{idx}]"
            citation_map[label] = str(chunk.chunk_id)
            header = f"{label} source={chunk.filename}"
            if chunk.page_number:
                header += f" page={chunk.page_number}"
            parts.append(f"{header}\n{chunk.chunk_text}")

        return AssembledContext(
            chunks=selected,
            context_text="\n\n".join(parts),
            citation_map=citation_map,
        )

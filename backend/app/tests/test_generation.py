from app.domain.generation.models import AssembledContext
from app.services.generation.service import GenerationService


class MockLLM:
    provider_name = "mock"
    model_name = "mock-model"

    async def generate(self, prompt: str, system: str | None = None):
        from app.providers.llm.base import LLMResponse

        return LLMResponse(
            text="Answer based on [1] context.",
            model_provider=self.provider_name,
            model_name=self.model_name,
            latency_ms=5.0,
        )


async def test_generate_with_context():
    service = GenerationService(MockLLM())
    ctx = AssembledContext(
        chunks=[],
        context_text="[1] source=doc.txt\nSome context.",
        citation_map={"[1]": "chunk-uuid"},
    )
    answer = await service.generate("What is context?", ctx)
    assert "Answer" in answer.text
    assert len(answer.citations) >= 0


async def test_generate_empty_context():
    service = GenerationService(MockLLM())
    ctx = AssembledContext(chunks=[], context_text="", citation_map={})
    answer = await service.generate("question?", ctx)
    assert answer.insufficient_evidence is True

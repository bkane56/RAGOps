from app.domain.generation.models import AssembledContext
from app.services.generation.service import GenerationService


class MockLLM:
    provider_name = "mock"
    model_name = "m"

    async def generate(self, prompt: str, system: str | None = None):
        from app.providers.llm.base import LLMResponse

        return LLMResponse(text="See [1] and [2] for details.", model_provider="mock", model_name="m", latency_ms=1.0)


async def test_extract_multiple_citations():
    service = GenerationService(MockLLM())
    ctx = AssembledContext(
        chunks=[],
        context_text="ctx",
        citation_map={"[1]": "id-1", "[2]": "id-2"},
    )
    answer = await service.generate("q?", ctx)
    assert len(answer.citations) == 2

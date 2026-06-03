from app.services.retrieval.strategies import STRATEGY_REGISTRY


def test_all_strategies_registered():
    expected = {
        "basic_vector",
        "metadata_filtered_vector",
        "hybrid_keyword_vector",
        "multi_query",
        "reranked",
    }
    assert expected == set(STRATEGY_REGISTRY.keys())

def test_overview_endpoint(client, monkeypatch):
    stats = {
        "document_count": 1,
        "chunk_count": 5,
        "query_count": 2,
        "retrieval_strategies": ["basic_vector"],
        "latest_evaluation": {},
    }

    class FakeService:
        def __init__(self, db):
            pass

        def get_overview_stats(self):
            return stats

    monkeypatch.setattr("app.api.routes.evaluations.EvaluationService", FakeService)
    response = client.get("/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["document_count"] == 1

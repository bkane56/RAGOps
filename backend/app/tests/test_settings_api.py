def test_runtime_settings(client):
    response = client.get("/settings/runtime")
    assert response.status_code == 200
    data = response.json()
    assert "retrieval_strategies" in data
    assert "basic_vector" in data["retrieval_strategies"]

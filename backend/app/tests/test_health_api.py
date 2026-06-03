def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "RAGOps" in data["app_name"]


def test_ready_endpoint(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert "status" in response.json()

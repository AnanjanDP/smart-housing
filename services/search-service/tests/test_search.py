from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "search-service"

def test_search_query():
    payload = {
        "query": "studio downtown",
        "limit": 10
    }
    response = client.post("/api/v1/search/query", json=payload)
    assert response.status_code == 200
    assert "results" in response.json()

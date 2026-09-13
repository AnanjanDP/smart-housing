from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "recommendation-service"

def test_get_recommendations():
    response = client.get("/api/v1/recommendations/listings/user-123")
    assert response.status_code == 200
    assert len(response.json()["recommendations"]) > 0

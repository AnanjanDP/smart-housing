def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "search-service"


def test_search_query(client):
    payload = {
        "query": "studio downtown",
        "limit": 10
    }
    response = client.post("/api/v1/search/query", json=payload)
    assert response.status_code == 200
    assert "results" in response.json()


def test_websocket_chat(client):
    with client.websocket_connect("/api/v1/search/ws/chat/test-room") as websocket:
        init_msg = websocket.receive_json()
        assert init_msg["type"] == "connection_established"
        assert init_msg["room_id"] == "test-room"

        websocket.send_json({"text": "Hello world", "sender": "Tester"})
        data = websocket.receive_json()
        assert data["type"] == "chat_message"
        assert data["text"] == "Hello world"
        assert data["sender"] == "Tester"

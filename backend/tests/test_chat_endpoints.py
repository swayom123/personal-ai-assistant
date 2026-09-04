import json
from starlette.testclient import TestClient

def test_chat_endpoint_success(client: TestClient):
    payload = {
        "message": "Hello Aether, system check please.",
        "provider": "mock"
    }
    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["message"]["role"] == "assistant"
    assert len(data["message"]["content"]) > 0
    assert data["conversation_id"] is not None
    assert data["provider"] == "mock"

def test_chat_streaming_endpoint(client: TestClient):
    payload = {
        "message": "Explain FastAPI architecture",
        "provider": "mock",
        "stream": True
    }
    response = client.post("/api/v1/chat/stream", json=payload)
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    
    # Read stream chunks
    lines = [line.strip() for line in response.text.split("\n") if line.strip().startswith("data: ")]
    assert len(lines) > 0
    # First chunk is metadata
    first_event = json.loads(lines[0][6:])
    assert first_event["type"] == "meta"
    assert "conversation_id" in first_event

def test_list_models_endpoint(client: TestClient):
    response = client.get("/api/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert "active_provider" in data
    assert "models" in data
    assert len(data["models"]) > 0

def test_conversations_rest_api(client: TestClient):
    # 1. Create conversation
    create_resp = client.post("/api/v1/conversations", json={"title": "REST API Test Session"})
    assert create_resp.status_code == 201
    conv = create_resp.json()
    conv_id = conv["id"]

    # 2. List conversations
    list_resp = client.get("/api/v1/conversations")
    assert list_resp.status_code == 200
    assert any(c["id"] == conv_id for c in list_resp.json())

    # 3. Rename
    rename_resp = client.patch(f"/api/v1/conversations/{conv_id}", json={"title": "Renamed API Session"})
    assert rename_resp.status_code == 200
    assert rename_resp.json()["title"] == "Renamed API Session"

    # 4. Search
    search_resp = client.get("/api/v1/conversations/search?q=Renamed")
    assert search_resp.status_code == 200
    assert len(search_resp.json()) > 0

    # 5. Delete
    del_resp = client.delete(f"/api/v1/conversations/{conv_id}")
    assert del_resp.status_code == 204

from starlette.testclient import TestClient

def test_root_health_endpoint(client: TestClient):
    """Verify GET /health returns 200 and matches required payload."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "personal-ai-assistant"

def test_versioned_health_endpoint(client: TestClient):
    """Verify GET /api/v1/health returns 200 and matches required payload."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "personal-ai-assistant"

def test_request_id_middleware(client: TestClient):
    """Verify X-Request-ID and X-Process-Time headers are returned."""
    custom_id = "test-custom-request-id-123"
    response = client.get("/health", headers={"X-Request-ID": custom_id})
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == custom_id
    assert "X-Process-Time" in response.headers

def test_generated_request_id(client: TestClient):
    """Verify unique X-Request-ID is generated if not provided."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 0

def test_not_found_handling(client: TestClient):
    """Verify 404 for nonexistent endpoints."""
    response = client.get("/nonexistent-route")
    assert response.status_code == 404

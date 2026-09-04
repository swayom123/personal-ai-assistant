import pytest
from starlette.testclient import TestClient
from backend.app.main import create_app

@pytest.fixture(scope="module")
def client():
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client

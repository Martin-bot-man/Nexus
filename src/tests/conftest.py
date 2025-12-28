import pytest
from fastapi.testclient import TestClient

from src.main import app  # ← API Gateway

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client

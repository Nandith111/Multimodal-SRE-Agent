import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_ingest_log_without_image():
    response = client.post("/ingest", json={"message": "Test routine log message"})
    assert response.status_code == 200
    assert response.json() == {"status": "queued"}

def test_ingest_log_with_image():
    response = client.post("/ingest", json={"message": "Test novel log message", "image_path": "/tmp/test.png"})
    assert response.status_code == 200
    assert response.json() == {"status": "queued"}

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200


def test_review_rejects_empty_code():
    response = client.post("/review", json={"code": ""})
    assert response.status_code == 400


def test_review_rejects_oversized_code():
    response = client.post("/review", json={"code": "x" * 20_000})
    assert response.status_code == 400
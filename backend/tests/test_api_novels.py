from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_novel():
    payload = {"title": "My Novel", "theme": "A space adventure"}
    response = client.post("/novels", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My Novel"
    assert data["status"] == "drafting"

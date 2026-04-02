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


def test_list_chapters_for_novel():
    create_resp = client.post("/novels", json={"title": "T", "theme": "M"})
    novel_id = create_resp.json()["id"]
    response = client.get(f"/novels/{novel_id}/chapters")
    assert response.status_code == 200

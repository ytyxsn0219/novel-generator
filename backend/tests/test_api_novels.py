from unittest import mock
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


def test_generate_novel_settings():
    """Test the settings generation endpoint returns correct response structure."""
    # Mock the LLM client to avoid actual API calls
    mock_settings = {
        "genre": "fantasy",
        "tone": "epic",
        "setting": "medieval world"
    }

    with mock.patch("app.llm.openai_client.OpenAICompatibleClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.generate.return_value = f"```json\n{str(mock_settings).replace(chr(39), chr(34))}\n```"

        # Create a novel first
        create_resp = client.post("/novels", json={"title": "Test Novel", "theme": "A fantasy world"})
        assert create_resp.status_code == 201
        novel_id = create_resp.json()["id"]

        # Call settings endpoint
        response = client.post(f"/novels/{novel_id}/settings")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["title"] == "Test Novel"
        assert "settings" in data


def test_generate_novel_settings_not_found():
    """Test settings endpoint returns 404 for non-existent novel."""
    response = client.post("/novels/00000000-0000-0000-0000-000000000000/settings")
    assert response.status_code == 404

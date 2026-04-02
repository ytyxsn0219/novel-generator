from app.schemas import NovelCreate, SettingsConfirm


def test_novel_create_schema():
    data = NovelCreate(title="Test", theme="theme")
    assert data.title == "Test"


def test_settings_confirm_schema():
    data = SettingsConfirm(settings={"world": "fantasy"})
    assert data.settings["world"] == "fantasy"

import json
from src.whisperdesk.core.settings.settings_manager import SettingsManager, DEFAULTS, SETTINGS_PATH


def test_defaults_used_when_no_file_exists(tmp_path, monkeypatch):
    fake_path = tmp_path / "settings.json"
    monkeypatch.setattr("src.whisperdesk.core.settings.settings_manager.SETTINGS_PATH", fake_path)

    manager = SettingsManager()
    assert manager.settings.whisper_model_size == DEFAULTS["whisper_model_size"]


def test_update_persists_to_disk(tmp_path, monkeypatch):
    fake_path = tmp_path / "settings.json"
    monkeypatch.setattr("src.whisperdesk.core.settings.settings_manager.SETTINGS_PATH", fake_path)

    manager = SettingsManager()
    manager.update(whisper_model_size="small")

    with open(fake_path) as f:
        saved = json.load(f)
    assert saved["whisper_model_size"] == "small"


def test_reload_picks_up_saved_changes(tmp_path, monkeypatch):
    fake_path = tmp_path / "settings.json"
    monkeypatch.setattr("src.whisperdesk.core.settings.settings_manager.SETTINGS_PATH", fake_path)

    manager1 = SettingsManager()
    manager1.update(translation_enabled=False)

    manager2 = SettingsManager()
    assert manager2.settings.translation_enabled is False


def test_unknown_setting_raises_error(tmp_path, monkeypatch):
    fake_path = tmp_path / "settings.json"
    monkeypatch.setattr("src.whisperdesk.core.settings.settings_manager.SETTINGS_PATH", fake_path)

    manager = SettingsManager()
    try:
        manager.update(nonexistent_setting="value")
        assert False, "should have raised ValueError"
    except ValueError:
        pass
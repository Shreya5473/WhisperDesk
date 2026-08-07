"""
User-configurable settings, persisted as JSON.

Centralizes every tunable value (hotkeys, model size, languages)
in one place, with defaults if no settings file exists yet. 
"""

import json
from pathlib import Path
from dataclasses import dataclass, asdict

SETTINGS_PATH = Path.home() / ".whisperdesk" / "settings.json"

DEFAULTS = {
    "dictate_hotkey": "<cmd>+<shift>+<space>",
    "query_hotkey": "<cmd>+<shift>+a",
    "whisper_model_size": "base",
    "translation_target_language": "ar",
    "translation_enabled": True,
}


@dataclass
class Settings:
    dictate_hotkey: str
    query_hotkey: str
    whisper_model_size: str
    translation_target_language: str
    translation_enabled: bool


class SettingsManager:
    def __init__(self):
        self.settings = self._load()

    def _load(self) -> Settings:
        """Load settings from disk, falling back to defaults for
        anything missing (e.g. after an app update adds a new
        setting that doesn't exist in an older saved file)."""
        if SETTINGS_PATH.exists():
            with open(SETTINGS_PATH, "r") as f:
                saved = json.load(f)
        else:
            saved = {}

        # Merge saved values over defaults -- this is what makes
        # adding new settings later safe: old settings.json files
        # won't have the new key, so we fall back to DEFAULTS for it.
        merged = {**DEFAULTS, **saved}
        return Settings(**merged)

    def save(self) -> None:
        SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(SETTINGS_PATH, "w") as f:
            json.dump(asdict(self.settings), f, indent=2)

    def update(self, **kwargs) -> None:
        """Update one or more settings and persist immediately."""
        for key, value in kwargs.items():
            if not hasattr(self.settings, key):
                raise ValueError(f"Unknown setting: {key}")
            setattr(self.settings, key, value)
        self.save()
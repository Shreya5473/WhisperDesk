"""
Settings window 
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QCheckBox, QPushButton, QLineEdit
)
from PyQt6.QtCore import Qt

from src.whisperdesk.core.settings.settings_manager import SettingsManager

MODEL_SIZES = ["tiny", "base", "small", "medium"]
LANGUAGES = {"Arabic": "ar", "Spanish": "es", "French": "fr", "Hindi": "hi"}


class SettingsWindow(QWidget):
    def __init__(self, settings_manager: SettingsManager):
        super().__init__()
        self.settings_manager = settings_manager
        self.setWindowTitle("WhisperDesk Settings")
        self.setFixedWidth(380)
        self.setStyleSheet("""
            QWidget { background-color: #121214; color: white; font-size: 13px; }
            QLabel { color: #cccccc; }
            QLineEdit, QComboBox {
                background-color: #1e1e21; border: 1px solid #333;
                border-radius: 6px; padding: 6px; color: white;
            }
            QPushButton {
                background-color: #FF3B30; border: none; border-radius: 6px;
                padding: 8px 16px; color: white; font-weight: 600;
            }
            QPushButton:hover { background-color: #ff5c52; }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 28)

        title = QLabel("Settings")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: white;")
        layout.addWidget(title)

        settings = self.settings_manager.settings

        # Dictation hotkey
        layout.addWidget(QLabel("Dictation hotkey"))
        self.dictate_input = QLineEdit(settings.dictate_hotkey)
        layout.addWidget(self.dictate_input)

        # Query hotkey
        layout.addWidget(QLabel("Ask-a-question hotkey"))
        self.query_input = QLineEdit(settings.query_hotkey)
        layout.addWidget(self.query_input)

        # Whisper model size
        layout.addWidget(QLabel("Whisper model size (bigger = more accurate, slower)"))
        self.model_dropdown = QComboBox()
        self.model_dropdown.addItems(MODEL_SIZES)
        self.model_dropdown.setCurrentText(settings.whisper_model_size)
        layout.addWidget(self.model_dropdown)

        # Translation
        self.translation_checkbox = QCheckBox("Enable translation")
        self.translation_checkbox.setChecked(settings.translation_enabled)
        layout.addWidget(self.translation_checkbox)

        layout.addWidget(QLabel("Translate to"))
        self.language_dropdown = QComboBox()
        self.language_dropdown.addItems(LANGUAGES.keys())
        current_lang_name = next(
            (name for name, code in LANGUAGES.items() if code == settings.translation_target_language),
            "Arabic",
        )
        self.language_dropdown.setCurrentText(current_lang_name)
        layout.addWidget(self.language_dropdown)

        # Save button + restart notice
        note = QLabel("Changes apply the next time WhisperDesk starts.")
        note.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(note)

        save_button = QPushButton("Save")
        save_button.setMinimumHeight(40)
        save_button.clicked.connect(self._on_save)
        layout.addWidget(save_button)

        layout.addSpacing(8)
        self.adjustSize()

    def _on_save(self) -> None:
        self.settings_manager.update(
            dictate_hotkey=self.dictate_input.text().strip(),
            query_hotkey=self.query_input.text().strip(),
            whisper_model_size=self.model_dropdown.currentText(),
            translation_enabled=self.translation_checkbox.isChecked(),
            translation_target_language=LANGUAGES[self.language_dropdown.currentText()],
        )
        self.close()
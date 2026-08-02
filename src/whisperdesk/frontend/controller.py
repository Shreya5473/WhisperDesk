"""
Bridges background-thread events (hotkey presses, audio levels) into
safe, main-thread GUI updates using Qt's Signal/Slot system.

This is the answer to: "the hotkey listener and audio recorder run
on background threads -- how do we safely update GUI widgets from
there without crashing?" Signals can be emitted from ANY thread;
Qt guarantees the connected slot function runs on the main thread.
"""

from PyQt6.QtCore import QObject, pyqtSignal

from src.whisperdesk.core.audio.recorder import AudioRecorder
from src.whisperdesk.core.transcription.engine import TranscriptionEngine
from src.whisperdesk.core.translation.translator import Translator
from src.whisperdesk.core.snippets.expander import SnippetExpander
from src.whisperdesk.hotkeys.manager import HotkeyManager
from src.whisperdesk.injection.text_injector import TextInjector
from src.whisperdesk.storage.db import get_connection
from src.whisperdesk.storage.history_repository import HistoryRepository
from src.whisperdesk.storage.snippet_repository import SnippetRepository


class AppController(QObject):
    # Signals -- declared at class level, this is Qt's required pattern.
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    level_changed = pyqtSignal(float)
    transcript_ready = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.recorder = AudioRecorder()
        self.recorder.on_level = self._on_level  # background thread

        print("Loading Whisper model...")
        self.engine = TranscriptionEngine(model_size="base")

        print("Loading translator...")
        self.translator = Translator(from_code="en", to_code="ar")

        self.injector = TextInjector()

        self.conn = get_connection()
        self.history = HistoryRepository(self.conn)
        self.snippet_repo = SnippetRepository(self.conn)
        self.expander = SnippetExpander(self.snippet_repo.get_all())

        self.hotkey_manager = HotkeyManager(hotkey="<cmd>+<shift>+<space>")
        self.hotkey_manager.on_activate = self._on_hotkey_press      # background thread
        self.hotkey_manager.on_deactivate = self._on_hotkey_release  # background thread

    def start(self) -> None:
        self.hotkey_manager.start()

    def stop(self) -> None:
        self.hotkey_manager.stop()

    # --- Called on BACKGROUND threads. We only ever emit signals
    # here -- never touch GUI objects directly from these methods. ---

    def _on_hotkey_press(self) -> None:
        self.recorder.start()
        self.recording_started.emit()

    def _on_level(self, level: float) -> None:
        self.level_changed.emit(level)

    def _on_hotkey_release(self) -> None:
        self.recording_stopped.emit()
        audio = self.recorder.stop()

        text_en = self.engine.transcribe(audio, sample_rate=self.recorder.sample_rate)
        text_en = self.expander.expand(text_en)
        text_ar = self.translator.translate(text_en) if text_en else ""

        if text_en:
            self.history.save(text_en, arabic_text=text_ar)
            self.injector.inject(text_en)

        self.transcript_ready.emit(text_en)
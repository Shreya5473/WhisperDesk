"""
Bridges background-thread events (hotkey presses, audio levels) into
safe, main-thread GUI updates using Qt's Signal/Slot system.

Handles TWO hotkeys:
- Dictation hotkey: record -> transcribe -> translate -> inject text
- Query hotkey: record -> transcribe -> RAG search + answer -> inject answer
"""

from PyQt6.QtCore import QObject, pyqtSignal

from src.whisperdesk.core.settings.settings_manager import SettingsManager
from src.whisperdesk.core.audio.recorder import AudioRecorder
from src.whisperdesk.core.transcription.engine import TranscriptionEngine
from src.whisperdesk.core.translation.translator import Translator
from src.whisperdesk.core.snippets.expander import SnippetExpander
from src.whisperdesk.core.rag.pipeline import RAGPipeline
from src.whisperdesk.hotkeys.manager import HotkeyManager
from src.whisperdesk.injection.text_injector import TextInjector
from src.whisperdesk.storage.db import get_connection
from src.whisperdesk.storage.history_repository import HistoryRepository
from src.whisperdesk.storage.snippet_repository import SnippetRepository


class AppController(QObject):
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    level_changed = pyqtSignal(float)
    transcript_ready = pyqtSignal(str)

    query_started = pyqtSignal()
    query_thinking = pyqtSignal()
    query_answered = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.settings_manager = SettingsManager()
        settings = self.settings_manager.settings

        self.recorder = AudioRecorder()
        self.recorder.on_level = self._on_level

        # Tracks which hotkey triggered the current recording, so
        # release logic knows whether to dictate or query.
        self._mode = None

        print("Loading Whisper model...")
        self.engine = TranscriptionEngine(model_size=settings.whisper_model_size)

        print("Loading translator...")
        self.translator = Translator(from_code="en", to_code=settings.translation_target_language)

        self.injector = TextInjector()

        self.conn = get_connection()
        self.history = HistoryRepository(self.conn)
        self.snippet_repo = SnippetRepository(self.conn)
        self.expander = SnippetExpander(self.snippet_repo.get_all())

        print("Loading RAG pipeline...")
        self.rag = RAGPipeline()

        self.dictate_hotkey = HotkeyManager(hotkey=settings.dictate_hotkey)
        self.dictate_hotkey.on_activate = self._on_dictate_press
        self.dictate_hotkey.on_deactivate = self._on_dictate_release

        self.query_hotkey = HotkeyManager(hotkey=settings.query_hotkey)
        self.query_hotkey.on_activate = self._on_query_press
        self.query_hotkey.on_deactivate = self._on_query_release

    def start(self) -> None:
        self.dictate_hotkey.start()
        self.query_hotkey.start()

    def stop(self) -> None:
        self.dictate_hotkey.stop()
        self.query_hotkey.stop()

    def _on_level(self, level: float) -> None:
        self.level_changed.emit(level)

    # --- Dictation hotkey ---

    def _on_dictate_press(self) -> None:
        print("\n[Dictate hotkey pressed] Recording...")
        self._mode = "dictate"
        self.recorder.start()
        self.recording_started.emit()

    def _on_dictate_release(self) -> None:
        if self._mode != "dictate":
            return
        print("[Dictate hotkey released] Transcribing...")
        self.recording_stopped.emit()
        audio = self.recorder.stop()

        text_en = self.engine.transcribe(audio, sample_rate=self.recorder.sample_rate)
        text_en = self.expander.expand(text_en)
        text_ar = ""
        if text_en and self.settings_manager.settings.translation_enabled:
            text_ar = self.translator.translate(text_en)

        print(f"  EN: {text_en}")
        print(f"  AR: {text_ar}")

        if text_en:
            self.history.save(text_en, arabic_text=text_ar)
            self.injector.inject(text_en)

        self.transcript_ready.emit(text_en)
        self._mode = None

    # --- Query (voice RAG) hotkey ---

    def _on_query_press(self) -> None:
        print("\n[Query hotkey pressed] Recording your question...")
        self._mode = "query"
        self.recorder.start()
        self.query_started.emit()

    def _on_query_release(self) -> None:
        if self._mode != "query":
            return
        print("[Query hotkey released] Transcribing question...")
        self.query_thinking.emit()
        audio = self.recorder.stop()

        question = self.engine.transcribe(audio, sample_rate=self.recorder.sample_rate)
        print(f"  Question: {question}")

        if not question.strip():
            self.query_answered.emit("")
            self._mode = None
            return

        answer = self.rag.ask(question)
        print(f"  Answer: {answer}")

        self.injector.inject(answer)
        self.query_answered.emit(answer)
        self._mode = None
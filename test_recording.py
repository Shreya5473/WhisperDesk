import time
from src.whisperdesk.core.audio.recorder import AudioRecorder
from src.whisperdesk.core.transcription.engine import TranscriptionEngine
from src.whisperdesk.core.translation.translator import Translator
from src.whisperdesk.storage.db import get_connection
from src.whisperdesk.storage.history_repository import HistoryRepository
from src.whisperdesk.core.snippets.expander import SnippetExpander
from src.whisperdesk.storage.snippet_repository import SnippetRepository

recorder = AudioRecorder()
print("Loading Whisper model...")
engine = TranscriptionEngine(model_size="base")

print("Loading translator...")
translator = Translator(from_code="en", to_code="ar")

conn = get_connection()
history = HistoryRepository(conn)

snippet_repo = SnippetRepository(conn)

# Seed a couple of snippets the first time (only runs if table is empty)
if not snippet_repo.get_all():
    snippet_repo.add("eml", "shreya@example.com")
    snippet_repo.add("addr", "Dubai, UAE")

expander = SnippetExpander(snippet_repo.get_all())

print("Recording for 5 seconds... speak now!")
recorder.start()
time.sleep(5)
audio = recorder.stop()

print("Transcribing...")
text_en = engine.transcribe(audio, sample_rate=recorder.sample_rate)
print(f"English: {text_en}")

print("Translating...")
text_ar = translator.translate(text_en)
print(f"Arabic:  {text_ar}")

text_en_expanded = expander.expand(text_en)
if text_en_expanded != text_en:
    print(f"Expanded: {text_en_expanded}")

saved = history.save(text_en, arabic_text=text_ar)
print(f"Saved as entry #{saved.id} at {saved.created_at}")

print("\n--- Full history ---")
for entry in history.get_all():
    print(f"[{entry.id}] {entry.created_at} ({entry.word_count} words)")
    print(f"  EN: {entry.text}")
    print(f"  AR: {entry.arabic_text}")
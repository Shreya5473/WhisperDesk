from src.whisperdesk.core.rag.pipeline import RAGPipeline

print("Initializing RAG pipeline (loading models)...")
rag = RAGPipeline()

notes = """
WhisperDesk uses faster-whisper for local, offline speech transcription, avoiding any cloud API dependency for privacy.

For translation between English and Arabic, we use Argos Translate, which also runs fully offline using downloaded language-pair models.

The app stores transcription history and user snippets in SQLite, accessed through a Repository pattern so all SQL lives in dedicated classes.

Global hotkey detection is handled by pynput, and text injection into whatever app is focused uses pynput's keyboard Controller.

The GUI is built with PyQt6, featuring a custom floating overlay with a live animated waveform driven by real-time RMS audio level metering.
"""

print("Adding notes to knowledge base...")
count = rag.add_notes(notes, source_name="whisperdesk_overview")
print(f"Ingested {count} chunks.\n")

questions = [
    "What library handles the global hotkey?",
    "How does the app store data?",
    "What GUI framework is used and what does the overlay show?",
]

for q in questions:
    print(f"Q: {q}")
    answer = rag.ask(q)
    print(f"A: {answer}\n")
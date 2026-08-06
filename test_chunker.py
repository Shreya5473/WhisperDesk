from src.whisperdesk.core.rag.chunker import chunk_text

long_text = """
The WhisperDesk project began as a way to build a local-first dictation app similar to VoiceInk. It uses faster-whisper for transcription, running entirely on-device with no cloud dependency.

For translation, we integrated Argos Translate, which downloads small language-pair models and runs offline. This keeps the "privacy-focused" pitch consistent across every feature.

The database layer uses SQLite via a Repository pattern, storing transcription history and user-defined snippets. All SQL lives in dedicated repository classes rather than being scattered across the app.

For the GUI, we chose PyQt6, building a custom floating overlay with a live animated waveform that reacts to microphone input in real time, along with a system tray icon for background operation.
"""

chunks = chunk_text(long_text, chunk_size=200, overlap=30)

print(f"Total chunks: {len(chunks)}\n")
for i, chunk in enumerate(chunks):
    print(f"--- Chunk {i} ({len(chunk)} chars) ---")
    print(chunk)
    print()
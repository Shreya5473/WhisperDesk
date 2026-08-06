from src.whisperdesk.core.rag.embeddings import EmbeddingModel
from src.whisperdesk.core.rag.vector_store import VectorStore
from src.whisperdesk.core.rag.ingestion import DocumentIngester

print("Loading embedding model...")
model = EmbeddingModel()
store = VectorStore(collection_name="test_ingestion")
ingester = DocumentIngester(model, store)

document = """
The WhisperDesk project began as a way to build a local-first dictation app similar to VoiceInk. It uses faster-whisper for transcription, running entirely on-device with no cloud dependency.

For translation, we integrated Argos Translate, which downloads small language-pair models and runs offline.

The database layer uses SQLite via a Repository pattern, storing transcription history and user-defined snippets.
"""

print("Ingesting document...")
num_chunks = ingester.ingest(document, source_name="whisperdesk_notes")
print(f"Ingested {num_chunks} chunks. Total in store: {store.count()}")

# Re-ingest the SAME document to prove no duplicates get created
num_chunks_again = ingester.ingest(document, source_name="whisperdesk_notes")
print(f"Re-ingested {num_chunks_again} chunks. Total in store: {store.count()}")
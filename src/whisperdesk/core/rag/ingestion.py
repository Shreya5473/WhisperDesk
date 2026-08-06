"""
Document ingestion pipeline: chunk -> embed -> store.

This is the "write" side of RAG -- turning a raw document into
searchable chunks in the vector store. 
"""

import hashlib

from src.whisperdesk.core.rag.chunker import chunk_text
from src.whisperdesk.core.rag.embeddings import EmbeddingModel
from src.whisperdesk.core.rag.vector_store import VectorStore


class DocumentIngester:
    def __init__(self, embedding_model: EmbeddingModel, vector_store: VectorStore):
        self.embedding_model = embedding_model
        self.vector_store = vector_store

    def ingest(self, document_text: str, source_name: str = "note") -> int:
        """
        Chunks, embeds, and stores a document. Returns the number of
        chunks created.
        """
        chunks = chunk_text(document_text)
        if not chunks:
            return 0

        embeddings = self.embedding_model.embed_batch(chunks)

        chunk_ids = [
            hashlib.sha256(f"{source_name}::{i}".encode()).hexdigest()[:16]
            for i in range(len(chunks))
        ]

        self.vector_store.add_chunks(chunk_ids, chunks, embeddings)
        return len(chunks)
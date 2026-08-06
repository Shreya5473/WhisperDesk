"""
Vector storage and similarity search using ChromaDB.

"""

import chromadb
from pathlib import Path

DB_PATH = Path.home() / ".whisperdesk" / "vector_store"


class VectorStore:
    def __init__(self, collection_name: str = "notes"):

        DB_PATH.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(DB_PATH))
        self.collection = self.client.get_or_create_collection(collection_name)

    def add_chunk(self, chunk_id: str, text: str, embedding: list[float]) -> None:
        """Store one chunk with its precomputed embedding."""
        self.collection.add(
            ids=[chunk_id],
            documents=[text],
            embeddings=[embedding],
        )

    def add_chunks(self, chunk_ids: list[str], texts: list[str], embeddings: list[list[float]]) -> None:
        """Store many chunks at once -- more efficient than looping add_chunk."""
        self.collection.add(
            ids=chunk_ids,
            documents=texts,
            embeddings=embeddings,
        )

    def search(self, query_embedding: list[float], top_k: int = 3) -> list[dict]:
        """Find the top_k stored chunks most similar to the query
        embedding. Returns them ranked closest-match first."""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )
        chunks = []
        for i in range(len(results["ids"][0])):
            chunks.append({
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "distance": results["distances"][0][i],
            })
        return chunks

    def count(self) -> int:
        return self.collection.count()
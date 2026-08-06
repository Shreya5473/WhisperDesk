from src.whisperdesk.core.rag.embeddings import EmbeddingModel
from src.whisperdesk.core.rag.vector_store import VectorStore


class Retriever:
    def __init__(self, embedding_model: EmbeddingModel, vector_store: VectorStore):
        self.embedding_model = embedding_model
        self.vector_store = vector_store

    def retrieve(self, query: str, top_k: int = 3) -> list[str]:
        """Returns the top_k most relevant chunk texts for a query,
        ranked most-relevant first."""
        query_embedding = self.embedding_model.embed(query)
        results = self.vector_store.search(query_embedding, top_k=top_k)
        return [r["text"] for r in results]
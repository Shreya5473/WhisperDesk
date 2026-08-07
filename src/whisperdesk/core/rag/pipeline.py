"""
The full RAG pipeline, combined into one simple interface: ask a
question, get a grounded answer. 
"""

from src.whisperdesk.core.rag.embeddings import EmbeddingModel
from src.whisperdesk.core.rag.vector_store import VectorStore
from src.whisperdesk.core.rag.ingestion import DocumentIngester
from src.whisperdesk.core.rag.retriever import Retriever
from src.whisperdesk.core.rag.generator import AnswerGenerator


class RAGPipeline:
    def __init__(self):
        self.embedding_model = EmbeddingModel()
        self.vector_store = VectorStore(collection_name="notes")
        self.ingester = DocumentIngester(self.embedding_model, self.vector_store)
        self.retriever = Retriever(self.embedding_model, self.vector_store)
        self.generator = AnswerGenerator()

    def add_notes(self, text: str, source_name: str = "note") -> int:
        """Ingest a document into the knowledge base. Returns chunk count."""
        return self.ingester.ingest(text, source_name=source_name)

    def ask(self, question: str, top_k: int = 3) -> str:
        """Ask a question against everything ingested so far."""
        chunks = self.retriever.retrieve(question, top_k=top_k)
        return self.generator.generate_answer(question, chunks)
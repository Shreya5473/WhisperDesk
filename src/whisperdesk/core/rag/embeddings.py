"""
Text embedding generation.

Converts text into a vector that captures its
semantic meaning, using a small local sentence-transformer model.
"""

from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        all-MiniLM-L6-v2: a small (~80MB), fast, well-regarded model. 
        Produces 384-number vectors per chunk of
        text. 
        """
        self.model = SentenceTransformer(model_name)

    def embed(self, text: str) -> list[float]:
        """Convert a single piece of text into its embedding vector."""
        vector = self.model.encode(text)
        return vector.tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(texts)
        return vectors.tolist()
from src.whisperdesk.core.rag.embeddings import EmbeddingModel

print("Loading embedding model (first run downloads it)...")
model = EmbeddingModel()

text1 = "The database schema needs a users table"
text2 = "We decided to add a table for storing user accounts"
text3 = "The weather today is sunny and warm"

vec1 = model.embed(text1)
vec2 = model.embed(text2)
vec3 = model.embed(text3)

print(f"Vector length: {len(vec1)}")  # should print 384

# Cosine similarity: measures how "close" two vectors point in the
# same direction. 1.0 = identical meaning, 0 = unrelated, -1 = opposite.
import numpy as np

def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

print(f"Similarity (text1 vs text2, related): {cosine_similarity(vec1, vec2):.3f}")
print(f"Similarity (text1 vs text3, unrelated): {cosine_similarity(vec1, vec3):.3f}")

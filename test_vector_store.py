from src.whisperdesk.core.rag.embeddings import EmbeddingModel
from src.whisperdesk.core.rag.vector_store import VectorStore

print("Loading embedding model...")
model = EmbeddingModel()
store = VectorStore()

notes = [
    "The database uses PostgreSQL with a users table and a posts table.",
    "We're deploying the app using Docker containers on AWS.",
    "The frontend is built with React and TypeScript.",
    "Meeting notes: decided to use JWT tokens for authentication.",
]

print("Embedding and storing notes...")
embeddings = model.embed_batch(notes)
ids = [f"note_{i}" for i in range(len(notes))]
store.add_chunks(ids, notes, embeddings)

print(f"Total chunks stored: {store.count()}")

query = "What database are we using?"
print(f"\nQuery: {query}")
query_embedding = model.embed(query)
results = store.search(query_embedding, top_k=2)

print("\nTop matches:")
for r in results:
    print(f"  [{r['distance']:.3f}] {r['text']}")
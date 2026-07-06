from app.services.chunking.chunker import ChunkBuilder
from app.services.embeddings.service import EmbeddingService
from app.services.vectorstore.collection import CollectionManager
from app.services.vectorstore.qdrant import QdrantService
from app.services.repository.repository import analyze_repository

repo_id = "test"

repository_root = "C:/Users/Hafsa/ai_proj_architect/backend/extracted/2e842df4-561f-4281-8196-2dc73e7735f6"

repository = analyze_repository(repository_root)

builder = ChunkBuilder()

chunks = builder.build_chunks(
    repo_id,
    repository_root,
    repository["files"]
)

embedding_service = EmbeddingService()

embedded = embedding_service.embed_chunks(chunks)

manager = CollectionManager()

vector_size = len(embedded[0]["embedding"])

manager.create_collection(vector_size)

qdrant = QdrantService()

count = qdrant.upsert_chunks(embedded)

print(f"Stored {count} chunks.")
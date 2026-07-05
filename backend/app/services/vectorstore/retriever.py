from app.core.config import COLLECTION_NAME
from app.services.embeddings.service import EmbeddingService
from app.services.vectorstore.qdrant import QdrantService


class RepositoryRetriever:

    def __init__(self):

        self.embedding_service = EmbeddingService()

        self.qdrant = QdrantService()

    def retrieve(
        self,
        query: str,
        repository_id: str,
        limit: int = 5
    ):

        query_vector = self.embedding_service.provider.embed(
            query
        )

        results = self.qdrant.search(
            vector=query_vector,
            repository_id=repository_id,
            limit=limit
        )

        return results
from qdrant_client import QdrantClient
from qdrant_client.models import Distance
from qdrant_client.models import VectorParams

from app.core.config import (
    QDRANT_URL,
    QDRANT_API_KEY,
    COLLECTION_NAME
)


class CollectionManager:

    def __init__(self):

        self.client = QdrantClient(
             url=QDRANT_URL,
             api_key=QDRANT_API_KEY
        )

    def create_collection(
        self,
        vector_size: int
    ):

        collections = self.client.get_collections()

        names = [

            collection.name

            for collection in collections.collections

        ]

        if COLLECTION_NAME in names:
            return

        self.client.create_collection(

            collection_name=COLLECTION_NAME,

            vectors_config=VectorParams(

                size=vector_size,

                distance=Distance.COSINE

            )

        )

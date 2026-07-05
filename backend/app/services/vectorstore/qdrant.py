from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from qdrant_client.models import Filter
from qdrant_client.models import FieldCondition
from qdrant_client.models import MatchValue

from app.core.config import (
    QDRANT_HOST,
    QDRANT_PORT,
    COLLECTION_NAME
)


class QdrantService:

    def __init__(self):

        self.client = QdrantClient(
            host=QDRANT_HOST,
            port=QDRANT_PORT
        )
    def search(
    self,
    vector,
    repository_id,
    limit=5
    ):

        results = self.client.query_points(

            collection_name=COLLECTION_NAME,

            query=vector,

            limit=limit,

            query_filter=Filter(

                must=[

                    FieldCondition(

                        key="repository_id",

                        match=MatchValue(
                            value=repository_id
                        )

                    )

                ]

            )

        )

        return results.points



    def upsert_chunks(
        self,
        embedded_chunks: list
    ):

        points = []

        for item in embedded_chunks:

            chunk = item["chunk"]

            embedding = item["embedding"]

            points.append(

                PointStruct(

                    id=chunk.id,

                    vector=embedding,

                    payload={

                        "repository_id": chunk.repository_id,

                        "path": chunk.path,

                        "language": chunk.language,

                        "chunk_type": chunk.chunk_type,

                        "name": chunk.name,

                        "content": chunk.content,

                        "metadata": chunk.metadata

                    }

                )

            )

        self.client.upsert(

            collection_name=COLLECTION_NAME,

            points=points

        )

        return len(points)
    
    
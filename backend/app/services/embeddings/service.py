from app.models.chunk import CodeChunk
from app.services.embeddings.huggingface import (
    HuggingFaceEmbeddingProvider,
)


class EmbeddingService:

    def __init__(self):

        self.provider = HuggingFaceEmbeddingProvider()

    def embed_chunks(
        self,
        chunks: list[CodeChunk]
    ):

        embeddings = self.provider.embed_batch(
            [chunk.content for chunk in chunks]
        )

        return [

            {
                "chunk": chunk,
                "embedding": embedding
            }

            for chunk, embedding in zip(
                chunks,
                embeddings
            )

        ]
from huggingface_hub import InferenceClient

from app.core.config import HF_TOKEN
from app.services.embeddings.provider import EmbeddingProvider


class HuggingFaceEmbeddingProvider(EmbeddingProvider):

    def __init__(self):

        self.client = InferenceClient(
            provider="hf-inference",
            api_key=HF_TOKEN
        )

        self.model = "BAAI/bge-base-en-v1.5"

    def embed(self, text: str) -> list[float]:

        embedding = self.client.feature_extraction(
            text,
            model=self.model
        )

        return embedding

    def embed_batch(self, texts: list[str]) -> list[list[float]]:

        return [
            self.embed(text)
            for text in texts
        ]
"""
Thin async wrapper around the Ollama HTTP API.

Ollama is free, open-source, and runs any of the open vision/text/embedding
models (Qwen2.5-VL, LLaVA, Llama 3.1, nomic-embed-text, ...) fully offline
on the machine that hosts it. This client just talks to that local server.
"""
import base64
import logging
from typing import List, Optional

import httpx

from app.config import settings

logger = logging.getLogger("pixelrag.ollama")


class OllamaError(RuntimeError):
    pass


class OllamaClient:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")

    async def _post(self, path: str, payload: dict, timeout: float = 120.0) -> dict:
        url = f"{self.base_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPError as e:
            logger.error("Ollama request failed: %s", e)
            raise OllamaError(f"Ollama request to {path} failed: {e}") from e

    async def describe_image(self, image_base64: str, prompt: Optional[str] = None) -> str:
        """Run the vision model over a screenshot and return extracted text/description."""
        prompt = prompt or (
            "You are reading a screenshot of a web page. Transcribe all readable "
            "text verbatim where possible, then give a short structural summary "
            "(headings, main content, any prices/dates/key facts). Be thorough "
            "and factual; do not invent content that is not visible."
        )
        payload = {
            "model": settings.ollama_vision_model,
            "prompt": prompt,
            "images": [image_base64],
            "stream": False,
        }
        data = await self._post("/api/generate", payload, timeout=180.0)
        return data.get("response", "").strip()

    async def embed(self, text: str) -> List[float]:
        payload = {"model": settings.ollama_embed_model, "prompt": text}
        data = await self._post("/api/embeddings", payload, timeout=60.0)
        embedding = data.get("embedding")
        if not embedding:
            raise OllamaError("Ollama returned no embedding")
        return embedding

    async def chat_answer(self, question: str, context: str) -> str:
        system = (
            "You are PixelRAG, an assistant that answers questions using ONLY "
            "the provided context extracted from web pages the user has captured. "
            "If the answer is not contained in the context, say you don't know. "
            "Cite which page a fact came from when possible."
        )
        payload = {
            "model": settings.ollama_text_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
            ],
            "stream": False,
        }
        data = await self._post("/api/chat", payload, timeout=120.0)
        message = data.get("message", {})
        return message.get("content", "").strip()

    @staticmethod
    def validate_base64_image(image_base64: str, max_size_mb: int) -> bytes:
        try:
            raw = base64.b64decode(image_base64, validate=True)
        except Exception as e:
            raise ValueError("Invalid base64 image data") from e
        if len(raw) > max_size_mb * 1024 * 1024:
            raise ValueError(f"Image exceeds {max_size_mb}MB limit")
        return raw


ollama_client = OllamaClient()

"""
Multi-tenant vector store on top of Chroma (free, embedded, open source).
Every user's chunks live in the same collection but are always filtered by
user_id, so one user can never retrieve another user's data.
"""
import logging
from typing import List, Dict, Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings

logger = logging.getLogger("pixelrag.vectorstore")

_client = chromadb.PersistentClient(
    path=settings.chroma_persist_dir,
    settings=ChromaSettings(anonymized_telemetry=False),
)
_collection = _client.get_or_create_collection(name="pixelrag_chunks")


def add_chunks(
    user_id: str,
    page_id: str,
    url: str,
    title: str,
    chunks: List[str],
    embeddings: List[List[float]],
) -> None:
    if not chunks:
        return
    ids = [f"{page_id}:{i}" for i in range(len(chunks))]
    metadatas = [
        {"user_id": user_id, "page_id": page_id, "url": url, "title": title or ""}
        for _ in chunks
    ]
    _collection.add(ids=ids, documents=chunks, embeddings=embeddings, metadatas=metadatas)


def delete_page(page_id: str) -> None:
    _collection.delete(where={"page_id": page_id})


def query(
    user_id: str,
    query_embedding: List[float],
    top_k: int = 5,
    page_id: str | None = None,
) -> List[Dict[str, Any]]:
    where: Dict[str, Any] = {"user_id": user_id}
    if page_id:
        where = {"$and": [{"user_id": user_id}, {"page_id": page_id}]}

    result = _collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where,
    )
    out = []
    docs = result.get("documents", [[]])[0]
    metas = result.get("metadatas", [[]])[0]
    dists = result.get("distances", [[]])[0]
    for doc, meta, dist in zip(docs, metas, dists):
        out.append({
            "text": doc,
            "page_id": meta.get("page_id"),
            "url": meta.get("url"),
            "title": meta.get("title"),
            "score": 1.0 - dist,  # cosine distance -> similarity-ish score
        })
    return out

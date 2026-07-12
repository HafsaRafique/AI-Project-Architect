import logging
from typing import List

from sqlalchemy.orm import Session

from app import models
from app.services.ollama_client import ollama_client, OllamaError
from app.services import vectorstore

logger = logging.getLogger("pixelrag.rag")

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    text = text.strip()
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap
    return chunks


async def process_page(db: Session, page_id: str, image_base64: str) -> None:
    """Background job: run the vision model, chunk + embed the result, store it."""
    page = db.query(models.Page).filter(models.Page.id == page_id).first()
    if page is None:
        return

    page.status = models.PageStatus.processing
    db.commit()

    try:
        extracted = await ollama_client.describe_image(image_base64)
        chunks = chunk_text(extracted)
        embeddings = [await ollama_client.embed(c) for c in chunks]

        vectorstore.add_chunks(
            user_id=page.user_id,
            page_id=page.id,
            url=page.url,
            title=page.title or "",
            chunks=chunks,
            embeddings=embeddings,
        )

        page.extracted_text = extracted
        page.chunk_count = len(chunks)
        page.status = models.PageStatus.done
        page.error = None
    except OllamaError as e:
        logger.exception("Failed to process page %s", page_id)
        page.status = models.PageStatus.failed
        page.error = str(e)
    finally:
        db.commit()


async def answer_question(
    user_id: str, question: str, top_k: int = 5, page_id: str | None = None
) -> dict:
    query_embedding = await ollama_client.embed(question)
    results = vectorstore.query(user_id, query_embedding, top_k=top_k, page_id=page_id)

    if not results:
        return {
            "answer": "I don't have any captured pages matching that question yet.",
            "sources": [],
        }

    context = "\n\n".join(
        f"[Source: {r['title'] or r['url']}]\n{r['text']}" for r in results
    )
    answer = await ollama_client.chat_answer(question, context)

    sources = [
        {
            "page_id": r["page_id"],
            "url": r["url"],
            "title": r["title"],
            "snippet": r["text"][:280],
            "score": round(float(r["score"]), 4),
        }
        for r in results
    ]
    return {"answer": answer, "sources": sources}

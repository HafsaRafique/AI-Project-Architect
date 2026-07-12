from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import get_db, SessionLocal
from app.deps import get_current_user
from app.config import settings
from app.services.ollama_client import OllamaClient
from app.services import rag, vectorstore

router = APIRouter(prefix="/pages", tags=["pages"])


def _run_process_page_job(page_id: str, image_base64: str) -> None:
    """Wrapper to give the background task its own DB session + event loop."""
    import asyncio
    db = SessionLocal()
    try:
        asyncio.run(rag.process_page(db, page_id, image_base64))
    finally:
        db.close()


@router.post("", response_model=schemas.PageOut, status_code=status.HTTP_202_ACCEPTED)
def capture_page(
    payload: schemas.PageCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        OllamaClient.validate_base64_image(payload.image_base64, settings.max_image_size_mb)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    page = models.Page(
        user_id=current_user.id,
        url=payload.url,
        title=payload.title,
        status=models.PageStatus.pending,
    )
    db.add(page)
    db.commit()
    db.refresh(page)

    background_tasks.add_task(_run_process_page_job, page.id, payload.image_base64)
    return page


@router.get("", response_model=List[schemas.PageListOut])
def list_pages(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    limit: int = 50,
):
    return (
        db.query(models.Page)
        .filter(models.Page.user_id == current_user.id)
        .order_by(models.Page.created_at.desc())
        .limit(limit)
        .all()
    )


@router.get("/{page_id}", response_model=schemas.PageOut)
def get_page(
    page_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    page = (
        db.query(models.Page)
        .filter(models.Page.id == page_id, models.Page.user_id == current_user.id)
        .first()
    )
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page


@router.delete("/{page_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_page(
    page_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    page = (
        db.query(models.Page)
        .filter(models.Page.id == page_id, models.Page.user_id == current_user.id)
        .first()
    )
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    vectorstore.delete_page(page_id)
    db.delete(page)
    db.commit()
    return None

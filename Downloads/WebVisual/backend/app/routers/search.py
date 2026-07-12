from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user
from app.services import rag
from app.services.ollama_client import OllamaError

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/ask", response_model=schemas.AskResponse)
async def ask(
    payload: schemas.AskRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if payload.page_id:
        page = (
            db.query(models.Page)
            .filter(models.Page.id == payload.page_id, models.Page.user_id == current_user.id)
            .first()
        )
        if not page:
            raise HTTPException(status_code=404, detail="Page not found")

    try:
        result = await rag.answer_question(
            user_id=current_user.id,
            question=payload.question,
            top_k=payload.top_k,
            page_id=payload.page_id,
        )
    except OllamaError as e:
        raise HTTPException(status_code=503, detail=f"Model backend unavailable: {e}")

    return result

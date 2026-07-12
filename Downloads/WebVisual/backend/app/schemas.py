from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator



class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
    id: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# 
class PageCreate(BaseModel):
    url: str
    title: Optional[str] = None
    image_base64: str  # data URI or raw base64 PNG/JPEG

    @field_validator("image_base64")
    @classmethod
    def strip_data_uri(cls, v: str) -> str:
        if v.startswith("data:"):
            return v.split(",", 1)[-1]
        return v


class PageOut(BaseModel):
    id: str
    url: str
    title: Optional[str]
    status: str
    extracted_text: Optional[str]
    error: Optional[str]
    chunk_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class PageListOut(BaseModel):
    id: str
    url: str
    title: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---- Search / RAG ----
class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)
    page_id: Optional[str] = None  # restrict to a single page if provided


class SourceChunk(BaseModel):
    page_id: str
    url: str
    title: Optional[str]
    snippet: str
    score: float


class AskResponse(BaseModel):
    answer: str
    sources: List[SourceChunk]

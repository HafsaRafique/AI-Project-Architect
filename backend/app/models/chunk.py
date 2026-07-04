from pydantic import BaseModel
from typing import Any


class CodeChunk(BaseModel):
    id: str

    repository_id: str

    path: str

    language: str

    chunk_type: str

    name: str

    content: str

    metadata: dict[str, Any]
from fastapi import APIRouter, HTTPException
import os

router = APIRouter()


@router.get("/{repository_id}")
def get_file(
    repository_id: str,
    path: str
):

    file_path = os.path.join(
        "extracted",
        repository_id,
        path
    )

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as f:

        content = f.read()

    return {
        "content": content
    }
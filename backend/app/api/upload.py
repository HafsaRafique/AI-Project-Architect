from fastapi import APIRouter, File, UploadFile
from app.services.repository.extractor import save_and_extract_zip
router = APIRouter(
    prefix = "/api",
    tags = ["Upload"]
)
@router.post("upload/")
async def upload_repository(file: UploadFile = File(...)):
    return await save_and_extract_zip(file)
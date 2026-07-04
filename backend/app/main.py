from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.upload import router as upload_router

app = FastAPI(
    title="CodeArchitect AI",
    version="0.1.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
@app.get("/")
async def root():
    return{
        "status": "running",
        "project": "CodeArchitectAI"
    }
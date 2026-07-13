from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.upload import router as upload_router
from app.api.chat import router as chat_router
from app.api.file import router as file_router
from app.api import graph

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
app.include_router(graph.router)

@app.get("/")
async def root():
    return{
        "status": "running",
        "project": "CodeArchitectAI"
    }



app.include_router(
    file_router,
    prefix="/api/file",
    tags=["Files"]
)
app.include_router(
    chat_router,
    prefix="/api/chat",
    tags=["Chat"]
)

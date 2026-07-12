from fastapi import APIRouter

from app.models.chat import ChatRequest
from app.services.agents.supervisor import SupervisorAgent
from fastapi.responses import FileResponse
from app.services.pdf import generate_documentation_pdf

router = APIRouter()

supervisor = SupervisorAgent()

@router.post("/")
async def chat(request: ChatRequest):

    agent = supervisor.route(
        request.question
    )

    answer = supervisor.chat(
        request.repository_id,
        request.question
    )

    response = {

        "agent": agent,

        "answer": answer

    }

    if agent == "documentation":

        pdf = generate_documentation_pdf(
            answer,
            request.repository_id
        )

        response["pdf"] = pdf

    return response

@router.get("/download/{repository_id}")
async def download(repository_id: str):

    return FileResponse(
        f"generated/{repository_id}.pdf",
        media_type="application/pdf",
        filename="Repository_Documentation.pdf"
    )
from fastapi import APIRouter

from app.models.chat import ChatRequest
from app.services.agents.supervisor import SupervisorAgent

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

    return {

        "agent": agent,

        "answer": answer

    }
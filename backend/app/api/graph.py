from fastapi import APIRouter
from app.services.agents.repository_agent import RepositoryAgent

router = APIRouter(
    prefix="/api/graph",
    tags=["graph"]
)


@router.post("/analyze-node")
async def analyze_node(data: dict):

    repository_id = data["repository_id"]
    file_path = data["file_path"]

    agent = RepositoryAgent()

    result = agent.chat(
        repository_id,
        f"""
Analyze this file:

{file_path}

Explain:
- purpose
- responsibilities
- important functions
- dependencies
- possible problems
"""
    )

    return {
        "analysis": result
    }
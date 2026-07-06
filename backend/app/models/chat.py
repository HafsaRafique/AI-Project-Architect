from pydantic import BaseModel


class ChatRequest(BaseModel):

    repository_id: str

    question: str

class ChatResponse(BaseModel):

    agent: str

    answer: str
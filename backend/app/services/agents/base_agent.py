from app.services.vectorstore.retriever import RepositoryRetriever
from app.services.llm.service import LLMService


class BaseAgent:

    def __init__(self):

        self.retriever = RepositoryRetriever()
        self.llm = LLMService()

    def retrieve(
        self,
        repository_id: str,
        question: str,
        limit: int = 5
    ):

        return self.retriever.retrieve(
            query=question,
            repository_id=repository_id,
            limit=limit
        )

    def generate(
        self,
        prompt: str
    ):

        return self.llm.generate(prompt)
from app.services.llm.service import LLMService

from app.services.prompts.router import build_router_prompt

from app.services.agents.repository_agent import RepositoryAgent
from app.services.agents.architecture_agent import ArchitectureAgent
from app.services.agents.documentation_agent import DocumentationAgent
from app.services.agents.review_agent import ReviewAgent


class SupervisorAgent:

    def __init__(self):

        self.llm = LLMService()

        self.repository = RepositoryAgent()

        self.architecture = ArchitectureAgent()

        self.review_agent = ReviewAgent()

        self.documentation_agent = DocumentationAgent()

    def route(self, question: str):

        prompt = build_router_prompt(question)

        result = self.llm.generate_json(prompt)

        return result["agent"]

    def chat(
        self,
        repository_id,
        question
    ):

        agent = self.route(question)

        print(f"Routing to {agent}")

        if agent == "architecture":

            return self.architecture.chat(
                repository_id,
                question
            )

        elif agent == "review":
            return self.review_agent.answer(
                repository_id,
                question
            )
        
        elif agent == "documentation":

            return self.documentation_agent.answer(
                repository_id,
                question
            )
        return self.repository.chat(
            repository_id,
            question
        )
from app.services.agents.base_agent import BaseAgent
from app.services.prompts.documentation import build_documentation_prompt


class DocumentationAgent(BaseAgent):

    def answer(self, repository_id: str, question: str):

        chunks = self.retrieve(
            repository_id,
            question,
            limit=10
        )

        context = "\n\n".join(
            chunk.payload["content"]
            for chunk in chunks
        )

        prompt = build_documentation_prompt(
            context,
            question
        )

        return self.generate(prompt)
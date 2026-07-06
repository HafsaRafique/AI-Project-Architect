from app.services.agents.base_agent import BaseAgent
from app.services.prompts.review import build_review_prompt


class ReviewAgent(BaseAgent):

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

        prompt = build_review_prompt(
            context,
            question
        )

        return self.generate(prompt)
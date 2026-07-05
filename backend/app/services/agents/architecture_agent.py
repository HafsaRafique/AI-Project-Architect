from app.services.agents.base_agent import BaseAgent
from app.services.prompts.architecture import build_architecture_prompt


class ArchitectureAgent(BaseAgent):

    def chat(
        self,
        repository_id: str,
        question: str
    ):

        chunks = self.retrieve(
            repository_id,
            question,
            limit=8
        )

        prompt = build_architecture_prompt(
            question,
            chunks
        )

        answer = self.generate(prompt)

        return {
            "agent": "architecture",
            "answer": answer,
            "sources": [
                {
                    "path": chunk.payload["path"],
                    "name": chunk.payload["name"],
                    "score": float(chunk.score)
                }
                for chunk in chunks
            ]
        }
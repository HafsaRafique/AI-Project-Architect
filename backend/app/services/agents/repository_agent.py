from app.services.agents.base_agent import BaseAgent
from app.services.prompts.chat import build_chat_prompt


class RepositoryAgent(BaseAgent):

    def chat(
        self,
        repository_id: str,
        question: str
    ):

        chunks = self.retrieve(
            repository_id,
            question
        )

        prompt = build_chat_prompt(
            question,
            chunks
        )

        answer = self.generate(prompt)
        print("Retrieved chunks:", len(chunks))

        for chunk in chunks:
            print(chunk.payload["path"])
        return {
            "agent": "repository",
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
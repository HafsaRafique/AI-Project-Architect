from app.services.llm.huggingface import (
    HuggingFaceLLMProvider
)
import json

class LLMService:

    def __init__(self):

        self.provider = HuggingFaceLLMProvider()

    def generate_json(self, prompt: str):

        response = self.generate(prompt)

        return json.loads(response)


    def generate(
        self,
        prompt: str
    ) -> str:

        return self.provider.generate(prompt)
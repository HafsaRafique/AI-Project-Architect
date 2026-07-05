from app.services.llm.huggingface import (
    HuggingFaceLLMProvider
)
import json
import re

class LLMService:

    def __init__(self):

        self.provider = HuggingFaceLLMProvider()

    def generate_json(self, prompt: str):

        response = self.generate(prompt)

        print("RAW RESPONSE:")
        print(response)

        # Remove all markdown
        response = re.sub(r"```(?:json)?", "", response, flags=re.IGNORECASE)

        response = response.strip()

        # Find first JSON object
        match = re.search(r"\{[\s\S]*?\}", response)

        if not match:
            raise ValueError(f"No JSON found:\n{response}")

        return json.loads(match.group(0))


    def generate(
        self,
        prompt: str
    ) -> str:

        return self.provider.generate(prompt)
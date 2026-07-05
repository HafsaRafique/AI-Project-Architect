from huggingface_hub import InferenceClient

from app.core.config import HF_TOKEN
from app.services.llm.provider import LLMProvider


class HuggingFaceLLMProvider(LLMProvider):

    def __init__(self):

        self.client = InferenceClient(
            api_key=HF_TOKEN
        )

        # 
        self.model = "Qwen/Qwen2.5-Coder-32B-Instruct"

    def generate(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 1024
    ) -> str:

        response = self.client.chat.completions.create(

            model=self.model,

            messages=[
                {
                    "role": "system",
                    "content":
                    "You are an expert software architect."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=temperature,

            max_tokens=max_tokens
        )

        return response.choices[0].message.content
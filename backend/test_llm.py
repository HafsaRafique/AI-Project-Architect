from app.services.llm.service import LLMService

llm = LLMService()

response = llm.generate(
    """
Explain what a REST API is in two sentences.
    """
)

print(response)
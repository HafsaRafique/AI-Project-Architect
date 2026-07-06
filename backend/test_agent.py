from app.services.agents.repository_agent import RepositoryAgent


REPOSITORY_ID = "test"

agent = RepositoryAgent()

questions = [
    "Explain the repository.",
    "How does the server start?",
    "What does llm_client.py do?",
    "What are the main functions?",
    "How are moves processed?"
]

for question in questions:

    print("=" * 80)
    print("QUESTION:")
    print(question)
    
    

    answer = agent.chat(
        repository_id=REPOSITORY_ID,
        question=question
    )

    print("\nANSWER:")
    print(answer)
    print()
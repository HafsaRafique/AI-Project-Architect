from app.services.agents.review_agent import ReviewAgent

repo_id = "test"

agent = ReviewAgent()

questions = [
    "Review this repository.",
    "Find potential bugs.",
    "Suggest improvements.",
    "What are the biggest code smells?",
    "Is this project production ready?",
    "Are there any security issues?"
]

for q in questions:
    print("=" * 80)
    print("QUESTION:", q)
    print("=" * 80)
    print(agent.answer(repo_id, q))
    print()
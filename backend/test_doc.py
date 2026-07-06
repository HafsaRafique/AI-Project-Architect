from app.services.agents.documentation_agent import DocumentationAgent

repo_id = "test"

agent = DocumentationAgent()

questions = [

    "Generate a README for this repository.",

    "Document this project.",

    "Explain the architecture.",

    "Describe the folder structure.",

    "Write onboarding documentation."

]

for q in questions:

    print("=" * 80)
    print(q)
    print("=" * 80)

    print(agent.answer(repo_id, q))

    print()
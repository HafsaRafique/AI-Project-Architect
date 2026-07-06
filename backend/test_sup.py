from app.services.agents.supervisor import SupervisorAgent

repo_id = "test"

agent = SupervisorAgent()

print(
    agent.chat(
        repo_id,
        "Generate a README for this repository."
    )
)
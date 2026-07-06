from app.services.agents.supervisor import SupervisorAgent

agent = SupervisorAgent()

questions = [

    "Explain the architecture.",

    "How does authentication work?",

    "Generate documentation.",

    "Review this repository.",

    "Explain server.py."
]

for q in questions:

    print(agent.route(q))
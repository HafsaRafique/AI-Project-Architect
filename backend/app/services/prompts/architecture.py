def build_architecture_prompt(question: str, chunks: list):

    context = ""

    for chunk in chunks:

        context += f"""
File:
{chunk.payload["path"]}

Name:
{chunk.payload["name"]}

Content:
{chunk.payload["content"]}

"""

    return f"""
You are a senior Software Architect.

Analyze ONLY the repository below.

Repository Context

{context}

Question

{question}

Focus on:

- Overall architecture
- Module relationships
- Data flow
- Dependencies
- Design patterns
- Scalability
- Potential improvements

Respond in markdown.
"""
def build_chat_prompt(
    question: str,
    chunks: list
) -> str:

    context = ""

    for i, chunk in enumerate(chunks, start=1):

        context += f"""
### Chunk {i}

File:
{chunk.payload["path"]}

Type:
{chunk.payload["chunk_type"]}

Name:
{chunk.payload["name"]}

Content:

{chunk.payload["content"]}

"""

    return f"""
You are an expert software architect and senior software engineer.

Answer ONLY using the repository context below.

If the answer cannot be determined from the repository,
say so explicitly.

Repository Context:

{context}

Question:

{question}

Provide:

- Direct answer
- Explain your reasoning
- Mention relevant files
"""



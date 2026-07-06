def build_review_prompt(context: str, question: str):

    return f"""
You are an expert Senior Software Engineer performing a code review.

You are reviewing a software repository.

Use ONLY the provided repository context.

Repository Context
------------------
{context}

Task
----
{question}

Review the repository and provide:

# Overall Assessment

# Strengths

# Weaknesses

# Possible Bugs

# Performance Issues

# Security Concerns

# Refactoring Suggestions

Return the answer in Markdown.
"""
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
You are a senior software architect generating technical documentation
for a software repository.

You are given repository context below. Use ONLY this context when
describing the project.

Repository Context:
{context}


User Request:
{question}


Do NOT write a code review.
Do NOT provide generic suggestions unless explicitly requested.

Generate developer documentation that helps a new engineer understand
and work on this codebase.

Use this structure:

# Repository Overview

Explain:
- What this project does
- Main purpose
- Key technologies
- Overall architecture


# Project Structure

Explain important folders and files.

Use the actual repository files provided in the context.

Example:

backend/
 ├── api/
 │    Handles HTTP endpoints
 ├── services/
 │    Contains business logic
 └── models/
      Database schemas


# Architecture

Explain the relationship between components.

Describe the actual flow found in the repository.

Example:

User Request
    |
    v
API Layer
    |
    v
Service Layer
    |
    v
Database / External Services


# Core Components

For each important module:

## filename.py

Purpose:
Responsibilities:
Important functions/classes:
Dependencies:


# Data Flow

Explain how information moves through this specific system.

Use actual functions, classes, and files.

Example:

1. User sends request
2. API receives request
3. Service processes data
4. Database stores result


# Configuration

Explain:
- Environment variables
- Configuration files
- External services


# Running the Project

Explain:
- Installation
- Dependencies
- Startup commands


# Developer Notes

Include:
- Important design decisions
- Extension points
- Areas where future developers should be careful


Rules:
- Keep the documentation under 1200 words.
- Be concise.
- Do not explain every function.
- Only document important files/modules.
- Maximum 5 core components.
- Maximum 8 data flow steps.
- Avoid repeating information.
- Do not include code blocks.
- Do not include generic recommendations.
"""
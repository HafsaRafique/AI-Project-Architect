def build_documentation_prompt(context: str, question: str):

    return f"""
You are an expert software documentation engineer.

Use ONLY the provided repository context.

Repository Context
------------------
{context}

Task
----
{question}

Produce clear Markdown documentation.

When appropriate include:

# Project Overview

# Architecture

# Folder Structure

# Key Components

# Main Classes

# Main Functions

# API Endpoints

# Data Flow

# Setup Instructions

# Future Improvements

Return only Markdown.
"""
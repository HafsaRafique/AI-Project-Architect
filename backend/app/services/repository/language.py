from pathlib import Path

LANGUAGES = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".jsx": "jsx",
    ".java": "java",
    ".cpp": "cpp",
    ".c": "c",
    ".go": "go",
    ".rs": "rust",
    ".json": "json",
    ".md": "markdown",
}


def detect_language(filepath: str):

    ext = Path(filepath).suffix.lower()

    return LANGUAGES.get(ext, "unknown")
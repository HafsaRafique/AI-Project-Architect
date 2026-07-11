import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

# Ensure LLM calls never hit the network during tests: any test that cares
# about a specific provider behavior mocks llm_client directly instead.
os.environ.setdefault("LLM_PROVIDER", "ollama")
os.environ.setdefault("OLLAMA_HOST", "http://localhost:1")  # unroutable on purpose

import server  # noqa: E402


@pytest.fixture()
def client():
    server.app.config.update(TESTING=True)
    with server.app.test_client() as c:
        yield c
    # Reset in-memory game state between tests so they don't leak into
    # each other.
    server.games.clear()

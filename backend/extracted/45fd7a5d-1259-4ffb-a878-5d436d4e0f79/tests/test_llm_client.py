"""Unit tests for the LLM integration layer.

These never touch the network: `requests.post`/`requests.get` are
monkeypatched with fakes that simulate success, malformed JSON, schema
violations, timeouts, and permanent config errors, so we can exercise the
retry/validation/fallback logic deterministically.
"""
import json

import pytest
import requests
from pydantic import ValidationError

import llm_client as lc

# ---------------------------------------------------------------------
# Pure helpers: fallback narration/effect, JSON extraction
# ---------------------------------------------------------------------

def test_fallback_narration_checkmate():
    info = {"mover": "white", "piece": "q", "checkmate": True}
    text = lc._fallback_narration(info)
    assert "CHECKMATE" in text
    assert "White" in text


def test_fallback_narration_capture():
    info = {"mover": "black", "piece": "n", "captured": "p"}
    text = lc._fallback_narration(info)
    assert "Pawn" in text


def test_fallback_effect_is_always_valid():
    for category_info in [
        {"checkmate": True},
        {"captured": "p"},
        {"check": True},
        {"castle": True},
        {},
    ]:
        assert lc._fallback_effect(category_info) in lc.VALID_EFFECTS


@pytest.mark.parametrize(
    "raw,expected",
    [
        ('{"narration": "a", "effect": "fire"}', {"narration": "a", "effect": "fire"}),
        ('```json\n{"narration": "a", "effect": "fire"}\n```', {"narration": "a", "effect": "fire"}),
        ('Sure! {"narration": "a", "effect": "fire"} hope that helps', {"narration": "a", "effect": "fire"}),
    ],
)
def test_extract_json_handles_common_model_quirks(raw, expected):
    assert lc._extract_json(raw) == expected


def test_extract_json_raises_on_garbage():
    with pytest.raises(json.JSONDecodeError):
        lc._extract_json("not json at all")


# ---------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------

def test_narration_response_rejects_unknown_effect():
    with pytest.raises(ValidationError):
        lc.NarrationResponse.model_validate({"narration": "hi", "effect": "not-an-effect"})


def test_narration_response_rejects_empty_narration():
    with pytest.raises(ValidationError):
        lc.NarrationResponse.model_validate({"narration": "   ", "effect": "fire"})


def test_narration_response_truncates_very_long_narration():
    long_text = " ".join(["word"] * 100)
    validated = lc.NarrationResponse.model_validate({"narration": long_text, "effect": "fire"})
    assert len(validated.narration.split()) <= 41  # 40 words + ellipsis token


# ---------------------------------------------------------------------
# Personas
# ---------------------------------------------------------------------

def test_build_messages_uses_persona_system_prompt():
    messages = lc.build_messages({"san": "e4"}, persona="whimsical")
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == lc.NARRATOR_PERSONAS["whimsical"]
    assert messages[1]["role"] == "user"
    assert "e4" in messages[1]["content"]


def test_build_messages_falls_back_to_default_for_unknown_persona():
    messages = lc.build_messages({"san": "e4"}, persona="nonexistent")
    assert messages[0]["content"] == lc.NARRATOR_PERSONAS[lc.DEFAULT_PERSONA]


# ---------------------------------------------------------------------
# get_narration: end-to-end with a fake transport
# ---------------------------------------------------------------------

class _FakeResponse:
    def __init__(self, json_data=None, status=200, raise_exc=None):
        self._json = json_data or {}
        self.status_code = status
        self._raise_exc = raise_exc

    def raise_for_status(self):
        if self._raise_exc:
            raise self._raise_exc

    def json(self):
        return self._json


def test_get_narration_success_ollama(monkeypatch):
    monkeypatch.setattr(lc, "LLM_PROVIDER", "ollama")

    def fake_post(url, json, timeout):
        return _FakeResponse({"message": {"content": '{"narration": "The knight leaps!", "effect": "wind"}'}})

    monkeypatch.setattr(lc.requests, "post", fake_post)

    result = lc.get_narration({"san": "Nf3"})
    assert result["source"] == "ollama"
    assert result["effect"] == "wind"
    assert "knight" in result["narration"].lower()
    assert "error" not in result
    assert isinstance(result["latency_ms"], int)


def test_get_narration_falls_back_on_repeated_transport_failure(monkeypatch):
    monkeypatch.setattr(lc, "LLM_PROVIDER", "ollama")
    monkeypatch.setattr(lc, "MAX_ATTEMPTS", 2)
    monkeypatch.setattr(lc, "RETRY_BACKOFF_SECONDS", 0)  # keep the test fast

    calls = {"n": 0}

    def fake_post(url, json, timeout):
        calls["n"] += 1
        raise requests.ConnectionError("boom")

    monkeypatch.setattr(lc.requests, "post", fake_post)

    result = lc.get_narration({"san": "e4", "mover": "white", "piece": "p"})
    assert result["source"] == "fallback"
    assert "error" in result
    assert calls["n"] == 2  # retried up to MAX_ATTEMPTS


def test_get_narration_retries_then_succeeds(monkeypatch):
    monkeypatch.setattr(lc, "LLM_PROVIDER", "ollama")
    monkeypatch.setattr(lc, "MAX_ATTEMPTS", 2)
    monkeypatch.setattr(lc, "RETRY_BACKOFF_SECONDS", 0)

    calls = {"n": 0}

    def fake_post(url, json, timeout):
        calls["n"] += 1
        if calls["n"] == 1:
            raise requests.Timeout("slow")
        return _FakeResponse({"message": {"content": '{"narration": "Recovers!", "effect": "heal"}'}})

    monkeypatch.setattr(lc.requests, "post", fake_post)

    result = lc.get_narration({"san": "e4"})
    assert result["source"] == "ollama"
    assert result["effect"] == "heal"
    assert calls["n"] == 2


def test_get_narration_falls_back_on_invalid_schema(monkeypatch):
    monkeypatch.setattr(lc, "LLM_PROVIDER", "ollama")
    monkeypatch.setattr(lc, "MAX_ATTEMPTS", 1)

    def fake_post(url, json, timeout):
        return _FakeResponse({"message": {"content": '{"narration": "ok", "effect": "not-a-real-effect"}'}})

    monkeypatch.setattr(lc.requests, "post", fake_post)

    result = lc.get_narration({"san": "e4", "checkmate": True})
    assert result["source"] == "fallback"
    assert result["effect"] in lc.VALID_EFFECTS


def test_get_narration_huggingface_missing_token_does_not_retry(monkeypatch):
    monkeypatch.setattr(lc, "LLM_PROVIDER", "huggingface")
    monkeypatch.setattr(lc, "HF_TOKEN", "")

    calls = {"n": 0}

    def fake_post(*a, **k):
        calls["n"] += 1
        raise AssertionError("should not be called when token is missing")

    monkeypatch.setattr(lc.requests, "post", fake_post)

    result = lc.get_narration({"san": "e4"})
    assert result["source"] == "fallback"
    assert "HF_TOKEN" in result["error"]
    assert calls["n"] == 0


def test_check_provider_health_ollama_unreachable(monkeypatch):
    monkeypatch.setattr(lc, "LLM_PROVIDER", "ollama")

    def fake_get(url, timeout):
        raise requests.ConnectionError("no route")

    monkeypatch.setattr(lc.requests, "get", fake_get)
    health = lc.check_provider_health()
    assert health["ok"] is False
    assert health["provider"] == "ollama"


def test_check_provider_health_ollama_reachable_and_model_pulled(monkeypatch):
    monkeypatch.setattr(lc, "LLM_PROVIDER", "ollama")
    monkeypatch.setattr(lc, "OLLAMA_MODEL", "llama3.2")

    def fake_get(url, timeout):
        return _FakeResponse({"models": [{"name": "llama3.2:latest"}]})

    monkeypatch.setattr(lc.requests, "get", fake_get)
    health = lc.check_provider_health()
    assert health["ok"] is True
    assert health["model_pulled"] is True


def test_check_provider_health_huggingface_no_token(monkeypatch):
    monkeypatch.setattr(lc, "LLM_PROVIDER", "huggingface")
    monkeypatch.setattr(lc, "HF_TOKEN", "")
    health = lc.check_provider_health()
    assert health["ok"] is False

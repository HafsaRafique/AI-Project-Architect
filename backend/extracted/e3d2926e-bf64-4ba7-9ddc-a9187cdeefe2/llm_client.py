"""
Turns a chess move into RPG narration + a visual spell effect, using an
LLM as the storyteller.

This module is the "AI engineering" core of the project. It is deliberately
structured the way you'd want a real LLM-integration layer to look:

  - a clean boundary between *providers* (Ollama, Hugging Face) and the
    rest of the app, so adding a third backend means adding one function;
  - a strict, documented output schema, validated with Pydantic instead of
    trusted blindly (`NarrationResponse`);
  - bounded retries with backoff for transient failures, so a single
    dropped connection doesn't fall all the way back to canned text;
  - graceful, deterministic degradation (`_fallback_narration`) when the
    model is unreachable, rate-limited, or returns garbage, so the game is
    never blocked on the LLM;
  - a small "personality" system (`NARRATOR_PERSONAS`) that swaps the
    system prompt to change the narrator's voice, without touching any
    other code — a minimal but real example of prompt/config separation;
  - latency + provider metadata returned alongside the content, because in
    production you always want to know *how* an answer was produced, not
    just what it was.

Two providers are supported, switchable with one env var (LLM_PROVIDER):

  - "ollama"      : a fully self-hosted, open-source model running on your
                    own machine or server via Ollama (https://ollama.com).
                    No API key, no cloud, but your machine must stay on
                    and be reachable.
  - "huggingface" : Hugging Face's Inference Providers API. Still an
                    open-source model under the hood (Llama, Qwen,
                    Mistral, etc.), but hosted by HF's cloud instead of by
                    you — needs an HF_TOKEN, but your Flask app can then
                    be deployed anywhere with zero tunnels, since there's
                    no "localhost" for it to reach.

If the model is unreachable, missing a token, rate-limited, times out on
every retry, or returns something that fails schema validation, we fall
back to canned narration so the game never breaks.
"""
from __future__ import annotations

import json
import logging
import os
import random
import time
from dataclasses import dataclass
from typing import Any

import requests
from pydantic import BaseModel, ValidationError, field_validator

logger = logging.getLogger("rpg_chess.llm")

LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "ollama").strip().lower()

# ---- Ollama (local / self-hosted) ----
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_CHAT_URL = f"{OLLAMA_HOST.rstrip('/')}/api/chat"
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")

# ---- Hugging Face Inference Providers (cloud, OpenAI-compatible) ----
HF_TOKEN = os.environ.get("HF_TOKEN", "")
HF_MODEL = os.environ.get("HF_MODEL", "meta-llama/Llama-3.2-3B-Instruct")
HF_URL = "https://router.huggingface.co/v1/chat/completions"

# ---- Retry policy for transient failures ----
MAX_ATTEMPTS = int(os.environ.get("LLM_MAX_ATTEMPTS", "2"))
RETRY_BACKOFF_SECONDS = 0.6

VALID_EFFECTS = {
    "fire", "ice", "lightning", "heal", "slash",
    "explosion", "holy", "dark", "sparkle", "wind",
}

FALLBACK_EFFECTS = {
    "checkmate": ["explosion", "dark", "holy"],
    "capture": ["slash", "fire", "explosion"],
    "check": ["lightning", "holy"],
    "castle": ["heal", "holy"],
    "normal": ["sparkle", "wind"],
}

PIECE_NAMES = {
    "p": "Pawn", "n": "Knight", "b": "Bishop",
    "r": "Rook", "q": "Queen", "k": "King",
}

# ---- Narrator personas: swap the system prompt to change the voice ----
NARRATOR_PERSONAS: dict[str, str] = {
    "grimdark": (
        "You are the narrator of a grim fantasy duel between two rival "
        "kingdoms, fought out as a game of chess. Every chess move is one "
        "action in a deadly battle. Your tone is dark, weighty, and "
        "dramatic, like a war chronicle."
    ),
    "whimsical": (
        "You are a cheerful, slightly chaotic bard narrating a chess match "
        "as if it were a whimsical fantasy skirmish between two quirky "
        "kingdoms. Your tone is playful and funny, full of light-hearted "
        "flourish."
    ),
    "shakespearean": (
        "You are a Shakespearean herald narrating a chess match as a duel "
        "between noble houses. Write in a theatrical, archaic register "
        "(thee, thou, doth) while staying short and punchy."
    ),
}
DEFAULT_PERSONA = "grimdark"


class NarrationResponse(BaseModel):
    """Strict schema for what we accept back from the model.

    Validating this explicitly (rather than trusting `json.loads` output)
    is the difference between "the model usually behaves" and "the app
    cannot crash no matter what the model says."
    """

    narration: str
    effect: str

    @field_validator("narration")
    @classmethod
    def _non_empty_and_bounded(cls, v: str) -> str:
        v = v.strip().strip('"')
        if not v:
            raise ValueError("narration must not be empty")
        # Guard against runaway generations; keep it a one-liner.
        words = v.split()
        if len(words) > 40:
            v = " ".join(words[:40]) + "…"
        return v

    @field_validator("effect")
    @classmethod
    def _known_effect(cls, v: str) -> str:
        v = v.strip().lower()
        if v not in VALID_EFFECTS:
            raise ValueError(f"unknown effect {v!r}")
        return v


@dataclass
class NarrationResult:
    narration: str
    effect: str
    source: str  # "ollama" | "huggingface" | "fallback"
    latency_ms: int
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d = {
            "narration": self.narration,
            "effect": self.effect,
            "source": self.source,
            "latency_ms": self.latency_ms,
        }
        if self.error:
            d["error"] = self.error
        return d


def _category(move_info: dict) -> str:
    if move_info.get("checkmate"):
        return "checkmate"
    if move_info.get("captured"):
        return "capture"
    if move_info.get("check"):
        return "check"
    if move_info.get("castle"):
        return "castle"
    return "normal"


def _fallback_effect(move_info: dict) -> str:
    return random.choice(FALLBACK_EFFECTS[_category(move_info)])


def _fallback_narration(move_info: dict) -> str:
    piece = PIECE_NAMES.get((move_info.get("piece") or "").lower(), "Unit")
    mover = (move_info.get("mover") or "a warrior").capitalize()
    if move_info.get("checkmate"):
        return f"{mover}'s {piece} lands the final blow — CHECKMATE!"
    if move_info.get("captured"):
        cap = PIECE_NAMES.get((move_info.get("captured") or "").lower(), "foe")
        return f"{mover}'s {piece} cuts down the enemy {cap}!"
    if move_info.get("check"):
        return f"{mover}'s {piece} strikes fear into the enemy King — CHECK!"
    if move_info.get("castle"):
        return f"{mover}'s King retreats behind the castle walls."
    if move_info.get("stalemate"):
        return "The battlefield falls silent. A stalemate."
    return f"{mover}'s {piece} advances across the battlefield."


def build_messages(move_info: dict, persona: str = DEFAULT_PERSONA) -> list[dict[str, str]]:
    """Builds a chat-style (system, user) message pair for the given move.

    Using separate system/user turns (instead of one blob of text) is what
    lets `persona` swap the narrator's voice without touching the move
    data or the output-format instructions at all.
    """
    system_prompt = NARRATOR_PERSONAS.get(persona, NARRATOR_PERSONAS[DEFAULT_PERSONA])
    user_prompt = f"""Move data (JSON): {json.dumps(move_info)}

Write ONE short, dramatic sentence (max 20 words) narrating this move as a
battle action, and pick ONE visual spell effect that matches its mood.

Respond with ONLY a raw JSON object, nothing else, no markdown fences:
{{"narration": "<sentence>", "effect": "<one of: fire, ice, lightning, heal, slash, explosion, holy, dark, sparkle, wind>"}}
"""
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def _extract_json(text: str) -> dict:
    """Strips markdown fences some models add despite instructions, and
    grabs the first {...} block if there's stray text around it."""
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        text = text[start:end + 1]
    return json.loads(text)


def _call_ollama(messages: list[dict[str, str]], timeout: float) -> str:
    resp = requests.post(
        OLLAMA_CHAT_URL,
        json={
            "model": OLLAMA_MODEL,
            "messages": messages,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.9},
        },
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json().get("message", {}).get("content", "")


def _call_huggingface(messages: list[dict[str, str]], timeout: float) -> str:
    if not HF_TOKEN:
        raise RuntimeError("HF_TOKEN is not set")
    resp = requests.post(
        HF_URL,
        headers={
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/json",
        },
        json={
            "model": HF_MODEL,
            "messages": messages,
            "max_tokens": 150,
            "temperature": 0.9,
        },
        timeout=timeout,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def _call_provider(provider: str, messages: list[dict[str, str]], timeout: float) -> str:
    if provider == "huggingface":
        return _call_huggingface(messages, timeout)
    return _call_ollama(messages, timeout)


def _generate_with_retries(
    move_info: dict, persona: str, timeout: float
) -> tuple[NarrationResponse, str]:
    """Calls the configured provider, validating and retrying on failure.

    Retries cover transient issues (timeouts, momentary 5xx, a model that
    burped out invalid JSON once). They deliberately do *not* retry on
    `HF_TOKEN` missing or similar permanent misconfiguration — that should
    fail fast and fall back immediately instead of wasting the retry budget.
    """
    messages = build_messages(move_info, persona)
    last_exc: Exception | None = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            raw = _call_provider(LLM_PROVIDER, messages, timeout)
            parsed = _extract_json(raw)
            validated = NarrationResponse.model_validate(parsed)
            return validated, LLM_PROVIDER
        except RuntimeError:
            # Permanent config error (e.g. missing token) — don't retry.
            raise
        except (requests.RequestException, json.JSONDecodeError, ValidationError) as exc:
            last_exc = exc
            logger.warning(
                "LLM call attempt %d/%d failed (%s): %s",
                attempt, MAX_ATTEMPTS, type(exc).__name__, exc,
            )
            if attempt < MAX_ATTEMPTS:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)

    assert last_exc is not None
    raise last_exc


def get_narration(
    move_info: dict, persona: str = DEFAULT_PERSONA, timeout: float = 15
) -> dict:
    """Returns a dict: {narration, effect, source, latency_ms, [error]}.

    Never raises — any failure in the LLM path degrades to deterministic
    canned narration so the chess game itself is never blocked.
    """
    start = time.monotonic()
    try:
        validated, source = _generate_with_retries(move_info, persona, timeout)
        latency_ms = int((time.monotonic() - start) * 1000)
        result = NarrationResult(
            narration=validated.narration,
            effect=validated.effect,
            source=source,
            latency_ms=latency_ms,
        )
    except Exception as exc:
        latency_ms = int((time.monotonic() - start) * 1000)
        logger.info("Falling back to canned narration: %s", exc)
        result = NarrationResult(
            narration=_fallback_narration(move_info),
            effect=_fallback_effect(move_info),
            source="fallback",
            latency_ms=latency_ms,
            error=str(exc),
        )
    return result.to_dict()


def check_provider_health(timeout: float = 5) -> dict:
    """Lightweight connectivity check used by /api/health.

    Does not consume the narration retry budget or invent game state —
    just confirms the configured provider is reachable and (for Ollama)
    that the configured model is actually pulled.
    """
    if LLM_PROVIDER == "huggingface":
        if not HF_TOKEN:
            return {"provider": "huggingface", "ok": False, "detail": "HF_TOKEN not set"}
        return {"provider": "huggingface", "ok": True, "model": HF_MODEL}

    try:
        resp = requests.get(f"{OLLAMA_HOST.rstrip('/')}/api/tags", timeout=timeout)
        resp.raise_for_status()
        names = {m.get("name", "").split(":")[0] for m in resp.json().get("models", [])}
        model_base = OLLAMA_MODEL.split(":")[0]
        pulled = model_base in names
        return {
            "provider": "ollama",
            "ok": True,
            "model": OLLAMA_MODEL,
            "model_pulled": pulled,
            "host": OLLAMA_HOST,
        }
    except requests.RequestException as exc:
        return {"provider": "ollama", "ok": False, "detail": str(exc), "host": OLLAMA_HOST}

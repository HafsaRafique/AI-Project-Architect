"""
Turns a chess move into RPG narration + a visual spell effect, using an
LLM as the storyteller. Two backends are supported, switchable with one
env var (LLM_PROVIDER):

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

If the model is unreachable, missing a token, rate-limited, or returns
something unparsable, we fall back to canned narration so the game never
breaks.
"""
import json
import os
import random
import requests

LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "ollama").strip().lower()

# ---- Ollama (local / self-hosted) ----
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_URL = f"{OLLAMA_HOST.rstrip('/')}/api/generate"
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")

# ---- Hugging Face Inference Providers (cloud, OpenAI-compatible) ----
HF_TOKEN = os.environ.get("HF_TOKEN", "")
HF_MODEL = os.environ.get("HF_MODEL", "meta-llama/Llama-3.2-3B-Instruct")
HF_URL = "https://router.huggingface.co/v1/chat/completions"

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


def _category(move_info):
    if move_info.get("checkmate"):
        return "checkmate"
    if move_info.get("captured"):
        return "capture"
    if move_info.get("check"):
        return "check"
    if move_info.get("castle"):
        return "castle"
    return "normal"


def _fallback_effect(move_info):
    return random.choice(FALLBACK_EFFECTS[_category(move_info)])


def _fallback_narration(move_info):
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


def build_prompt(move_info):
    return f"""You are the narrator of a fantasy RPG duel between two rival kingdoms,
fought out as a game of chess. Every chess move is one action in the battle.

Move data (JSON): {json.dumps(move_info)}

Write ONE short, dramatic sentence (max 20 words) narrating this move as an
RPG battle action, and pick ONE visual spell effect that matches its mood.

Respond with ONLY a raw JSON object, nothing else, no markdown fences:
{{"narration": "<dramatic sentence>", "effect": "<one of: fire, ice, lightning, heal, slash, explosion, holy, dark, sparkle, wind>"}}
"""


def _extract_json(text):
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


def _call_ollama(prompt, timeout):
    resp = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.9},
        },
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json().get("response", "")


def _call_huggingface(prompt, timeout):
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
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 150,
            "temperature": 0.9,
        },
        timeout=timeout,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def get_narration(move_info, timeout=15):
    prompt = build_prompt(move_info)
    try:
        if LLM_PROVIDER == "huggingface":
            raw = _call_huggingface(prompt, timeout)
        else:
            raw = _call_ollama(prompt, timeout)

        parsed = _extract_json(raw)
        narration = str(parsed.get("narration", "")).strip()
        effect = str(parsed.get("effect", "")).strip().lower()

        if not narration:
            narration = _fallback_narration(move_info)
        if effect not in VALID_EFFECTS:
            effect = _fallback_effect(move_info)

        return {"narration": narration, "effect": effect, "source": LLM_PROVIDER}

    except Exception as exc:
        return {
            "narration": _fallback_narration(move_info),
            "effect": _fallback_effect(move_info),
            "source": "fallback",
            "error": str(exc),
        }

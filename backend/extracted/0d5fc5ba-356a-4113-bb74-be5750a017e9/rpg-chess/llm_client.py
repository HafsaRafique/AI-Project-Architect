"""
Talks to a locally-hosted, open-source LLM through Ollama
(https://ollama.com — runs models like Llama 3, Mistral, Qwen, etc. entirely
on your own machine, no API key, no cloud).

The model is the center of the whole app: every move is handed to it, and it
decides both WHAT is said (narration) and WHAT is shown (the effect key that
the frontend animates). If the model is unreachable or returns something
unparsable, we fall back to canned narration so the game never breaks.
"""
import json
import random
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

# Change this to whatever open-source model you've pulled with
# `ollama pull <name>`. Good small/fast options: "llama3.2", "qwen2.5:7b",
# "mistral". Larger ones ("llama3.1:70b") give richer narration if you have
# the hardware.
MODEL_NAME = "llama3.2"

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


def get_narration(move_info, timeout=8):
    prompt = build_prompt(move_info)
    try:
        resp = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {"temperature": 0.9},
            },
            timeout=timeout,
        )
        resp.raise_for_status()
        raw = resp.json().get("response", "")
        parsed = json.loads(raw)

        narration = str(parsed.get("narration", "")).strip()
        effect = str(parsed.get("effect", "")).strip().lower()

        if not narration:
            narration = _fallback_narration(move_info)
        if effect not in VALID_EFFECTS:
            effect = _fallback_effect(move_info)

        return {"narration": narration, "effect": effect, "source": "llm"}

    except Exception as exc:
        return {
            "narration": _fallback_narration(move_info),
            "effect": _fallback_effect(move_info),
            "source": "fallback",
            "error": str(exc),
        }

# Runebound Chess

Real 2-player chess (hot-seat, one board, alternating turns) where every move
is narrated by a **self-hosted, open-source LLM** as an RPG battle action,
with a matching spell-effect animation on the board. The model is the center
of the experience: it decides both what's said and what visual effect fires.

No cloud API, no API key — the LLM runs entirely on your own machine via
[Ollama](https://ollama.com).

## How it works

- **Backend** (`server.py`, Flask): implements the actual chess rules using
  `python-chess` — legal move validation, check/checkmate/stalemate,
  castling, en passant, promotion.
- **LLM layer** (`llm_client.py`): after each move, sends structured move
  data (piece, captured piece, check/checkmate/castle flags, etc.) to a
  local Ollama model and asks it to return JSON: a one-line dramatic
  narration + a spell-effect name (`fire`, `ice`, `lightning`, `heal`,
  `slash`, `explosion`, `holy`, `dark`, `sparkle`, `wind`). If the model is
  unreachable or replies with something unparsable, a canned fallback keeps
  the game playable.
- **Frontend** (`static/`): a hand-drawn dark-arcane chessboard. Clicking a
  piece highlights legal moves; making a move triggers a particle burst
  matching the model's chosen effect, and the narration appears in "The
  Chronicle" scroll panel.

## Setup

### 1. Install Ollama and pull a model

```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

# pull an open-source model (pick one that fits your hardware)
ollama pull llama3.2        # ~2GB, fast, good default
# or: ollama pull qwen2.5:7b
# or: ollama pull mistral

# Ollama usually runs as a background service on localhost:11434.
# If not, start it manually:
ollama serve
```

If you use a different model name, update `MODEL_NAME` in `llm_client.py`.

### 2. Install Python dependencies

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run the app

```bash
python server.py
```

Open **http://localhost:5000** in your browser. Two people share the same
screen/keyboard and take turns clicking moves (classic hot-seat chess).

## Extending it

- **Network multiplayer**: give each game a real `game_id`, add a second
  route/socket per player, and use a WebSocket (Flask-SocketIO) instead of
  polling `/api/state`, so both browsers update live.
- **Different personality per model**: swap `MODEL_NAME`, or run two models
  and let each side's moves be narrated in a different voice (e.g. a grim
  general for Black, a noble knight for White) by changing the prompt in
  `build_prompt()` based on `move_info["mover"]`.
- **Voice**: pipe the narration text through a local TTS engine (e.g.
  Piper, also open-source and self-hosted) to have the battle narrated
  aloud.
- **Board skins**: the effect classes are plain CSS in `style.css` — add
  new ones and teach the prompt about the new effect names.

## Project layout

```
rpg-chess/
├── server.py           # Flask backend + chess rules
├── llm_client.py        # Ollama integration, prompt, fallback logic
├── requirements.txt
├── static/
│   ├── index.html
│   ├── style.css        # dark-arcane theme + spell-effect animations
│   └── app.js           # board rendering, move handling, effects
└── README.md
```

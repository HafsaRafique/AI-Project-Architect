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

## Deployment

Two different goals, two different answers.

### A. Just want two people to play on the same network

You don't need to "deploy" anything — run it on one machine and have the
other player join over Wi-Fi:

```bash
python server.py
```

Find your machine's LAN IP (`ipconfig` on Windows, `ifconfig`/`ip a` on
Mac/Linux — something like `192.168.1.42`), then the second player opens
`http://192.168.1.42:5000` on their own device, on the same network. Since
this app is hot-seat (one shared board, alternating turns), realistically
both people play by looking at whichever screen is open — this mode is
mainly useful if you want to view the board on a phone while it runs on a
laptop, etc. For each player to see their own moves-only view from a
separate device, you'd want the "network multiplayer" extension mentioned
below.

### B. Deploy it to a real server (Docker, recommended)

The included `Dockerfile` and `docker-compose.yml` run the Flask app and a
self-hosted Ollama instance as two containers on the same Docker network:

```bash
docker compose up -d
docker compose exec ollama ollama pull llama3.2
```

Then visit `http://<server-ip>:5000`. To change the model, edit
`OLLAMA_MODEL` in `docker-compose.yml` and re-pull it with the command
above.

**Hardware note:** Ollama needs real compute. A small model like
`llama3.2` (3B) runs fine on 8GB RAM with just a CPU, but responses will be
a few seconds slower per move than with a GPU. If you're deploying to a
cloud VPS, pick one with at least 8GB RAM (e.g. a $40-80/mo box on
Hetzner/DigitalOcean/Linode), or use a GPU instance if you want a bigger,
faster model.

**Exposing it publicly:** put a reverse proxy (Caddy or Nginx) in front of
port 5000 for HTTPS and a real domain. Caddy is the simplest — a two-line
`Caddyfile`:
```
yourdomain.com {
    reverse_proxy localhost:5000
}
```
Do **not** expose Ollama's port (11434) publicly — it has no auth. In the
compose file it's only reachable app-to-app over the internal Docker
network; the `11434:11434` port mapping is optional and only for your own
debugging.

### C. Deploy without Docker (plain VPS)

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2

pip install -r requirements.txt gunicorn
gunicorn --workers 1 --threads 4 --bind 0.0.0.0:5000 server:app
```

Run both as `systemd` services (or inside `tmux`/`screen`) so they survive
logout and restart on reboot.

**Important:** always run the Flask app with `--workers 1`. Game state
lives in an in-memory Python dict, so multiple worker processes would each
maintain their own separate, inconsistent copy of the board. If you need
to scale beyond one process (e.g. many simultaneous games under load),
move the `games` dict to Redis or a small database first.

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

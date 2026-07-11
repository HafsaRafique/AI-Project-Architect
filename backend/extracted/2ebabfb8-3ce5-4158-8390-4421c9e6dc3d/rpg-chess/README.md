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

## Choosing your LLM backend

The app supports two backends, switched with one environment variable
(`LLM_PROVIDER`). Copy `.env.example` to `.env` and fill in what you need.

### Option 1: Ollama (fully self-hosted, local)

Everything, including the model weights, runs on your own machine — no
API key, no cloud, no per-call cost. The tradeoff: your machine (or
whatever server it's on) has to be running and reachable whenever anyone
plays, which means tunneling (see the Deployment section below) if you
want to share it.

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2
```
```
# .env
LLM_PROVIDER=ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

### Option 2: Hugging Face Inference Providers (cloud, needs an API key)

The model itself is still open-source (Llama, Qwen, Mistral, etc.) — it's
just hosted on Hugging Face's infrastructure instead of yours. This is the
easier path if you want to deploy the app to a real server: since there's
no "localhost" the LLM depends on, your Flask app can run anywhere and
just make an outbound HTTPS call.

1. Create a token at https://huggingface.co/settings/tokens — a
   fine-grained token with **"Make calls to Inference Providers"**
   permission is enough. No dedicated GPU or endpoint needed.
2. Set:
```
# .env
LLM_PROVIDER=huggingface
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
HF_MODEL=meta-llama/Llama-3.2-3B-Instruct
```
Any chat-capable model on the Hugging Face Hub that has an available
Inference Provider works — swap `HF_MODEL` for anything from
https://huggingface.co/models?inference_provider=all&pipeline_tag=text-generation.

**Free-tier notes:** Hugging Face's free tier has rate limits and can have
a short "cold start" delay the first time a given model is called after
being idle — the app's fallback narration kicks in automatically if a
call times out or fails, so the game never stalls. For steady traffic,
either accept occasional fallback lines on the free tier, or use a paid
Inference Provider / dedicated Inference Endpoint for guaranteed capacity.

**Never commit `HF_TOKEN` to source control.** Put it in `.env` (already
gitignored if you use the included `.dockerignore`/`.gitignore` pattern)
or your hosting platform's environment variable settings.

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
`http://192.168.1.42:5000` on their own device, on the same network.

### B. Deploying with Ollama (self-hosted LLM)

Since Ollama has to run somewhere your app can reach it, you have two
sub-options:

**B1. Tunnel your local machine out** (keeps everything, including Ollama,
on your own computer):
```bash
ngrok http 5000          # or: cloudflared tunnel --url http://localhost:5000
```
Get a free static ngrok domain at https://dashboard.ngrok.com/domains so
the URL doesn't change every restart:
```bash
ngrok http --url=your-name-1234.ngrok-free.app 5000
```
Your machine has to stay on and awake the whole time.

**B2. Run both the app and Ollama on a real server**, using the included
Docker setup:
```bash
docker compose up -d
docker compose exec ollama ollama pull llama3.2
```
Needs a server with real RAM (8GB+ for a small model like `llama3.2`,
more for bigger ones, or a GPU instance for speed).

### C. Deploying with Hugging Face (cloud LLM) — no tunnel needed

This is the simplest path to a permanently-online deployment, because the
LLM call goes out over HTTPS to Hugging Face regardless of where your app
lives. Any host works:

```bash
# on any VPS, Render, Railway, Fly.io, etc.
pip install -r requirements.txt gunicorn
export LLM_PROVIDER=huggingface
export HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
export HF_MODEL=meta-llama/Llama-3.2-3B-Instruct
gunicorn --workers 1 --threads 4 --bind 0.0.0.0:5000 server:app
```

Or with Docker — the same `Dockerfile` works, just don't bother starting
the `ollama` service from `docker-compose.yml`:
```bash
docker build -t rpg-chess .
docker run -p 5000:5000 \
  -e LLM_PROVIDER=huggingface \
  -e HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx \
  -e HF_MODEL=meta-llama/Llama-3.2-3B-Instruct \
  rpg-chess
```

Put a domain + HTTPS in front with Caddy (simplest option):
```
yourdomain.com {
    reverse_proxy localhost:5000
}
```

**Important either way:** always run with `--workers 1`. Game state lives
in an in-memory Python dict, so multiple worker processes would each keep
their own separate, inconsistent copy of the board. Scale beyond one
process only after moving `games` to Redis or a small database.

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

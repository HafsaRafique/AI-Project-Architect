"""
RPG Chess — backend server.

Two humans play real chess (hot-seat, one board, alternating turns).
After every move, the move is described to an LLM (Ollama or Hugging
Face), which invents a short RPG-battle narration line and picks a visual
"spell effect" that the frontend renders as an animation on the board.

Run:
    pip install -r requirements.txt
    ollama pull llama3.2      # or any model you like, see llm_client.py
    ollama serve              # usually already running as a service
    python server.py
Then open http://localhost:5000
"""
from __future__ import annotations

import logging
import os
import threading
from dataclasses import dataclass, field

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import chess
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from llm_client import DEFAULT_PERSONA, NARRATOR_PERSONAS, check_provider_health, get_narration

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("rpg_chess.server")

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)


@dataclass
class Game:
    board: chess.Board = field(default_factory=chess.Board)
    history: list[dict] = field(default_factory=list)
    persona: str = DEFAULT_PERSONA
    lock: threading.Lock = field(default_factory=threading.Lock)


# In-memory game store. Fine for single-process/single-worker deployments
# (see README/Dockerfile); move to Redis before scaling past one worker.
games: dict[str, Game] = {}
games_lock = threading.Lock()


def get_game(game_id: str) -> Game:
    with games_lock:
        if game_id not in games:
            games[game_id] = Game()
        return games[game_id]


def serialize_state(game: Game, extra: dict | None = None) -> dict:
    board = game.board
    data = {
        "fen": board.fen(),
        "turn": "white" if board.turn == chess.WHITE else "black",
        "is_check": board.is_check(),
        "is_checkmate": board.is_checkmate(),
        "is_stalemate": board.is_stalemate(),
        "is_game_over": board.is_game_over(),
        "move_stack": [m.uci() for m in board.move_stack],
        "history": game.history,
        "persona": game.persona,
    }
    if extra:
        data.update(extra)
    return data


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/personas", methods=["GET"])
def personas():
    return jsonify({
        "personas": list(NARRATOR_PERSONAS.keys()),
        "default": DEFAULT_PERSONA,
    })


@app.route("/api/health", methods=["GET"])
def health():
    llm_status = check_provider_health()
    overall_ok = llm_status.get("ok", False)
    return jsonify({
        "ok": True,  # the web app itself is always "up" if this responds
        "llm": llm_status,
        "narration_degrades_gracefully": True if not overall_ok else None,
        "active_games": len(games),
    })


@app.route("/api/new_game", methods=["POST"])
def new_game():
    data = request.get_json(force=True, silent=True) or {}
    game_id = str(data.get("game_id") or "default")
    persona = data.get("persona", DEFAULT_PERSONA)
    if persona not in NARRATOR_PERSONAS:
        persona = DEFAULT_PERSONA
    with games_lock:
        games[game_id] = Game(persona=persona)
        game = games[game_id]
    logger.info("New game %s started with persona=%s", game_id, persona)
    return jsonify(serialize_state(game))


@app.route("/api/state", methods=["GET"])
def state():
    game_id = request.args.get("game_id", "default")
    game = get_game(game_id)
    return jsonify(serialize_state(game))


@app.route("/api/legal_moves", methods=["GET"])
def legal_moves():
    game_id = request.args.get("game_id", "default")
    square = request.args.get("square")
    game = get_game(game_id)
    moves = []
    if square:
        try:
            sq = chess.parse_square(square)
        except ValueError:
            return jsonify({"moves": []})
        with game.lock:
            for m in game.board.legal_moves:
                if m.from_square == sq:
                    moves.append(chess.square_name(m.to_square))
    return jsonify({"moves": moves})


@app.route("/api/move", methods=["POST"])
def make_move():
    data = request.get_json(force=True)
    game_id = str(data.get("game_id") or "default")
    uci = data.get("move", "")
    game = get_game(game_id)

    with game.lock:
        board = game.board

        try:
            move = chess.Move.from_uci(uci)
        except Exception:
            return jsonify({"error": "invalid move format"}), 400

        if move not in board.legal_moves:
            return jsonify({"error": "illegal move"}), 400

        piece = board.piece_at(move.from_square)
        captured = board.piece_at(move.to_square)
        is_castle = board.is_castling(move)
        is_ep = board.is_en_passant(move)
        san = board.san(move)
        mover_color = "white" if board.turn == chess.WHITE else "black"

        board.push(move)

        move_info = {
            "san": san,
            "mover": mover_color,
            "piece": piece.symbol() if piece else None,
            "captured": captured.symbol() if captured else None,
            "castle": is_castle,
            "en_passant": is_ep,
            "check": board.is_check(),
            "checkmate": board.is_checkmate(),
            "stalemate": board.is_stalemate(),
            "promotion": move.promotion is not None,
            "to_square": chess.square_name(move.to_square),
        }
        game.history.append(move_info)
        persona = game.persona

    narration = get_narration(move_info, persona=persona)
    logger.info(
        "move=%s game=%s source=%s latency_ms=%s",
        move_info["san"], game_id, narration.get("source"), narration.get("latency_ms"),
    )

    return jsonify(serialize_state(game, extra={
        "move_info": move_info,
        "narration": narration,
    }))


@app.errorhandler(404)
def not_found(_e):
    return jsonify({"error": "not found"}), 404


@app.errorhandler(500)
def server_error(e):
    logger.exception("Unhandled server error")
    return jsonify({"error": "internal server error"}), 500


if __name__ == "__main__":
    # Game state lives in an in-memory dict (`games`), which only works
    # correctly with a single process/worker. For local dev or LAN play
    # this is fine. For a real deployment, run this behind gunicorn with
    # `--workers 1` (see Dockerfile / README), or move `games` to Redis if
    # you need multiple workers.
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)

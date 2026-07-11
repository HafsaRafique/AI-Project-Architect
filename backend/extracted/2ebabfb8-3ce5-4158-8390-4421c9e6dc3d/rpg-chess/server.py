"""
RPG Chess — backend server.

Two humans play real chess (hot-seat, one board, alternating turns).
After every move, the move is described to a self-hosted LLM (via Ollama),
which invents a short RPG-battle narration line and picks a visual "spell
effect" that the frontend renders as an animation on the board.

Run:
    pip install -r requirements.txt
    ollama pull llama3.2      # or any model you like, see llm_client.py
    ollama serve              # usually already running as a service
    python server.py
Then open http://localhost:5000
"""
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import chess

from llm_client import get_narration

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)


class Game:
    def __init__(self):
        self.board = chess.Board()
        self.history = []


games = {}


def get_game(game_id):
    if game_id not in games:
        games[game_id] = Game()
    return games[game_id]


def serialize_state(game, extra=None):
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
    }
    if extra:
        data.update(extra)
    return data


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/new_game", methods=["POST"])
def new_game():
    data = request.get_json(force=True, silent=True) or {}
    game_id = data.get("game_id", "default")
    games[game_id] = Game()
    return jsonify(serialize_state(games[game_id]))


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
        for m in game.board.legal_moves:
            if m.from_square == sq:
                moves.append(chess.square_name(m.to_square))
    return jsonify({"moves": moves})


@app.route("/api/move", methods=["POST"])
def make_move():
    data = request.get_json(force=True)
    game_id = data.get("game_id", "default")
    uci = data.get("move", "")
    game = get_game(game_id)
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

    narration = get_narration(move_info)

    return jsonify(serialize_state(game, extra={
        "move_info": move_info,
        "narration": narration,
    }))


if __name__ == "__main__":
    # Game state lives in an in-memory dict (`games`), which only works
    # correctly with a single process/worker. For local dev or LAN play
    # this is fine. For a real deployment, run this behind gunicorn with
    # `--workers 1` (see Dockerfile / README), or move `games` to Redis if
    # you need multiple workers.
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)

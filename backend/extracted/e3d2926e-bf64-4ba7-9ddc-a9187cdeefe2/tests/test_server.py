"""Integration tests for the Flask API surface, using python-chess's own
rules as the source of truth (we're testing our wiring, not chess itself).

LLM calls are monkeypatched to a fast, deterministic stub so these tests
run in milliseconds with no network access and no dependency on Ollama or
Hugging Face being reachable.
"""
import server


def _stub_narration(move_info, persona=None, timeout=15):
    return {
        "narration": f"stub narration for {move_info.get('san')}",
        "effect": "sparkle",
        "source": "stub",
        "latency_ms": 0,
    }


def test_index_serves_frontend(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"<html" in resp.data.lower()


def test_new_game_resets_board(client):
    resp = client.post("/api/new_game", json={"game_id": "g1"})
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["turn"] == "white"
    assert data["is_game_over"] is False
    assert data["history"] == []


def test_new_game_rejects_unknown_persona_silently(client):
    resp = client.post("/api/new_game", json={"game_id": "g1", "persona": "not-a-real-persona"})
    data = resp.get_json()
    assert data["persona"] == server.DEFAULT_PERSONA


def test_new_game_accepts_known_persona(client):
    resp = client.post("/api/new_game", json={"game_id": "g1", "persona": "whimsical"})
    data = resp.get_json()
    assert data["persona"] == "whimsical"


def test_state_autocreates_game(client):
    resp = client.get("/api/state?game_id=fresh")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["fen"].startswith("rnbqkbnr")


def test_legal_moves_for_opening_pawn(client):
    client.post("/api/new_game", json={"game_id": "g1"})
    resp = client.get("/api/legal_moves?game_id=g1&square=e2")
    data = resp.get_json()
    assert sorted(data["moves"]) == ["e3", "e4"]


def test_legal_moves_empty_square_returns_empty_list(client):
    client.post("/api/new_game", json={"game_id": "g1"})
    resp = client.get("/api/legal_moves?game_id=g1&square=e4")
    assert resp.get_json()["moves"] == []


def test_make_move_valid(client, monkeypatch):
    monkeypatch.setattr(server, "get_narration", _stub_narration)
    client.post("/api/new_game", json={"game_id": "g1"})
    resp = client.post("/api/move", json={"game_id": "g1", "move": "e2e4"})
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["turn"] == "black"
    assert data["move_info"]["san"] == "e4"
    assert data["narration"]["effect"] == "sparkle"
    assert len(data["history"]) == 1


def test_make_move_illegal_returns_400(client, monkeypatch):
    monkeypatch.setattr(server, "get_narration", _stub_narration)
    client.post("/api/new_game", json={"game_id": "g1"})
    # e2e5 is not a legal pawn move
    resp = client.post("/api/move", json={"game_id": "g1", "move": "e2e5"})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_make_move_malformed_uci_returns_400(client, monkeypatch):
    monkeypatch.setattr(server, "get_narration", _stub_narration)
    client.post("/api/new_game", json={"game_id": "g1"})
    resp = client.post("/api/move", json={"game_id": "g1", "move": "not-a-move"})
    assert resp.status_code == 400


def test_foolsmate_reports_checkmate(client, monkeypatch):
    """Plays the fastest possible checkmate (Fool's Mate) and verifies the
    server correctly reports checkmate + game-over state."""
    monkeypatch.setattr(server, "get_narration", _stub_narration)
    client.post("/api/new_game", json={"game_id": "g1"})
    moves = ["f2f3", "e7e5", "g2g4", "d8h4"]
    last = None
    for uci in moves:
        last = client.post("/api/move", json={"game_id": "g1", "move": uci})
    data = last.get_json()
    assert data["is_checkmate"] is True
    assert data["is_game_over"] is True
    assert data["move_info"]["checkmate"] is True


def test_castling_flag_set(client, monkeypatch):
    monkeypatch.setattr(server, "get_narration", _stub_narration)
    client.post("/api/new_game", json={"game_id": "g1"})
    moves = ["g1f3", "g8f6", "g2g3", "g7g6", "f1g2", "f8g7", "e1g1"]  # kingside castle
    last = None
    for uci in moves:
        last = client.post("/api/move", json={"game_id": "g1", "move": uci})
    data = last.get_json()
    assert data["move_info"]["castle"] is True


def test_health_endpoint_reports_llm_status(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert "llm" in data
    assert "provider" in data["llm"]


def test_personas_endpoint_lists_options(client):
    resp = client.get("/api/personas")
    data = resp.get_json()
    assert "grimdark" in data["personas"]
    assert data["default"] == "grimdark"


def test_games_are_independent(client, monkeypatch):
    monkeypatch.setattr(server, "get_narration", _stub_narration)
    client.post("/api/new_game", json={"game_id": "a"})
    client.post("/api/new_game", json={"game_id": "b"})
    client.post("/api/move", json={"game_id": "a", "move": "e2e4"})

    state_a = client.get("/api/state?game_id=a").get_json()
    state_b = client.get("/api/state?game_id=b").get_json()

    assert state_a["turn"] == "black"
    assert state_b["turn"] == "white"  # untouched

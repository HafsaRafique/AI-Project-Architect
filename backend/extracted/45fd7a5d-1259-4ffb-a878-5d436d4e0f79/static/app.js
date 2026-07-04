const boardEl = document.getElementById('board');
const chronicleEl = document.getElementById('chronicle');
const turnEl = document.getElementById('turn-indicator');
const statusEl = document.getElementById('status');
const thinkingEl = document.getElementById('thinking');
const effectLayer = document.getElementById('effect-layer');
const personaSelect = document.getElementById('persona-select');
const connectionDot = document.getElementById('connection-dot');
const modelNoteEl = document.getElementById('model-note');
const overlayEl = document.getElementById('game-over-overlay');
const overlayTitleEl = document.getElementById('game-over-title');
const overlayDetailEl = document.getElementById('game-over-detail');

const GAME_ID = 'default';
let selectedSquare = null;
let legalTargets = [];
let currentFen = null;
let isBusy = false; // true while a move is in flight (awaiting narration)

const PIECE_UNICODE = {
  P: '♙', N: '♘', B: '♗', R: '♖', Q: '♕', K: '♔',
  p: '♟', n: '♞', b: '♝', r: '♜', q: '♛', k: '♚',
};

function fenToBoard(fen) {
  const rows = fen.split(' ')[0].split('/');
  const board = [];
  for (const row of rows) {
    const boardRow = [];
    for (const ch of row) {
      if (/\d/.test(ch)) {
        for (let i = 0; i < parseInt(ch, 10); i++) boardRow.push(null);
      } else {
        boardRow.push(ch);
      }
    }
    board.push(boardRow);
  }
  return board; // board[0] = rank 8 ... board[7] = rank 1
}

function squareName(fileIdx, rankIdx) {
  const file = String.fromCharCode('a'.charCodeAt(0) + fileIdx);
  const rank = 8 - rankIdx;
  return `${file}${rank}`;
}

function renderBoard(fen) {
  currentFen = fen;
  const board = fenToBoard(fen);
  boardEl.innerHTML = '';
  for (let r = 0; r < 8; r++) {
    for (let f = 0; f < 8; f++) {
      const sq = squareName(f, r);
      const isLight = (r + f) % 2 === 0;
      const cell = document.createElement('div');
      cell.className = `square ${isLight ? 'light' : 'dark'}`;
      cell.dataset.square = sq;

      const piece = board[r][f];
      if (piece) {
        const span = document.createElement('span');
        span.className = `piece ${piece === piece.toUpperCase() ? 'white-piece' : 'black-piece'}`;
        span.textContent = PIECE_UNICODE[piece];
        cell.appendChild(span);
      }
      if (selectedSquare === sq) cell.classList.add('selected');
      if (legalTargets.includes(sq)) cell.classList.add('legal-target');

      cell.addEventListener('click', () => onSquareClick(sq));
      boardEl.appendChild(cell);
    }
  }
}

async function api(path, opts) {
  const res = await fetch(`/api/${path}`, opts);
  return res.json();
}

async function loadPersonas() {
  try {
    const data = await api('personas');
    personaSelect.innerHTML = '';
    for (const persona of data.personas) {
      const opt = document.createElement('option');
      opt.value = persona;
      opt.textContent = persona.charAt(0).toUpperCase() + persona.slice(1);
      if (persona === data.default) opt.selected = true;
      personaSelect.appendChild(opt);
    }
  } catch (e) {
    personaSelect.innerHTML = '<option value="grimdark">Grimdark</option>';
  }
}

async function checkHealth() {
  try {
    const data = await api('health');
    const ok = data.llm && data.llm.ok;
    connectionDot.classList.toggle('online', !!ok);
    connectionDot.classList.toggle('offline', !ok);
    if (ok && data.llm.provider === 'ollama') {
      connectionDot.title = `Connected to Ollama (${data.llm.model})`;
      modelNoteEl.innerHTML = `Narrated live by <strong>${data.llm.model}</strong> via ` +
        `<a href="https://ollama.com" target="_blank" rel="noopener">Ollama</a>, running on your own machine. ` +
        `No cloud, no API key.`;
    } else if (ok) {
      connectionDot.title = `Connected via ${data.llm.provider} (${data.llm.model || ''})`;
      modelNoteEl.innerHTML = `Narrated live by <strong>${data.llm.model || data.llm.provider}</strong> ` +
        `via Hugging Face Inference Providers.`;
    } else {
      connectionDot.title = 'Narrator unreachable — using scripted fallback lines';
      modelNoteEl.innerHTML = `The LLM narrator isn't reachable right now, so moves are being narrated with ` +
        `scripted fallback lines instead. The game itself is unaffected — see the README to connect a model.`;
    }
  } catch (e) {
    connectionDot.classList.remove('online');
    connectionDot.classList.add('offline');
    modelNoteEl.textContent = 'Could not reach the server to check narrator status.';
  }
}

async function loadState() {
  const data = await api(`state?game_id=${GAME_ID}`);
  renderBoard(data.fen);
  updateStatus(data);
}

function updateStatus(data) {
  turnEl.textContent = data.turn === 'white' ? "White's turn" : "Black's turn";
  if (data.is_checkmate) statusEl.textContent = 'Checkmate!';
  else if (data.is_stalemate) statusEl.textContent = 'Stalemate.';
  else if (data.is_check) statusEl.textContent = 'Check!';
  else statusEl.textContent = '';

  if (data.is_checkmate) {
    const winner = data.turn === 'white' ? 'Black' : 'White';
    showGameOver('Checkmate', `${winner} triumphs on the battlefield.`);
  } else if (data.is_stalemate) {
    showGameOver('Stalemate', 'Neither army can strike the final blow.');
  } else {
    hideGameOver();
  }
}

function showGameOver(title, detail) {
  overlayTitleEl.textContent = title;
  overlayDetailEl.textContent = detail;
  overlayEl.classList.remove('hidden');
}

function hideGameOver() {
  overlayEl.classList.add('hidden');
}

function isPromotion(from, to) {
  const board = fenToBoard(currentFen);
  const fromFile = from.charCodeAt(0) - 'a'.charCodeAt(0);
  const fromRankIdx = 8 - parseInt(from[1], 10);
  const piece = board[fromRankIdx][fromFile];
  if (!piece) return false;
  const isPawn = piece.toLowerCase() === 'p';
  const toRank = to[1];
  return isPawn && (toRank === '8' || toRank === '1');
}

async function onSquareClick(sq) {
  if (isBusy) return; // ignore clicks while a move is resolving

  if (!selectedSquare) {
    const data = await api(`legal_moves?game_id=${GAME_ID}&square=${sq}`);
    if (data.moves.length > 0) {
      selectedSquare = sq;
      legalTargets = data.moves;
      renderBoard(currentFen);
    }
    return;
  }

  if (sq === selectedSquare) {
    selectedSquare = null;
    legalTargets = [];
    renderBoard(currentFen);
    return;
  }

  if (legalTargets.includes(sq)) {
    let uci = selectedSquare + sq;
    if (isPromotion(selectedSquare, sq)) uci += 'q';

    selectedSquare = null;
    legalTargets = [];
    setBusy(true);

    const result = await api('move', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ game_id: GAME_ID, move: uci }),
    });

    setBusy(false);

    if (result.error) {
      renderBoard(currentFen);
      return;
    }

    renderBoard(result.fen);
    updateStatus(result);

    if (result.narration) {
      addChronicleEntry(result.move_info, result.narration);
      playEffect(result.narration.effect, sq);
    }
  } else {
    const data = await api(`legal_moves?game_id=${GAME_ID}&square=${sq}`);
    if (data.moves.length > 0) {
      selectedSquare = sq;
      legalTargets = data.moves;
    } else {
      selectedSquare = null;
      legalTargets = [];
    }
    renderBoard(currentFen);
  }
}

function setBusy(busy) {
  isBusy = busy;
  thinkingEl.classList.toggle('hidden', !busy);
  boardEl.classList.toggle('busy', busy);
}

function addChronicleEntry(moveInfo, narration) {
  const empty = chronicleEl.querySelector('.chronicle-empty');
  if (empty) empty.remove();

  const entry = document.createElement('div');
  entry.className = 'chronicle-entry';

  const line = document.createElement('div');
  line.className = 'chronicle-line';
  line.textContent = narration.narration;
  entry.appendChild(line);

  const meta = document.createElement('div');
  meta.className = 'chronicle-meta';
  const san = moveInfo && moveInfo.san ? moveInfo.san : '';
  const sourceLabel = narration.source === 'fallback' ? 'scripted' : narration.source;
  const latency = typeof narration.latency_ms === 'number' ? `${narration.latency_ms}ms` : '';
  meta.textContent = [san, sourceLabel, latency].filter(Boolean).join(' · ');
  entry.appendChild(meta);

  chronicleEl.prepend(entry);
  entry.classList.add('pop');
}

document.getElementById('new-game-btn').addEventListener('click', () => startNewGame());
document.getElementById('game-over-new-btn').addEventListener('click', () => startNewGame());

async function startNewGame() {
  const persona = personaSelect.value || undefined;
  const data = await api('new_game', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ game_id: GAME_ID, persona }),
  });
  selectedSquare = null;
  legalTargets = [];
  hideGameOver();
  renderBoard(data.fen);
  updateStatus(data);
  chronicleEl.innerHTML = '<div class="chronicle-entry chronicle-empty">A new battle begins!</div>';
}

async function init() {
  await loadPersonas();
  await loadState();
  await checkHealth();
  setInterval(checkHealth, 30000);
}

init();

const boardEl = document.getElementById('board');
const narrationEl = document.getElementById('narration');
const turnEl = document.getElementById('turn-indicator');
const statusEl = document.getElementById('status');
const effectLayer = document.getElementById('effect-layer');

const GAME_ID = 'default';
let selectedSquare = null;
let legalTargets = [];
let currentFen = null;

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

    const result = await api('move', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ game_id: GAME_ID, move: uci }),
    });

    selectedSquare = null;
    legalTargets = [];

    if (result.error) {
      renderBoard(currentFen);
      return;
    }

    renderBoard(result.fen);
    updateStatus(result);

    if (result.narration) {
      showNarration(result.narration.narration);
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

function showNarration(text) {
  narrationEl.textContent = text;
  narrationEl.classList.remove('pop');
  void narrationEl.offsetWidth; // restart animation
  narrationEl.classList.add('pop');
}

function playEffect(effect, square) {
  const cellEl = boardEl.querySelector(`[data-square="${square}"]`);
  if (!cellEl) return;

  const rect = cellEl.getBoundingClientRect();
  const layerRect = effectLayer.getBoundingClientRect();
  const x = rect.left - layerRect.left + rect.width / 2;
  const y = rect.top - layerRect.top + rect.height / 2;

  const burst = document.createElement('div');
  burst.className = `fx fx-${effect}`;
  burst.style.left = `${x}px`;
  burst.style.top = `${y}px`;
  effectLayer.appendChild(burst);
  burst.addEventListener('animationend', () => burst.remove());

  const particleCount = 14;
  for (let i = 0; i < particleCount; i++) {
    const p = document.createElement('div');
    p.className = `particle particle-${effect}`;
    const angle = (Math.PI * 2 * i) / particleCount + Math.random() * 0.3;
    const dist = 36 + Math.random() * 34;
    p.style.setProperty('--dx', `${Math.cos(angle) * dist}px`);
    p.style.setProperty('--dy', `${Math.sin(angle) * dist}px`);
    p.style.left = `${x}px`;
    p.style.top = `${y}px`;
    effectLayer.appendChild(p);
    p.addEventListener('animationend', () => p.remove());
  }
}

document.getElementById('new-game-btn').addEventListener('click', async () => {
  const data = await api('new_game', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ game_id: GAME_ID }),
  });
  selectedSquare = null;
  legalTargets = [];
  renderBoard(data.fen);
  updateStatus(data);
  narrationEl.textContent = 'A new battle begins!';
});

loadState();

const HEART = '\u2661';
const DIAMOND = '\u2662';

const splash = document.getElementById('splash');
const table = document.getElementById('table');
const overlay = document.getElementById('overlay');
const statusEl = document.getElementById('status');
const aiNote = document.getElementById('ai-note');
const stockBtn = document.getElementById('stock');
const discardBtn = document.getElementById('discard-pile');
const stockStack = document.getElementById('stock-stack');
const discardStack = document.getElementById('discard-stack');
const stockCount = document.getElementById('stock-count');
const overlayTitle = document.getElementById('overlay-title');
const overlayBody = document.getElementById('overlay-body');
const overlayHands = document.getElementById('overlay-hands');

let state = null;
let selected = [];
let aiTimer = null;

function parseCard(code) {
  if (code === 'back') {
    return { back: true, joker: false, rank: '', suit: '', red: false };
  }
  if (code === '*') {
    return { back: false, joker: true, rank: '*', suit: '', red: false };
  }
  const suit = code.slice(-1);
  const rank = code.slice(0, -1);
  const red = suit === HEART || suit === DIAMOND;
  return { back: false, joker: false, rank, suit, red };
}

function fanAngle(index, count) {
  if (count <= 1) {
    return 0;
  }
  const spread = Math.min(26, count * 4.5);
  return -spread / 2 + (spread * index) / (count - 1);
}

function createCard(code, options = {}) {
  const info = parseCard(code);
  const card = document.createElement(options.staticCard ? 'div' : 'button');
  if (!options.staticCard) {
    card.type = 'button';
  }
  card.className = 'card';
  if (options.staticCard) {
    card.classList.add('static');
  }
  if (info.back) {
    card.classList.add('back');
    const pip = document.createElement('span');
    pip.className = 'pip';
    pip.textContent = '♔';
    card.appendChild(pip);
    return card;
  }
  if (info.joker) {
    card.classList.add('joker');
    const pip = document.createElement('span');
    pip.className = 'pip';
    pip.innerHTML = '<span>★</span><span class="joker-word">JOKER</span>';
    card.appendChild(pip);
    return card;
  }
  card.classList.add(info.red ? 'red' : 'black');
  const pip = document.createElement('span');
  pip.className = 'pip';
  pip.textContent = info.suit;
  card.appendChild(pip);
  ['top', 'bottom'].forEach((place) => {
    const corner = document.createElement('span');
    corner.className = `corner ${place}`;
    const rank = document.createElement('span');
    rank.className = 'rank';
    rank.textContent = info.rank;
    const suit = document.createElement('span');
    suit.className = 'suit';
    suit.textContent = info.suit;
    corner.append(rank, suit);
    card.appendChild(corner);
  });
  return card;
}

function currentPlayerKey() {
  if (!state) {
    return null;
  }
  return state.player1.active ? 'player1' : 'player2';
}

function threeMatch(codes) {
  if (codes.length !== 3) {
    return false;
  }
  const ranks = codes.filter((code) => code !== '*').map((code) => code[0]);
  if (ranks.length === 0) {
    return true;
  }
  return ranks.every((rank) => rank === ranks[0]);
}

async function fetchJson(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.error || 'Request failed');
  }
  return response.json();
}

async function sendAction(payload) {
  try {
    const next = await fetchJson('/api/action', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    selected = [];
    render(next);
  } catch (err) {
    statusEl.textContent = err.message;
  }
}

function renderHand(container, player, playerKey) {
  container.replaceChildren();
  container.classList.toggle('hidden', false);
  container.classList.toggle('active', Boolean(player.active));

  const meta = document.createElement('div');
  meta.className = 'hand-meta';
  const name = document.createElement('span');
  name.className = 'hand-name';
  name.textContent = player.name;
  meta.appendChild(name);
  if (player.points !== null && player.points !== undefined) {
    const points = document.createElement('span');
    points.className = 'hand-points';
    points.textContent = `${player.points} point${player.points === 1 ? '' : 's'}`;
    meta.appendChild(points);
  }
  container.appendChild(meta);

  if (player.active && state.phase !== 'over') {
    const tag = document.createElement('div');
    tag.className = 'turn-tag';
    tag.textContent = state.phase === 'discard'
      ? 'Click a card to discard'
      : 'Choosing between the stock and discard piles';
    container.appendChild(tag);
  }

  const row = document.createElement('div');
  row.className = 'cards';
  player.hand.forEach((code, index) => {
    const card = createCard(code);
    card.style.setProperty('--fan', `${fanAngle(index, player.hand.length)}deg`);
    if (playerKey === currentPlayerKey() && selected.includes(index)) {
      card.classList.add('selected');
    }
    if (code !== 'back') {
      card.addEventListener('click', () => onCardClick(playerKey, index));
    }
    row.appendChild(card);
  });
  container.appendChild(row);
}

function renderPiles() {
  const choosing = state.phase === 'choose' && !state.pending_ai && state.phase !== 'over';
  stockBtn.classList.toggle('disabled', !choosing || state.stock_count === 0);
  discardBtn.classList.toggle('disabled', !choosing || !state.discard);

  stockStack.replaceChildren();
  const backs = Math.min(3, Math.max(0, state.stock_count));
  if (backs === 0) {
    const empty = document.createElement('div');
    empty.className = 'empty-slot';
    stockStack.appendChild(empty);
  } else {
    for (let i = 0; i < backs; i += 1) {
      stockStack.appendChild(createCard('back', { staticCard: true }));
    }
  }
  stockCount.textContent = `${state.stock_count} card${state.stock_count === 1 ? '' : 's'}`;

  discardStack.replaceChildren();
  if (!state.discard) {
    const empty = document.createElement('div');
    empty.className = 'empty-slot';
    discardStack.appendChild(empty);
  } else {
    discardStack.appendChild(createCard(state.discard, { staticCard: true }));
  }
}

function renderOverlayHands() {
  overlayHands.replaceChildren();
  [state.player1, state.player2].forEach((player) => {
    const block = document.createElement('div');
    block.className = 'overlay-hand';
    const label = document.createElement('div');
    label.className = 'overlay-hand-label';
    const points = player.points === null ? '' : ` · ${player.points} points`;
    label.textContent = `${player.name}${points}`;
    block.appendChild(label);
    player.hand.forEach((code) => {
      block.appendChild(createCard(code, { staticCard: true }));
    });
    overlayHands.appendChild(block);
  });
}

function scheduleAi() {
  if (aiTimer) {
    clearTimeout(aiTimer);
    aiTimer = null;
  }
  if (!state || !state.pending_ai) {
    return;
  }
  aiTimer = setTimeout(async () => {
    const next = await fetchJson('/api/ai', { method: 'POST' });
    render(next);
  }, 900);
}

function render(nextState) {
  state = nextState;
  splash.classList.add('hidden');
  table.classList.remove('hidden');

  statusEl.textContent = state.error || state.message;
  if (state.vs_ai) {
    aiNote.classList.remove('hidden');
    aiNote.textContent = state.last_ai || 'Playing against the AI';
    if (state.phase === 'over') {
      renderHand(document.getElementById('hand-player2'), state.player2, 'player2');
    } else {
      document.getElementById('hand-player2').classList.add('hidden');
    }
  } else {
    aiNote.classList.add('hidden');
    renderHand(document.getElementById('hand-player2'), state.player2, 'player2');
  }
  renderHand(document.getElementById('hand-player1'), state.player1, 'player1');
  renderPiles();

  if (state.phase === 'over') {
    overlay.classList.remove('hidden');
    overlayTitle.textContent = 'Game over';
    overlayBody.textContent = state.winner;
    renderOverlayHands();
  } else {
    overlay.classList.add('hidden');
  }

  scheduleAi();
}

async function onCardClick(playerKey, index) {
  if (!state || state.pending_ai || state.phase === 'over') {
    return;
  }
  if (playerKey !== currentPlayerKey()) {
    return;
  }
  if (state.phase === 'discard') {
    await sendAction({ action: 'discard_card', player: playerKey, index });
    return;
  }
  if (state.phase !== 'choose') {
    return;
  }

  if (selected.includes(index)) {
    selected = selected.filter((item) => item !== index);
  } else {
    selected = [...selected, index];
  }

  if (selected.length === 3) {
    const codes = selected.map((item) => state[playerKey].hand[item]);
    if (!threeMatch(codes)) {
      selected = [];
      statusEl.textContent = 'Those three cards do not match in rank.';
      renderHand(document.getElementById(`hand-${playerKey}`), state[playerKey], playerKey);
      return;
    }
    await sendAction({ action: 'drop3', player: playerKey, indices: selected });
    return;
  }

  renderHand(document.getElementById(`hand-${playerKey}`), state[playerKey], playerKey);
}

async function startGame(vsAi) {
  selected = [];
  try {
    const next = await fetchJson('/api/new', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ vs_ai: vsAi }),
    });
    overlay.classList.add('hidden');
    render(next);
  } catch (err) {
    statusEl.textContent = err.message;
  }
}

function showSplash() {
  state = null;
  selected = [];
  table.classList.add('hidden');
  overlay.classList.add('hidden');
  splash.classList.remove('hidden');
}

stockBtn.addEventListener('click', () => {
  if (!state || stockBtn.classList.contains('disabled')) {
    return;
  }
  sendAction({ action: 'stock', player: currentPlayerKey() });
});

discardBtn.addEventListener('click', () => {
  if (!state || discardBtn.classList.contains('disabled')) {
    return;
  }
  sendAction({ action: 'discard', player: currentPlayerKey() });
});

document.getElementById('new-game').addEventListener('click', showSplash);
document.getElementById('play-again').addEventListener('click', showSplash);

document.querySelectorAll('.mode-btn[data-vs-ai]').forEach((button) => {
  button.addEventListener('click', () => {
    startGame(button.dataset.vsAi === 'true');
  });
});

fetchJson('/api/rules')
  .then((payload) => {
    document.getElementById('rules-text').textContent = payload.rules.trim();
  })
  .catch(() => {
    document.getElementById('rules-text').textContent = 'Could not load the rules.';
  });

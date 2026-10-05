(() => {
  if (!wordTrace.requireRole('PLAYER')) return;

  const loading = document.getElementById('loadingScreen');
  const content = document.getElementById('gameContent');
  const startOverlay = document.getElementById('startOverlay');
  const boardArea = document.getElementById('boardArea');
  const board = document.getElementById('board');
  const used = document.getElementById('used');
  const dots = Array.from(document.querySelectorAll('.dots i'));
  const startButton = document.getElementById('startButton');
  const quotaError = document.getElementById('quotaError');
  const guessForm = document.getElementById('guessForm');
  const guessInput = document.getElementById('guessInput');
  const gameError = document.getElementById('gameError');
  const roundId = document.getElementById('roundId');
  const guessCount = document.getElementById('guessCount');
  const modal = document.getElementById('resultModal');
  const resultTitle = document.getElementById('resultTitle');
  const resultMessage = document.getElementById('resultMessage');
  const resultMuted = document.getElementById('resultMuted');
  const closeResult = document.getElementById('closeResult');

  let game = null;
  let status = null;

  function renderStatus() {
    const usedToday = status?.gamesUsedToday ?? 0;
    used.textContent = usedToday;
    dots.forEach((dot, index) => dot.classList.toggle('spent', index < usedToday));
  }

  function renderBoard() {
    board.innerHTML = '';
    const rows = game?.guesses || [];
    for (let r = 0; r < 5; r++) {
      const row = document.createElement('div');
      row.className = 'row';
      const guessRow = rows[r];
      for (let i = 0; i < 5; i++) {
        const tile = document.createElement('div');
        tile.className = 'tile';
        if (guessRow) {
          tile.classList.add((guessRow.tiles[i] || 'GREY').toLowerCase());
          tile.textContent = guessRow.guess[i];
        } else {
          tile.classList.add('empty');
          if (game && r === game.guessCount && i === 0) tile.textContent = '·';
        }
        row.appendChild(tile);
      }
      board.appendChild(row);
    }
  }

  function renderGame() {
    if (!game) {
      startOverlay.hidden = false;
      boardArea.hidden = true;
      const remaining = status?.gamesRemainingToday ?? 0;
      startButton.disabled = remaining === 0;
      quotaError.hidden = remaining !== 0;
      return;
    }

    startOverlay.hidden = true;
    boardArea.hidden = false;
    roundId.textContent = `ROUND #${String(game.gameId).padStart(4, '0')}`;
    guessCount.textContent = game.guessCount;
    renderBoard();
    guessForm.hidden = game.completed;
    if (!game.completed) guessInput.focus();
  }

  function showModal() {
    resultTitle.textContent = game.won ? 'YOU CRACKED IT.' : 'KEEP THE LOG RUNNING.';
    resultMessage.textContent = game.message;
    resultMuted.hidden = game.won;
    modal.hidden = false;
  }

  async function load() {
    wordTrace.showError(gameError, '');
    try {
      status = await apiRequest('/api/game/status');
      renderStatus();
      if (status.activeGameId) {
        game = await apiRequest(`/api/game/${status.activeGameId}`);
      } else {
        game = null;
      }
      renderGame();
    } catch (err) {
      wordTrace.showError(gameError, err.message);
    } finally {
      loading.hidden = true;
      content.hidden = false;
    }
  }

  startButton.addEventListener('click', async () => {
    wordTrace.showError(gameError, '');
    startButton.disabled = true;
    try {
      const started = await apiRequest('/api/game/start', { method: 'POST' });
      status = {
        gamesUsedToday: started.gamesUsedToday,
        gamesRemainingToday: started.gamesRemainingToday,
        activeGameId: started.gameId,
      };
      game = await apiRequest(`/api/game/${started.gameId}`);
      guessInput.value = '';
      renderStatus();
      renderGame();
    } catch (err) {
      wordTrace.showError(gameError, err.message);
      startButton.disabled = false;
    }
  });

  guessInput.addEventListener('input', () => {
    guessInput.value = guessInput.value.replace(/[^a-zA-Z]/g, '').toUpperCase();
  });

  guessForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const clean = guessInput.value.toUpperCase();
    if (!/^[A-Z]{5}$/.test(clean)) {
      wordTrace.showError(gameError, 'Enter exactly 5 uppercase letters.');
      return;
    }
    wordTrace.showError(gameError, '');
    try {
      game = await apiRequest(`/api/game/${game.gameId}/guess`, {
        method: 'POST',
        body: JSON.stringify({ guess: clean }),
      });
      guessInput.value = '';
      status = await apiRequest('/api/game/status');
      renderStatus();
      renderGame();
      if (game.completed) showModal();
    } catch (err) {
      wordTrace.showError(gameError, err.message);
    }
  });

  closeResult.addEventListener('click', () => {
    modal.hidden = true;
    game = null;
    load();
  });

  load();
})();

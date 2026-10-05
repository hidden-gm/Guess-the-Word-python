(() => {
  if (!wordTrace.requireRole('ADMIN')) return;

  const today = new Date().toLocaleDateString('en-CA');
  const reportDate = document.getElementById('reportDate');
  const dailyUsers = document.getElementById('dailyUsers');
  const dailyCorrect = document.getElementById('dailyCorrect');
  const userReportForm = document.getElementById('userReportForm');
  const reportUsername = document.getElementById('reportUsername');
  const userRows = document.getElementById('userRows');
  const wordForm = document.getElementById('wordForm');
  const newWord = document.getElementById('newWord');
  const wordPills = document.getElementById('wordPills');
  const wordCount = document.getElementById('wordCount');
  const error = document.getElementById('error');
  reportDate.value = today;

  function setError(message) { wordTrace.showError(error, message); }

  async function loadWords() {
    try {
      const rows = await apiRequest('/api/admin/words');
      wordPills.innerHTML = '';
      wordCount.textContent = rows.length;
      rows.forEach((word) => {
        const pill = document.createElement('div');
        pill.className = 'word-pill';
        const span = document.createElement('span');
        span.textContent = word.value;
        const button = document.createElement('button');
        button.type = 'button';
        button.setAttribute('aria-label', `Delete ${word.value}`);
        button.textContent = '×';
        button.addEventListener('click', async () => {
          try {
            setError('');
            await apiRequest(`/api/admin/words/${word.id}`, { method: 'DELETE' });
            await loadWords();
          } catch (err) { setError(err.message); }
        });
        pill.append(span, button);
        wordPills.appendChild(pill);
      });
    } catch (err) { setError(err.message); }
  }

  async function runDayReport() {
    try {
      setError('');
      const data = await apiRequest(`/api/admin/reports/day?date=${encodeURIComponent(reportDate.value)}`);
      dailyUsers.textContent = data.users;
      dailyCorrect.textContent = data.correctGuesses;
    } catch (err) { setError(err.message); }
  }

  userReportForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const username = reportUsername.value.trim();
    if (!username) return;
    try {
      setError('');
      const rows = await apiRequest(`/api/admin/reports/user/${encodeURIComponent(username)}`);
      userRows.innerHTML = '';
      if (!rows.length) {
        userRows.innerHTML = '<tr><td colspan="3" class="empty-table">No report loaded.</td></tr>';
        return;
      }
      rows.forEach((row) => {
        const tr = document.createElement('tr');
        [row.date, row.wordsTried, row.correctGuesses].forEach((value) => {
          const td = document.createElement('td');
          td.textContent = value;
          tr.appendChild(td);
        });
        userRows.appendChild(tr);
      });
    } catch (err) {
      setError(err.message);
      userRows.innerHTML = '<tr><td colspan="3" class="empty-table">No report loaded.</td></tr>';
    }
  });

  wordForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    try {
      setError('');
      await apiRequest('/api/admin/words', {
        method: 'POST',
        body: JSON.stringify({ value: newWord.value }),
      });
      newWord.value = '';
      await loadWords();
    } catch (err) { setError(err.message); }
  });

  newWord.addEventListener('input', () => {
    newWord.value = newWord.value.replace(/[^a-zA-Z]/g, '').toUpperCase();
  });

  document.getElementById('runReport').addEventListener('click', runDayReport);
  Promise.all([loadWords(), runDayReport()]);
})();

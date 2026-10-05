(() => {
  if (localStorage.getItem('wordtrace_token')) {
    window.location.replace(localStorage.getItem('wordtrace_role') === 'ADMIN' ? '/admin' : '/game');
    return;
  }

  const form = document.getElementById('registerForm');
  const error = document.getElementById('error');
  const button = document.getElementById('submitButton');

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    wordTrace.showError(error, '');
    button.disabled = true;
    button.textContent = 'CREATING…';
    try {
      const data = await apiRequest('/api/auth/register', {
        method: 'POST',
        body: JSON.stringify({
          username: document.getElementById('username').value,
          password: document.getElementById('password').value,
        }),
      });
      localStorage.setItem('wordtrace_token', data.token);
      localStorage.setItem('wordtrace_username', data.username);
      localStorage.setItem('wordtrace_role', data.role);
      window.location.href = '/game';
    } catch (err) {
      wordTrace.showError(error, err.message);
    } finally {
      button.disabled = false;
      button.textContent = 'CREATE PLAYER ↗';
    }
  });
})();

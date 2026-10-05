(function () {
  const token = localStorage.getItem('wordtrace_token');
  const role = localStorage.getItem('wordtrace_role');
  const username = localStorage.getItem('wordtrace_username') || 'PLAYER';

  function goHome() {
    if (!token) return (window.location.href = '/login');
    window.location.href = role === 'ADMIN' ? '/admin' : '/game';
  }

  const topActions = document.getElementById('topActions');
  const navHome = document.getElementById('navHome');
  const logoutButton = document.getElementById('logoutButton');
  const brandButton = document.getElementById('brandButton');

  if (token && topActions) {
    topActions.hidden = false;
    document.getElementById('navUsername').textContent = username;
    document.getElementById('navRole').textContent = role || 'PLAYER';
    navHome.textContent = role === 'ADMIN' ? 'CONTROL' : 'GAME';
  }

  brandButton?.addEventListener('click', goHome);
  navHome?.addEventListener('click', goHome);
  logoutButton?.addEventListener('click', () => {
    localStorage.removeItem('wordtrace_token');
    localStorage.removeItem('wordtrace_username');
    localStorage.removeItem('wordtrace_role');
    window.location.href = '/login';
  });

  window.wordTrace = {
    token,
    role,
    username,
    requireRole(expectedRole) {
      if (!token) {
        window.location.replace('/login');
        return false;
      }
      if (expectedRole && role !== expectedRole) {
        window.location.replace(role === 'ADMIN' ? '/admin' : '/game');
        return false;
      }
      return true;
    },
    showError(element, message) {
      if (!element) return;
      element.textContent = message || '';
      element.hidden = !message;
    },
  };

  window.apiRequest = async function apiRequest(path, options = {}) {
    const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
    const currentToken = localStorage.getItem('wordtrace_token');
    if (currentToken) headers.Authorization = `Bearer ${currentToken}`;

    const response = await fetch(path, { ...options, headers });
    const data = response.status === 204 ? null : await response.json().catch(() => ({}));
    if (!response.ok) {
      if (response.status === 401 && path !== '/api/auth/login' && path !== '/api/auth/register') {
        localStorage.clear();
        window.location.replace('/login');
      }
      throw new Error((data && data.message) || 'Something went wrong.');
    }
    return data;
  };
})();

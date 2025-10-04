// auth.js handles login/register/logout and shows whoami
async function api(path, opts = {}) {
  const base = '/api';
  const res = await fetch(base + path, Object.assign({credentials: 'same-origin', headers: {'Content-Type': 'application/json'}}, opts));
  const json = await res.json().catch(() => ({}));
  return {status: res.status, ok: res.ok, body: json};
}

document.addEventListener('DOMContentLoaded', async () => {
  const loginForm = document.getElementById('login-form');
  const regForm = document.getElementById('register-form');
  const message = document.getElementById('message');

  if (loginForm) {
    loginForm.addEventListener('submit', async e => {
      e.preventDefault();
      const username = document.getElementById('login-username').value;
      const password = document.getElementById('login-password').value;
      const r = await api('/login', {method: 'POST', body: JSON.stringify({username, password})});
      if (!r.ok) {
        message && (message.textContent = r.body.error || 'Login failed');
      } else {
        window.location.href = '/dashboard';
      }
    });
  }

  if (regForm) {
    regForm.addEventListener('submit', async e => {
      e.preventDefault();
      const username = document.getElementById('reg-username').value;
      const password = document.getElementById('reg-password').value;
      const r = await api('/register', {method: 'POST', body: JSON.stringify({username, password})});
      if (!r.ok) {
        message && (message.textContent = r.body.error || 'Registration failed');
      } else {
        message && (message.textContent = 'Registered! You can now log in.');
        regForm.reset();
      }
    });
  }

  // whoami display on dashboard
  const who = document.getElementById('whoami');
  if (who) {
    const r = await api('/whoami');
    if (r.body && r.body.username) who.textContent = r.body.username;
    else window.location.href = '/static/login.html';
  }

  // logout
  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', async () => {
      await api('/logout', {method: 'POST'});
      window.location.href = '/';
    });
  }
});

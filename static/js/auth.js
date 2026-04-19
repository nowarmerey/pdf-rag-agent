const API = "/api";
const TOKEN_KEY = "lexai_token";
const USER_KEY = "lexai_user";

// ═══════════════════════════════
// Token Management
// ═══════════════════════════════
function saveAuth(token, user) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function getUser() {
  const u = localStorage.getItem(USER_KEY);
  return u ? JSON.parse(u) : null;
}

function logout() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  window.location.href = "/login";
}

function requireAuth() {
  if (!getToken()) window.location.href = "/login";
}

// ═══════════════════════════════
// Auth Headers
// ═══════════════════════════════
function authHeaders(isJson = true) {
  const headers = { Authorization: `Bearer ${getToken()}` };
  if (isJson) headers["Content-Type"] = "application/json";
  return headers;
}

// ═══════════════════════════════
// Register
// ═══════════════════════════════
async function handleRegister(fullName, email, password, language) {
  const btn = document.getElementById("submit-btn");
  const err = document.getElementById("error-msg");
  btn.disabled = true;

  try {
    const res = await fetch(`${API}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        full_name: fullName,
        email,
        password,
        language,
      }),
    });

    const data = await res.json();

    if (res.ok) {
      saveAuth(data.access_token, data.user);
      window.location.href = "/dashboard";
    } else {
      err.textContent = data.detail || "Registration failed";
      err.classList.remove("hidden");
    }
  } catch {
    err.textContent = "Connection error. Please try again.";
    err.classList.remove("hidden");
  } finally {
    btn.disabled = false;
  }
}

// ═══════════════════════════════
// Login
// ═══════════════════════════════
async function handleLogin(email, password) {
  const btn = document.getElementById("submit-btn");
  const err = document.getElementById("error-msg");
  btn.disabled = true;

  try {
    const formData = new FormData();
    formData.append("username", email);
    formData.append("password", password);

    const res = await fetch(`${API}/auth/login`, {
      method: "POST",
      body: formData,
    });

    const data = await res.json();

    if (res.ok) {
      saveAuth(data.access_token, data.user);
      window.location.href = "/dashboard";
    } else {
      err.textContent = data.detail || "Login failed";
      err.classList.remove("hidden");
    }
  } catch {
    err.textContent = "Connection error. Please try again.";
    err.classList.remove("hidden");
  } finally {
    btn.disabled = false;
  }
}

// ═══════════════════════════════
// Helpers
// ═══════════════════════════════
function togglePassword() {
  const input = document.querySelector(
    'input[type="password"], input[type="text"]',
  );
  input.type = input.type === "password" ? "text" : "password";
}

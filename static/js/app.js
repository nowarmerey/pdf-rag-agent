let currentSessionId = null;

// ═══════════════════════════════
// Helpers
// ═══════════════════════════════
function getToken() {
  return localStorage.getItem("lexai_token");
}
function getUser() {
  const u = localStorage.getItem("lexai_user");
  return u ? JSON.parse(u) : null;
}
function getLang() {
  return localStorage.getItem("lexai_lang") || "de";
}

// ═══════════════════════════════
// Init
// ═══════════════════════════════
document.addEventListener("DOMContentLoaded", async () => {
  if (!getToken()) {
    window.location.href = "/login";
    return;
  }
  loadTheme();
  // ربط file input
  document
    .getElementById("file-input")
    .addEventListener("change", async (e) => {
      if (e.target.files[0]) await uploadDocument(e.target.files[0]);
    });

  loadUserInfo();
  await loadDocuments();
  await loadSessions();
  setupTextarea();
});

function loadUserInfo() {
  const user = getUser();
  if (!user) return;
  document.getElementById("user-name").textContent = user.full_name;
  document.getElementById("user-email").textContent = user.email;
  setLang(user.language || getLang());
}

// ═══════════════════════════════
// Documents
// ═══════════════════════════════
async function uploadDocument(file) {
  const progress = document.getElementById("upload-progress");
  const fill = document.getElementById("progress-fill");
  const text = document.getElementById("progress-text");

  progress.classList.remove("hidden");
  fill.style.width = "30%";
  text.textContent = `Uploading ${file.name}...`;

  const formData = new FormData();
  formData.append("file", file);

  try {
    fill.style.width = "60%";
    const res = await fetch("/api/documents/upload", {
      method: "POST",
      headers: { Authorization: `Bearer ${getToken()}` },
      body: formData,
    });
    const data = await res.json();
    fill.style.width = "100%";

    if (res.ok) {
      text.textContent = `✓ ${file.name} uploaded`;
      setTimeout(() => progress.classList.add("hidden"), 2000);
      await loadDocuments();
    } else {
      text.textContent = `✗ ${data.detail}`;
      setTimeout(() => progress.classList.add("hidden"), 3000);
    }
  } catch {
    text.textContent = "✗ Connection error";
    setTimeout(() => progress.classList.add("hidden"), 3000);
  }
  document.getElementById("file-input").value = "";
}

async function loadDocuments() {
  try {
    const res = await fetch("/api/documents/", {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    const docs = await res.json();
    renderDocuments(docs);
  } catch (e) {
    console.error("Failed to load documents:", e);
  }
}

function getFileIcon(filename) {
  const ext = filename.split(".").pop().toLowerCase();
  const icons = {
    pdf: "📄",
    docx: "📝",
    doc: "📝",
    jpg: "🖼️",
    jpeg: "🖼️",
    png: "🖼️",
    webp: "🖼️",
  };
  return icons[ext] || "📄";
}

function renderDocuments(docs) {
  const list = document.getElementById("documents-list");
  if (!docs.length) {
    list.innerHTML = `
            <div class="empty-state">
                <span>📄</span>
                <p data-de="Keine Dokumente" 
                   data-en="No documents">Keine Dokumente</p>
            </div>`;
    setLang(getLang());
    return;
  }
  list.innerHTML = docs
    .map(
      (doc) => `
        <div class="doc-item" id="doc-${doc.id}">
            <div class="doc-info">
                <span class="doc-icon">${getFileIcon(doc.filename)}</span>
                <div>
                    <p class="doc-name">${doc.filename}</p>
                    <p class="doc-meta">${doc.file_size} MB · ${doc.chunks_count} chunks</p>
                </div>
            </div>
            <button class="btn-delete" onclick="deleteDocument(${doc.id})">🗑</button>
        </div>
    `,
    )
    .join("");
}

async function deleteDocument(id) {
  const msg = getLang() === "de" ? "Dokument löschen?" : "Delete document?";
  if (!confirm(msg)) return;
  await fetch(`/api/documents/${id}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  await loadDocuments();
}

// ═══════════════════════════════
// Chat Sessions
// ═══════════════════════════════
async function loadSessions() {
  try {
    const res = await fetch("/api/chat/sessions", {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    const sessions = await res.json();
    renderSessions(sessions);
  } catch (e) {
    console.error("Failed to load sessions:", e);
  }
}

function renderSessions(sessions) {
  const list = document.getElementById("sessions-list");
  if (!sessions.length) {
    list.innerHTML = '<p class="no-sessions">–</p>';
    return;
  }
  list.innerHTML = sessions
    .map(
      (s) => `
        <div class="session-item ${s.id === currentSessionId ? "active" : ""}"
             onclick="loadSession(${s.id})">
            <span class="session-icon">💬</span>
            <span class="session-title">${s.title}</span>
            <button class="btn-del-session"
                    onclick="event.stopPropagation(); deleteSession(${s.id})">×</button>
        </div>
    `,
    )
    .join("");
}

async function loadSession(sessionId) {
  currentSessionId = sessionId;
  try {
    const res = await fetch(`/api/chat/sessions/${sessionId}`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    const session = await res.json();
    renderMessages(session.messages);
    await loadSessions();
  } catch (e) {
    console.error("Failed to load session:", e);
  }
}

async function deleteSession(sessionId) {
  await fetch(`/api/chat/sessions/${sessionId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  if (currentSessionId === sessionId) newChat();
  await loadSessions();
}

function newChat() {
  currentSessionId = null;
  document.getElementById("chat-messages").innerHTML = `
        <div class="welcome-message">
            <span class="welcome-icon">⚖️</span>
            <h3 data-de="Willkommen bei LexAI"
                data-en="Welcome to LexAI">Willkommen bei LexAI</h3>
            <p data-de="Laden Sie Rechtsdokumente hoch und stellen Sie Fragen dazu."
               data-en="Upload legal documents and ask questions about them.">
                Laden Sie Rechtsdokumente hoch und stellen Sie Fragen dazu.
            </p>
        </div>`;
  setLang(getLang());
  loadSessions();
}

// ═══════════════════════════════
// Chat
// ═══════════════════════════════
async function sendMessage() {
  const input = document.getElementById("question-input");
  const question = input.value.trim();
  if (!question) return;

  input.value = "";
  input.style.height = "auto";

  addMessage(question, "user");
  const typingEl = addTyping();
  const sendBtn = document.getElementById("send-btn");
  sendBtn.disabled = true;

  try {
    const res = await fetch("/api/chat/", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${getToken()}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question,
        session_id: currentSessionId,
        language: getLang(),
      }),
    });
    const data = await res.json();
    typingEl.remove();

    if (res.ok) {
      currentSessionId = data.session_id;
      addMessage(data.answer, "assistant", data.sources);
      await loadSessions();
    } else {
      addMessage(`Error: ${data.detail}`, "assistant");
    }
  } catch {
    typingEl.remove();
    addMessage("Connection error. Please try again.", "assistant");
  }

  sendBtn.disabled = false;
  input.focus();
}

function addMessage(content, role, sources = []) {
  const container = document.getElementById("chat-messages");
  const div = document.createElement("div");
  div.className = `message ${role}-message`;

  const formatted =
    role === "assistant"
      ? content
          .replace(/^## (.*)/gm, "<h2>$1</h2>")
          .replace(/^### (.*)/gm, "<h3>$1</h3>")
          .replace(/^#### (.*)/gm, "<h4>$1</h4>")
          .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
          .replace(/\*(.*?)\*/g, "<em>$1</em>")
          .replace(/`(.*?)`/g, "<code>$1</code>")
          .replace(/^> (.*)/gm, "<blockquote>$1</blockquote>")
          .replace(/^- (.*)/gm, "<li>$1</li>")
          .replace(/(<li>.*<\/li>)/s, "<ul>$1</ul>")
          .replace(/^─+$/gm, "<hr>")
          .replace(/\n{2,}/g, "<br><br>")
          .replace(/\n/g, "<br>")
      : content;

  const sourcesHtml = sources.length
    ? `<div class="sources">
               <span>📎</span>
               <span>${sources.join(" · ")}</span>
           </div>`
    : "";

  div.innerHTML = `
        <div class="message-bubble">
            <div class="message-content">${formatted}</div>
            ${sourcesHtml}
        </div>`;

  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return div;
}

function renderMessages(messages) {
  const container = document.getElementById("chat-messages");
  container.innerHTML = "";
  messages.forEach((msg) => {
    const sources = msg.sources ? JSON.parse(msg.sources) : [];
    addMessage(msg.content, msg.role, sources);
  });
}

function addTyping() {
  const container = document.getElementById("chat-messages");
  const div = document.createElement("div");
  div.className = "message assistant-message";
  div.innerHTML = `
        <div class="message-bubble">
            <div class="typing-dots">
                <span></span><span></span><span></span>
            </div>
        </div>`;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return div;
}

// ═══════════════════════════════
// Textarea Auto-resize
// ═══════════════════════════════
function setupTextarea() {
  const textarea = document.getElementById("question-input");
  textarea.addEventListener("input", () => {
    textarea.style.height = "auto";
    textarea.style.height = Math.min(textarea.scrollHeight, 150) + "px";
  });
  textarea.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
}
// ═══════════════════════════════
// Theme Toggle
// ═══════════════════════════════
function toggleTheme() {
  const body = document.body;
  const btn = document.getElementById("theme-btn");
  const isLight = body.classList.toggle("light-mode");

  btn.textContent = isLight ? "🌙" : "☀️";
  localStorage.setItem("lexai_theme", isLight ? "light" : "dark");
}

function loadTheme() {
  const theme = localStorage.getItem("lexai_theme");
  const btn = document.getElementById("theme-btn");
  if (theme === "light") {
    document.body.classList.add("light-mode");
    if (btn) btn.textContent = "🌙";
  } else {
    if (btn) btn.textContent = "☀️";
  }
}

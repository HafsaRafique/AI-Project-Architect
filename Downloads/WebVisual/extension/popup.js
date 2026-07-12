const $ = (id) => document.getElementById(id);

let mode = "login"; // or "register"

function send(message) {
  return new Promise((resolve) => chrome.runtime.sendMessage(message, resolve));
}

async function checkBackendHealth() {
  const { apiBase } = await chrome.storage.local.get("apiBase");
  const base = apiBase || "https://pixelrag.onrender.com";
  $("apiBase").value = base;
  try {
    const resp = await fetch(`${base}/health`, { signal: AbortSignal.timeout(2500) });
    $("statusDot").className = resp.ok ? "dot online" : "dot offline";
  } catch {
    $("statusDot").className = "dot offline";
  }
}

async function refreshView() {
  const { token } = await chrome.storage.local.get("token");
  if (token) {
    $("authView").classList.add("hidden");
    $("mainView").classList.remove("hidden");
    await loadPages();
  } else {
    $("authView").classList.remove("hidden");
    $("mainView").classList.add("hidden");
  }
}

function badgeClass(status) {
  return `badge ${status}`;
}

async function loadPages() {
  const res = await send({ type: "LIST_PAGES" });
  const list = $("pageList");
  list.innerHTML = "";
  if (!res.ok) {
    list.innerHTML = `<li class="muted">Could not load pages (${res.error || res.data?.detail || "error"})</li>`;
    return;
  }
  if (res.data.length === 0) {
    list.innerHTML = `<li class="muted">No pages captured yet</li>`;
    return;
  }
  for (const page of res.data) {
    const li = document.createElement("li");
    const title = page.title || page.url;
    li.innerHTML = `<span class="title" title="${title}">${title}</span><span class="${badgeClass(page.status)}">${page.status}</span>`;
    list.appendChild(li);
  }
}

// ---- Auth ----
$("tabLogin").addEventListener("click", () => {
  mode = "login";
  $("tabLogin").classList.add("active");
  $("tabRegister").classList.remove("active");
  $("submitAuth").textContent = "Log in";
});
$("tabRegister").addEventListener("click", () => {
  mode = "register";
  $("tabRegister").classList.add("active");
  $("tabLogin").classList.remove("active");
  $("submitAuth").textContent = "Sign up";
});

$("submitAuth").addEventListener("click", async () => {
  const email = $("email").value.trim();
  const password = $("password").value;
  $("authError").textContent = "";
  if (!email || !password) {
    $("authError").textContent = "Enter an email and password.";
    return;
  }

  if (mode === "register") {
    const res = await send({ type: "REGISTER", email, password });
    if (!res.ok) {
      $("authError").textContent = res.data?.detail || res.error || "Registration failed";
      return;
    }
  }

  const res = await send({ type: "LOGIN", email, password });
  if (!res.ok) {
    $("authError").textContent = res.data?.detail || res.error || "Login failed";
    return;
  }
  await refreshView();
});

$("logoutBtn").addEventListener("click", async () => {
  await send({ type: "LOGOUT" });
  await refreshView();
});

$("saveApiBase").addEventListener("click", async () => {
  const apiBase = $("apiBase").value.trim().replace(/\/$/, "");
  await send({ type: "SET_API_BASE", apiBase });
  await checkBackendHealth();
});

// ---- Capture ----
$("captureBtn").addEventListener("click", async () => {
  $("captureStatus").textContent = "Capturing and sending to the vision model...";
  const res = await send({ type: "CAPTURE_PAGE" });
  if (!res.ok) {
    $("captureStatus").textContent = `Failed: ${res.data?.detail || res.error}`;
    return;
  }
  $("captureStatus").textContent = "Captured! Processing in the background — refresh below.";
  await loadPages();
});

// ---- Ask ----
$("askBtn").addEventListener("click", async () => {
  const question = $("question").value.trim();
  if (!question) return;
  const answerEl = $("answer");
  answerEl.classList.remove("hidden");
  answerEl.innerHTML = "Thinking...";

  const res = await send({ type: "ASK", question });
  if (!res.ok) {
    answerEl.innerHTML = `Error: ${res.data?.detail || res.error}`;
    return;
  }
  const sources = (res.data.sources || [])
    .map((s) => `• ${s.title || s.url}`)
    .join("<br/>");
  answerEl.innerHTML = `${res.data.answer}${sources ? `<div class="sources">Sources:<br/>${sources}</div>` : ""}`;
});

$("question").addEventListener("keydown", (e) => {
  if (e.key === "Enter") $("askBtn").click();
});

(async function init() {
  await checkBackendHealth();
  await refreshView();
})();

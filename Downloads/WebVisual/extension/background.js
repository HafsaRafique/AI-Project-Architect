// PixelRAG background service worker.
// Handles screenshot capture and talks to the self-hosted PixelRAG backend.

const DEFAULT_API_BASE = "https://webvisual.onrender.com";

async function getApiBase() {
  const { apiBase } = await chrome.storage.local.get("apiBase");
  return apiBase || DEFAULT_API_BASE;
}

async function getToken() {
  const { token } = await chrome.storage.local.get("token");
  return token || null;
}

async function apiFetch(path, options = {}) {
  const apiBase = await getApiBase();
  const token = await getToken();
  const headers = options.headers || {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const resp = await fetch(`${apiBase}${path}`, { ...options, headers });
  return resp;
}

async function captureActiveTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab) throw new Error("No active tab found");
  const dataUrl = await chrome.tabs.captureVisibleTab({ format: "png" });
  return { dataUrl, url: tab.url, title: tab.title };
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  (async () => {
    try {
      switch (message.type) {
        case "REGISTER": {
          const resp = await apiFetch("/auth/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: message.email, password: message.password }),
          });
          const data = await resp.json();
          sendResponse({ ok: resp.ok, data });
          break;
        }
        case "LOGIN": {
          const form = new URLSearchParams();
          form.set("username", message.email);
          form.set("password", message.password);
          const resp = await apiFetch("/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: form.toString(),
          });
          const data = await resp.json();
          if (resp.ok) {
            await chrome.storage.local.set({ token: data.access_token });
          }
          sendResponse({ ok: resp.ok, data });
          break;
        }
        case "LOGOUT": {
          await chrome.storage.local.remove("token");
          sendResponse({ ok: true });
          break;
        }
        case "CAPTURE_PAGE": {
          const { dataUrl, url, title } = await captureActiveTab();
          const resp = await apiFetch("/pages", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url, title, image_base64: dataUrl }),
          });
          const data = await resp.json();
          sendResponse({ ok: resp.ok, data });
          break;
        }
        case "LIST_PAGES": {
          const resp = await apiFetch("/pages");
          const data = await resp.json();
          sendResponse({ ok: resp.ok, data });
          break;
        }
        case "GET_PAGE": {
          const resp = await apiFetch(`/pages/${message.pageId}`);
          const data = await resp.json();
          sendResponse({ ok: resp.ok, data });
          break;
        }
        case "ASK": {
          const resp = await apiFetch("/search/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              question: message.question,
              top_k: 5,
              page_id: message.pageId || null,
            }),
          });
          const data = await resp.json();
          sendResponse({ ok: resp.ok, data });
          break;
        }
        case "SET_API_BASE": {
          await chrome.storage.local.set({ apiBase: message.apiBase });
          sendResponse({ ok: true });
          break;
        }
        default:
          sendResponse({ ok: false, error: "Unknown message type" });
      }
    } catch (err) {
      sendResponse({ ok: false, error: err.message || String(err) });
    }
  })();
  return true; // keep the message channel open for the async response
});

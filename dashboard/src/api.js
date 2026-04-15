const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  // Health
  health: () => request("/api/health"),

  // Documents
  listDocuments: () => request("/api/documents"),
  getDocument: (id) => request(`/api/documents/${id}`),
  createDocument: (data) =>
    request("/api/documents", { method: "POST", body: JSON.stringify(data) }),
  updateDocument: (id, data) =>
    request(`/api/documents/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteDocument: (id) =>
    request(`/api/documents/${id}`, { method: "DELETE" }),

  // Search
  searchDocuments: (params) => {
    const qs = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v) qs.set(k, v);
    });
    return request(`/api/search?${qs}`);
  },

  // Zones
  classify: (cognitiveLoad) =>
    request("/api/classify", {
      method: "POST",
      body: JSON.stringify({ cognitive_load: cognitiveLoad }),
    }),
  migrate: (data) =>
    request("/api/migrate", { method: "POST", body: JSON.stringify(data) }),
  zoneSummary: () => request("/api/zones/summary"),
  validate: (data) =>
    request("/api/validate", { method: "POST", body: JSON.stringify(data) }),

  // Sessions
  listSessions: () => request("/api/sessions"),
  createSession: (id) =>
    request("/api/sessions", {
      method: "POST",
      body: JSON.stringify({ session_id: id || undefined }),
    }),
  getSession: (id) => request(`/api/sessions/${id}`),
  startWork: (id) => request(`/api/sessions/${id}/work`, { method: "POST" }),
  endWork: (id, data) =>
    request(`/api/sessions/${id}/end-work`, {
      method: "POST",
      body: JSON.stringify(data || {}),
    }),
  recordLoad: (id, load) =>
    request(`/api/sessions/${id}/load`, {
      method: "POST",
      body: JSON.stringify({ cognitive_load: load }),
    }),
  wrapUp: (id) => request(`/api/sessions/${id}/wrap-up`, { method: "POST" }),
  closeSession: (id) =>
    request(`/api/sessions/${id}/close`, { method: "POST" }),
};

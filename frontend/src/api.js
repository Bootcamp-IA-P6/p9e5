const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function analyzeComment(text) {
  const res = await fetch(`${BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error("API error");
  return res.json();
}

export async function analyzeUrl(url, limit = 50) {
  const res = await fetch(`${BASE}/analyze-url`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, limit }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Error de red" }));
    throw new Error(err.detail || "API error");
  }
  return res.json();
}

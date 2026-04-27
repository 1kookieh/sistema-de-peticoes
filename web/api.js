const API_BASE = "/api/v1";

async function parseJson(response) {
  return response.json().catch(() => ({}));
}

export async function getJson(path, headers = {}) {
  const response = await fetch(`${API_BASE}${path}`, { headers });
  return { response, payload: await parseJson(response) };
}

export async function postJson(path, body, headers = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...headers },
    body: JSON.stringify(body),
  });
  return { response, payload: await parseJson(response) };
}

export async function postForm(path, body, headers = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers,
    body,
  });
  return { response, payload: await parseJson(response) };
}

export async function getBlob(path, headers = {}) {
  const response = await fetch(path, { headers });
  if (!response.ok) {
    throw new Error(response.status === 401 ? "Token da API inválido ou ausente." : "Falha ao abrir arquivo.");
  }
  return response.blob();
}

export function isUsingV1Only() {
  return API_BASE === "/api/v1";
}

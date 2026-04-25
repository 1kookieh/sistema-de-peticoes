const form = document.querySelector("#generator-form");
const pieceType = document.querySelector("#piece-type");
const pieceHint = document.querySelector("#piece-hint");
const profile = document.querySelector("#profile");
const profileDetails = document.querySelector("#profile-details");
const apiToken = document.querySelector("#api-token");
const text = document.querySelector("#text");
const file = document.querySelector("#file");
const fileInfo = document.querySelector("#file-info");
const clearFile = document.querySelector("#clear-file");
const generate = document.querySelector("#generate");
const result = document.querySelector("#result");
const history = document.querySelector("#history");
const refresh = document.querySelector("#refresh");

const MAX_TEXT_CHARS = 200000;
const MAX_FILE_BYTES = 5 * 1024 * 1024;
const MAX_TOTAL_UPLOAD_BYTES = 15 * 1024 * 1024;
const AUTO_VALUE = "auto";

let pieceTypes = [];
let profiles = [];
let defaultProfileId = "judicial-inicial-jef";

function escapeHTML(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function authHeaders(extra = {}) {
  const token = apiToken.value.trim();
  return token ? { ...extra, "X-API-Token": token } : extra;
}

function setMessage(target, message, kind = "muted") {
  target.innerHTML = `<p class="${kind}">${escapeHTML(message)}</p>`;
}

function selectedFiles() {
  return Array.from(file.files || []);
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

function renderPieceTypes(items) {
  const grouped = new Map();
  for (const item of items) {
    if (!grouped.has(item.grupo)) grouped.set(item.grupo, []);
    grouped.get(item.grupo).push(item);
  }
  pieceType.innerHTML = `<option value="${AUTO_VALUE}" selected>Detectar automaticamente pelo texto</option>`;
  for (const [group, groupItems] of grouped) {
    const optgroup = document.createElement("optgroup");
    optgroup.label = group;
    for (const item of groupItems) {
      const option = document.createElement("option");
      option.value = item.id;
      option.textContent = item.nome;
      optgroup.appendChild(option);
    }
    pieceType.appendChild(optgroup);
  }
}

function renderProfileBadges(item) {
  const flags = [];
  if (item.is_default) flags.push({ label: "padrão (PJE/Projudi)", kind: "ok" });
  if (item.require_oab) flags.push({ label: "exige OAB", kind: "neutral" });
  if (item.require_value_cause) flags.push({ label: "exige valor da causa", kind: "neutral" });
  if (item.require_local_data) flags.push({ label: "exige local e data", kind: "neutral" });
  if ((item.required_sections || []).length) {
    flags.push({ label: `${item.required_sections.length} seções mínimas`, kind: "neutral" });
  }
  if (!flags.length) return "";
  return `<div class="badge-row">${flags
    .map((f) => `<span class="badge badge-${f.kind}">${escapeHTML(f.label)}</span>`)
    .join("")}</div>`;
}

function renderProfiles(items, defaultId) {
  profile.innerHTML = "";
  const autoOption = document.createElement("option");
  autoOption.value = AUTO_VALUE;
  autoOption.textContent = "Detectar automaticamente (padrão: Inicial JEF/Federal)";
  autoOption.selected = true;
  profile.appendChild(autoOption);

  for (const item of items) {
    const option = document.createElement("option");
    option.value = item.id;
    const isDefault = item.id === defaultId ? " — padrão" : "";
    option.textContent = `${item.label}${isDefault}`;
    option.title = item.descricao;
    profile.appendChild(option);
  }
}

function profileById(id) {
  return profiles.find((p) => p.id === id);
}

function updateProfileDetails() {
  const value = profile.value;
  if (!value || value === AUTO_VALUE) {
    profileDetails.innerHTML = `
      <strong>Detecção automática</strong>
      <span>auto</span>
      <p>O sistema escolhe o perfil pela peça detectada. Sem peça reconhecida, usa <strong>Inicial JEF/Federal</strong> (PJE/Projudi).</p>
    `;
    return;
  }
  const selected = profileById(value);
  if (!selected) {
    profileDetails.innerHTML = "<p>Selecione um perfil para ver a regra formal aplicada.</p>";
    return;
  }
  const sections = (selected.required_sections || []).length
    ? `<p class="muted">Seções mínimas: ${selected.required_sections.map(escapeHTML).join(" · ")}</p>`
    : "";
  profileDetails.innerHTML = `
    <strong>${escapeHTML(selected.label)}</strong>
    <span>${escapeHTML(selected.id)}</span>
    <p>${escapeHTML(selected.descricao)}</p>
    ${renderProfileBadges(selected)}
    ${sections}
  `;
}

function updatePieceHint() {
  const value = pieceType.value;
  if (!value || value === AUTO_VALUE) {
    pieceHint.innerHTML = `
      <strong>Detecção automática</strong>
      <p>Cole o texto e o sistema identifica a peça pelas palavras-chave (ex.: <em>aposentadoria por idade rural</em>, <em>BPC/LOAS</em>, <em>recurso inominado</em>, <em>procuração ad judicia</em>). Se não reconhecer, segue sem peça e aplica o perfil padrão.</p>
    `;
    return;
  }
  const selected = pieceTypes.find((item) => item.id === value);
  if (!selected) {
    pieceHint.innerHTML = "<p>Peça não encontrada.</p>";
    return;
  }
  pieceHint.innerHTML = `
    <strong>${escapeHTML(selected.grupo)}</strong>
    <p>${escapeHTML(selected.exige_revisao)}</p>
  `;
}

async function loadProfiles() {
  try {
    const response = await fetch("/api/profiles");
    const payload = await response.json();
    profiles = Array.isArray(payload) ? payload : (payload.items || []);
    defaultProfileId = (payload && payload.default) || "judicial-inicial-jef";
    if (!profiles.length) {
      throw new Error("perfis vazios");
    }
    renderProfiles(profiles, defaultProfileId);
    updateProfileDetails();
  } catch {
    setMessage(result, "Não foi possível carregar os perfis de validação.", "warning");
  }
}

async function loadPieceTypes() {
  try {
    const response = await fetch("/api/piece-types");
    const payload = await response.json();
    pieceTypes = payload.items || [];
    renderPieceTypes(pieceTypes);
    updatePieceHint();
  } catch {
    setMessage(result, "Não foi possível carregar os tipos de peça.", "warning");
  }
}

async function fetchWithAuth(url) {
  const response = await fetch(url, { headers: authHeaders() });
  if (!response.ok) throw new Error(response.status === 401 ? "Token da API inválido ou ausente." : "Falha ao abrir arquivo.");
  return response;
}

async function openSecure(url, mode = "open") {
  try {
    const response = await fetchWithAuth(url);
    const blob = await response.blob();
    const objectUrl = URL.createObjectURL(blob);
    if (mode === "download") {
      const anchor = document.createElement("a");
      anchor.href = objectUrl;
      anchor.download = url.split("/").at(-2) || url.split("/").at(-1) || "arquivo";
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(objectUrl);
      return;
    }
    window.open(objectUrl, "_blank", "noopener");
    setTimeout(() => URL.revokeObjectURL(objectUrl), 60000);
  } catch (error) {
    setMessage(result, error.message, "warning");
  }
}

async function loadHistory() {
  try {
    const response = await fetch("/api/reports", { headers: authHeaders() });
    if (!response.ok) {
      setMessage(history, response.status === 401 ? "Informe o token da API para ver o histórico." : "Não foi possível carregar o histórico.", "warning");
      return;
    }
    const payload = await response.json();
    const reports = payload.reports || [];
    history.innerHTML = reports.length
      ? reports.map((item) => `
        <article class="history-item">
          <strong>${escapeHTML(item.name)}</strong>
          <p class="muted">${escapeHTML(item.generated_at || "sem data")} · perfil ${escapeHTML(item.profile || "-")}</p>
          <p>Válidos: ${escapeHTML(item.summary?.validos ?? 0)} · Bloqueados: ${escapeHTML(item.summary?.bloqueados ?? 0)} · Falhas: ${escapeHTML(item.summary?.falhas ?? 0)}</p>
          <div class="link-row">
            <button class="link-button" data-open="/api/reports/${encodeURIComponent(item.name)}">JSON</button>
            <button class="link-button" data-open="/api/reports/${encodeURIComponent(item.html_name)}">HTML</button>
            ${item.first_docx ? `<button class="link-button" data-download="/api/documents/${encodeURIComponent(item.first_docx)}/download">DOCX</button>` : ""}
          </div>
        </article>
      `).join("")
      : "<p class='muted'>Nenhum relatório local encontrado.</p>";
  } catch {
    setMessage(history, "Não foi possível conectar à API local.", "warning");
  }
}

async function loadTextPreviewFromFile(upload) {
  const suffix = upload.name.toLowerCase().split(".").pop();
  if (["txt", "md"].includes(suffix)) {
    text.value = await upload.text();
  } else {
    text.value = "";
  }
}

file.addEventListener("change", async () => {
  const uploads = selectedFiles();
  if (!uploads.length) return;
  const oversized = uploads.find((upload) => upload.size > MAX_FILE_BYTES);
  if (oversized) {
    setMessage(result, `${oversized.name} está acima do limite de ${formatBytes(MAX_FILE_BYTES)}.`, "warning");
    file.value = "";
    return;
  }
  const totalBytes = uploads.reduce((sum, upload) => sum + upload.size, 0);
  if (totalBytes > MAX_TOTAL_UPLOAD_BYTES) {
    setMessage(result, `Arquivos acima do limite total de ${formatBytes(MAX_TOTAL_UPLOAD_BYTES)}.`, "warning");
    file.value = "";
    return;
  }
  fileInfo.textContent = uploads
    .map((upload) => `${upload.name} · ${formatBytes(upload.size)}`)
    .join(" | ") + " · serão processados pelo backend local.";
  clearFile.hidden = false;
  await loadTextPreviewFromFile(uploads[0]);
});

clearFile.addEventListener("click", () => {
  file.value = "";
  fileInfo.textContent = "Nenhum arquivo selecionado. O sistema usará o texto colado abaixo.";
  clearFile.hidden = true;
});

profile.addEventListener("change", updateProfileDetails);
pieceType.addEventListener("change", updatePieceHint);

function validateBeforeGenerate() {
  const uploads = selectedFiles();
  if (uploads.length) return null;
  if (!text.value.trim()) return "Cole um texto ou selecione um arquivo.";
  if (text.value.length > MAX_TEXT_CHARS) return `Texto acima do limite de ${MAX_TEXT_CHARS} caracteres.`;
  return null;
}

async function generateFromUpload(uploads) {
  const body = new FormData();
  for (const upload of uploads) {
    body.append("files", upload);
  }
  body.append("profile_id", profile.value);
  body.append("piece_type_id", pieceType.value);
  body.append("remetente", "frontend.local@example.com");
  body.append("assunto", "Geração por upload local");
  const response = await fetch("/api/documents/upload", {
    method: "POST",
    headers: authHeaders(),
    body,
  });
  return { response, payload: await response.json() };
}

async function generateFromText() {
  const response = await fetch("/api/documents", {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({
      text: text.value,
      profile_id: profile.value,
      piece_type_id: pieceType.value,
      remetente: "frontend.local@example.com",
      assunto: "Geração pelo painel local",
    }),
  });
  return { response, payload: await response.json() };
}

function renderResult(payload) {
  const problems = payload.problems?.length
    ? `<p><strong>Problemas:</strong> ${escapeHTML(payload.problems.join("; "))}</p>`
    : "<p><strong>Validação formal:</strong> sem violações detectadas.</p>";
  const source = payload.source_filename ? `<p class="muted">Fonte: ${escapeHTML(payload.source_filename)}</p>` : "";
  const inferredTag = (kind) => `<span class="badge badge-ok">detectado automaticamente</span>`;
  const piece = payload.piece_type
    ? `<p class="muted">Peça: <strong>${escapeHTML(payload.piece_type.nome)}</strong>${payload.piece_type_inferred ? " " + inferredTag("piece") : ""}</p>`
    : `<p class="muted">Peça: <em>não identificada</em> — texto seguiu sem rótulo, validação formal aplicada com base no perfil.</p>`;
  const profileLine = payload.profile
    ? `<p class="muted">Perfil: <strong>${escapeHTML(payload.profile.label || payload.profile.id)}</strong>${payload.profile_inferred ? " " + inferredTag("profile") : ""}</p>`
    : "";
  result.innerHTML = `
    <h3>Resultado: ${escapeHTML(payload.status)}</h3>
    ${piece}
    ${profileLine}
    ${source}
    ${problems}
    <div class="link-row">
      ${payload.download_url ? `<button class="link-button primary-link" data-download="${escapeHTML(payload.download_url)}">Baixar DOCX</button>` : ""}
      <button class="link-button" data-open="${escapeHTML(payload.report_json_url)}">Relatório JSON</button>
      <button class="link-button" data-open="${escapeHTML(payload.report_html_url)}">Relatório HTML</button>
    </div>
  `;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const validationError = validateBeforeGenerate();
  if (validationError) {
    setMessage(result, validationError, "warning");
    return;
  }

  generate.disabled = true;
  result.innerHTML = "<p>Gerando documento e relatório...</p>";
  try {
    const uploads = selectedFiles();
    const { response, payload } = uploads.length
      ? await generateFromUpload(uploads)
      : await generateFromText();
    if (!response.ok) {
      setMessage(result, payload.detail || "Falha ao gerar documento.", "warning");
      return;
    }
    renderResult(payload);
    await loadHistory();
  } catch {
    setMessage(result, "Não foi possível conectar à API local.", "warning");
  } finally {
    generate.disabled = false;
  }
});

document.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-open], [data-download]");
  if (!button) return;
  if (button.dataset.open) await openSecure(button.dataset.open, "open");
  if (button.dataset.download) await openSecure(button.dataset.download, "download");
});

refresh.addEventListener("click", loadHistory);

apiToken.value = localStorage.getItem("sistemaPeticoesApiToken") || "";
apiToken.addEventListener("input", () => {
  localStorage.setItem("sistemaPeticoesApiToken", apiToken.value.trim());
});

await loadProfiles();
await loadPieceTypes();
await loadHistory();

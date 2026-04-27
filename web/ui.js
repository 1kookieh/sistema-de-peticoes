import { getBlob, getJson, postForm, postJson } from "./api.js";
import {
  AUTO_VALUE,
  THEME_STORAGE_KEY,
  TOKEN_STORAGE_KEY,
  TOKEN_TTL_MS,
  setLimits,
  setPieceTypes,
  setProfiles,
  setTheme,
  state,
} from "./state/store.js";
import {
  renderHistory,
  renderPieceHint,
  renderPieceTypes,
  renderProfileDetails,
  renderProfiles,
  renderResult,
  setMessage,
} from "./render.js";

const dom = {
  form: document.querySelector("#generator-form"),
  pieceType: document.querySelector("#piece-type"),
  pieceHint: document.querySelector("#piece-hint"),
  profile: document.querySelector("#profile"),
  profileDetails: document.querySelector("#profile-details"),
  apiToken: document.querySelector("#api-token"),
  text: document.querySelector("#text"),
  file: document.querySelector("#file"),
  fileInfo: document.querySelector("#file-info"),
  clearFile: document.querySelector("#clear-file"),
  generate: document.querySelector("#generate"),
  generateLabel: document.querySelector("#generate .btn-label"),
  result: document.querySelector("#result"),
  history: document.querySelector("#history"),
  refresh: document.querySelector("#refresh"),
  themeToggle: document.querySelector("#theme-toggle"),
  uploadBox: document.querySelector("#upload-box"),
  steps: document.querySelectorAll(".step-node"),
};

function setStep(active) {
  if (!dom.steps?.length) return;
  dom.steps.forEach((node) => {
    const step = Number(node.dataset.step);
    node.classList.toggle("is-active", step === active);
    node.classList.toggle("is-done", step < active);
  });
}

function setGenerateLoading(isLoading) {
  if (!dom.generate) return;
  dom.generate.disabled = isLoading;
  dom.generate.classList.toggle("is-loading", isLoading);
  if (dom.generateLabel) dom.generateLabel.textContent = isLoading ? "Gerando..." : "Gerar e validar DOCX";
}

function renderFileList(uploads) {
  if (!uploads.length) {
    dom.fileInfo.textContent = "Nenhum arquivo selecionado. O sistema usará o texto colado abaixo.";
    return;
  }
  const total = uploads.reduce((sum, u) => sum + u.size, 0);
  const rows = uploads.map((upload) => `
    <div class="file-row">
      <span class="file-name" title="${upload.name}">${upload.name}</span>
      <span class="file-size">${formatBytes(upload.size)}</span>
    </div>
  `).join("");
  dom.fileInfo.innerHTML = `
    <strong>${uploads.length} arquivo${uploads.length > 1 ? "s" : ""} selecionado${uploads.length > 1 ? "s" : ""}</strong>
    <span class="muted small"> · ${formatBytes(total)} no total</span>
    <div class="file-list">${rows}</div>
  `;
}

function authHeaders(extra = {}) {
  const token = dom.apiToken.value.trim();
  return token ? { ...extra, "X-API-Token": token } : extra;
}

function selectedFiles() {
  return Array.from(dom.file.files || []);
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

async function openSecure(url, mode = "open") {
  try {
    const blob = await getBlob(url, authHeaders());
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
    console.error(error);
    setMessage(dom.result, error.message, "warning");
  }
}

async function loadLimits() {
  try {
    const { response, payload } = await getJson("/limits");
    if (response.ok) setLimits(payload);
  } catch (error) {
    console.warn("Não foi possível carregar limites da API; usando limites locais.", error);
  }
}

async function loadProfiles() {
  try {
    const { response, payload } = await getJson("/profiles");
    if (!response.ok) throw new Error("falha ao carregar perfis");
    const profiles = Array.isArray(payload) ? payload : (payload.items || []);
    setProfiles(profiles, payload.default);
    renderProfiles(dom.profile);
    renderProfileDetails(dom.profileDetails, dom.profile.value);
  } catch (error) {
    console.error(error);
    setMessage(dom.result, "Não foi possível carregar os perfis de validação.", "warning");
  }
}

async function loadPieceTypes() {
  try {
    const { response, payload } = await getJson("/piece-types");
    if (!response.ok) throw new Error("falha ao carregar tipos de peça");
    setPieceTypes(payload.items || []);
    renderPieceTypes(dom.pieceType);
    renderPieceHint(dom.pieceHint, dom.pieceType.value);
  } catch (error) {
    console.error(error);
    setMessage(dom.result, "Não foi possível carregar os tipos de peça.", "warning");
  }
}

async function loadHistory() {
  try {
    const { response, payload } = await getJson("/reports", authHeaders());
    if (!response.ok) {
      setMessage(
        dom.history,
        response.status === 401 ? "Informe o token da API para ver o histórico." : "Não foi possível carregar o histórico.",
        "warning",
      );
      return;
    }
    renderHistory(dom.history, payload.reports || []);
  } catch (error) {
    console.error(error);
    setMessage(dom.history, "Não foi possível conectar à API local. Verifique se o servidor está rodando em http://127.0.0.1:8000/.", "warning");
  }
}

async function loadTextPreviewFromFile(upload) {
  const suffix = upload.name.toLowerCase().split(".").pop();
  dom.text.value = ["txt", "md"].includes(suffix) ? await upload.text() : "";
}

function validateFiles(uploads) {
  if (uploads.length > state.limits.max_upload_files) {
    return `Selecione no máximo ${state.limits.max_upload_files} arquivos por vez.`;
  }
  const oversized = uploads.find((upload) => upload.size > state.limits.max_file_bytes);
  if (oversized) return `${oversized.name} está acima do limite de ${formatBytes(state.limits.max_file_bytes)}.`;
  const totalBytes = uploads.reduce((sum, upload) => sum + upload.size, 0);
  if (totalBytes > state.limits.max_total_upload_bytes) {
    return `Arquivos acima do limite total de ${formatBytes(state.limits.max_total_upload_bytes)}.`;
  }
  return null;
}

function validateBeforeGenerate() {
  const uploads = selectedFiles();
  if (uploads.length) return null;
  if (!dom.text.value.trim()) return "Cole um texto ou selecione um arquivo.";
  if (dom.text.value.length > state.limits.max_text_chars) return `Texto acima do limite de ${state.limits.max_text_chars} caracteres.`;
  return null;
}

async function generateFromUpload(uploads) {
  const body = new FormData();
  for (const upload of uploads) body.append("files", upload);
  body.append("profile_id", dom.profile.value);
  body.append("piece_type_id", dom.pieceType.value);
  body.append("remetente", "frontend.local@example.com");
  body.append("assunto", "Geração por upload local");
  return postForm("/documents/upload", body, authHeaders());
}

async function generateFromText() {
  return postJson(
    "/documents",
    {
      text: dom.text.value,
      profile_id: dom.profile.value,
      piece_type_id: dom.pieceType.value,
      remetente: "frontend.local@example.com",
      assunto: "Geração pelo painel local",
    },
    authHeaders(),
  );
}

function loadStoredToken() {
  try {
    const stored = JSON.parse(localStorage.getItem(TOKEN_STORAGE_KEY) || "null");
    if (!stored || Date.now() - stored.savedAt > TOKEN_TTL_MS) {
      localStorage.removeItem(TOKEN_STORAGE_KEY);
      return "";
    }
    return stored.value || "";
  } catch {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    return "";
  }
}

function applyTheme(theme) {
  setTheme(theme);
  localStorage.setItem(THEME_STORAGE_KEY, theme);
  const resolved = theme === "system"
    ? (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")
    : theme;
  document.documentElement.dataset.theme = resolved;
  if (dom.themeToggle) {
    dom.themeToggle.setAttribute("aria-pressed", String(resolved === "dark"));
    dom.themeToggle.textContent = resolved === "dark" ? "Modo claro" : "Modo escuro";
  }
}

function initTheme() {
  const stored = localStorage.getItem(THEME_STORAGE_KEY) || "system";
  applyTheme(stored);
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
    if (state.theme === "system") applyTheme("system");
  });
}

function bindEvents() {
  async function handleFileSelection() {
    const uploads = selectedFiles();
    if (!uploads.length) {
      renderFileList([]);
      dom.clearFile.hidden = true;
      setStep(dom.text.value.trim() ? 2 : 1);
      return;
    }
    const error = validateFiles(uploads);
    if (error) {
      setMessage(dom.result, error, "warning");
      dom.file.value = "";
      renderFileList([]);
      dom.clearFile.hidden = true;
      return;
    }
    renderFileList(uploads);
    dom.clearFile.hidden = false;
    setStep(2);
    await loadTextPreviewFromFile(uploads[0]);
  }

  dom.file.addEventListener("change", handleFileSelection);

  dom.clearFile.addEventListener("click", () => {
    dom.file.value = "";
    renderFileList([]);
    dom.clearFile.hidden = true;
    setStep(dom.text.value.trim() ? 2 : 1);
  });

  // Drag-and-drop visual feedback no upload-box
  if (dom.uploadBox) {
    ["dragenter", "dragover"].forEach((evt) => {
      dom.uploadBox.addEventListener(evt, (event) => {
        event.preventDefault();
        dom.uploadBox.classList.add("is-dragover");
      });
    });
    ["dragleave", "dragend", "drop"].forEach((evt) => {
      dom.uploadBox.addEventListener(evt, (event) => {
        if (evt === "dragleave" && dom.uploadBox.contains(event.relatedTarget)) return;
        dom.uploadBox.classList.remove("is-dragover");
      });
    });
    dom.uploadBox.addEventListener("drop", async (event) => {
      event.preventDefault();
      const dropped = Array.from(event.dataTransfer?.files || []);
      if (!dropped.length) return;
      const dt = new DataTransfer();
      dropped.forEach((f) => dt.items.add(f));
      dom.file.files = dt.files;
      await handleFileSelection();
    });
  }

  dom.text.addEventListener("input", () => {
    if (dom.text.value.trim() || selectedFiles().length) setStep(2);
    else setStep(1);
  });

  dom.profile.addEventListener("change", () => renderProfileDetails(dom.profileDetails, dom.profile.value));
  dom.pieceType.addEventListener("change", () => renderPieceHint(dom.pieceHint, dom.pieceType.value));
  dom.refresh.addEventListener("click", loadHistory);
  dom.themeToggle?.addEventListener("click", () => applyTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark"));

  dom.apiToken.addEventListener("input", () => {
    localStorage.setItem(
      TOKEN_STORAGE_KEY,
      JSON.stringify({ value: dom.apiToken.value.trim(), savedAt: Date.now() }),
    );
  });

  dom.form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const validationError = validateBeforeGenerate();
    if (validationError) {
      setMessage(dom.result, validationError, "warning");
      return;
    }

    setGenerateLoading(true);
    setStep(3);
    dom.result.innerHTML = "<p class='muted'>Gerando documento e relatório...</p>";
    try {
      const uploads = selectedFiles();
      const { response, payload } = uploads.length
        ? await generateFromUpload(uploads)
        : await generateFromText();
      if (!response.ok) {
        setMessage(dom.result, payload.detail || "Falha ao gerar documento.", "warning");
        return;
      }
      renderResult(dom.result, payload);
      await loadHistory();
    } catch (error) {
      console.error(error);
      setMessage(dom.result, "Não foi possível conectar à API local. Verifique se o servidor está rodando em http://127.0.0.1:8000/.", "warning");
    } finally {
      setGenerateLoading(false);
    }
  });

  document.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-open], [data-download]");
    if (!button) return;
    if (button.dataset.open) await openSecure(button.dataset.open, "open");
    if (button.dataset.download) await openSecure(button.dataset.download, "download");
  });
}

export async function initUI() {
  initTheme();
  dom.apiToken.value = loadStoredToken();
  bindEvents();
  await loadLimits();
  await Promise.all([loadProfiles(), loadPieceTypes(), loadHistory()]);
}

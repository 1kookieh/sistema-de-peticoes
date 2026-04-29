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
  renderLoading,
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
  outputMode: document.querySelector("#output-mode"),
  llmProvider: document.querySelector("#llm-provider"),
  llmModel: document.querySelector("#llm-model"),
  llmConsent: document.querySelector("#llm-consent"),
  llmConsentField: document.querySelector("#llm-consent-field"),
  llmExternalWarning: document.querySelector("#llm-external-warning"),
  text: document.querySelector("#text"),
  file: document.querySelector("#file"),
  fileInfo: document.querySelector("#file-info"),
  clearFile: document.querySelector("#clear-file"),
  generate: document.querySelector("#generate"),
  generateLabel: document.querySelector("#generate .btn-label"),
  formAlert: document.querySelector("#form-alert"),
  result: document.querySelector("#result"),
  themeToggle: document.querySelector("#theme-toggle"),
  uploadBox: document.querySelector("#upload-box"),
  stepHelper: document.querySelector("#step-helper"),
  pasteText: document.querySelector("#paste-text"),
  clearText: document.querySelector("#clear-text"),
  insertExample: document.querySelector("#insert-example"),
  checklistStatus: document.querySelector("#checklist-status"),
  preflightChecks: document.querySelectorAll(".preflight-check"),
  quickChips: document.querySelectorAll("[data-piece-quick]"),
  steps: document.querySelectorAll(".step-node"),
};

const STEP_MESSAGES = {
  1: "Etapa 1 de 3 - escolha o tipo e informe os dados do caso.",
  2: "Etapa 2 de 3 - o backend monta o prompt e chama a IA.",
  3: "Etapa 3 de 3 - baixe o DOCX e confira os alertas.",
};

const EXAMPLE_TEXT = `Cliente relata indeferimento administrativo de beneficio por incapacidade.

Dados essenciais conhecidos:
- houve requerimento administrativo;
- existem exames medicos para conferencia;
- a parte deseja minuta judicial revisavel.

Dados ainda pendentes:
- confirmar DER, NB, documentos medicos, competencia, valor da causa, procuracao e OAB.`;

const EXTERNAL_LLM_PROVIDERS = new Set(["openai", "anthropic", "gemini", "openrouter"]);
const PROVIDER_LABELS = {
  mock: "Mock local (testes)",
  ollama: "Ollama local (sem API externa)",
  openai: "OpenAI (API externa)",
  anthropic: "Anthropic / Claude (API externa)",
};

function setStep(active) {
  if (!dom.steps?.length) return;
  dom.steps.forEach((node) => {
    const step = Number(node.dataset.step);
    const status = node.querySelector(".step-status");
    node.classList.toggle("is-active", step === active);
    node.classList.toggle("is-done", step < active);
    if (status) {
      status.textContent = step < active ? "concluido" : (step === active ? "ativo" : "pendente");
    }
  });
  if (dom.stepHelper) dom.stepHelper.textContent = STEP_MESSAGES[active] || STEP_MESSAGES[1];
}

function selectedFiles() {
  return Array.from(dom.file?.files || []);
}

function hasContent() {
  return Boolean(dom.text.value.trim() || selectedFiles().length);
}

function syncGenerateState() {
  if (dom.generate) dom.generate.disabled = !hasContent();
}

function checkedPreflightCount() {
  return Array.from(dom.preflightChecks || []).filter((item) => item.checked).length;
}

function syncChecklistStatus() {
  const total = dom.preflightChecks?.length || 0;
  const checked = checkedPreflightCount();
  if (!dom.checklistStatus || !total) return;
  dom.checklistStatus.textContent = checked
    ? `${checked} de ${total} itens conferidos`
    : "Conferencia pendente";
  dom.checklistStatus.classList.toggle("is-complete", checked === total);
}

function showFormAlert(message = "") {
  if (!dom.formAlert) return;
  dom.formAlert.hidden = !message;
  dom.formAlert.textContent = message;
}

function setGenerateLoading(isLoading) {
  if (!dom.generate) return;
  dom.generate.disabled = isLoading || !hasContent();
  dom.generate.classList.toggle("is-loading", isLoading);
  if (dom.generateLabel) {
    dom.generateLabel.textContent = isLoading ? "Criando com IA..." : "Criar documento com IA";
  }
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

function authHeaders(extra = {}) {
  const token = dom.apiToken.value.trim();
  return token ? { ...extra, "X-API-Token": token } : extra;
}

function renderFileList(uploads) {
  if (!uploads.length) {
    dom.fileInfo.innerHTML = `
      <strong>Estado vazio</strong>
      <span class="muted small">Nenhum arquivo selecionado. Arraste arquivos ou cole texto abaixo.</span>
    `;
    return;
  }
  const total = uploads.reduce((sum, upload) => sum + upload.size, 0);
  const rows = uploads.map((upload) => `
    <div class="file-row">
      <span class="file-name" title="${upload.name}">${upload.name}</span>
      <span class="file-size">${formatBytes(upload.size)}</span>
    </div>
  `).join("");
  dom.fileInfo.innerHTML = `
    <strong>Arquivo selecionado · ${uploads.length} arquivo${uploads.length > 1 ? "s" : ""}</strong>
    <span class="muted small"> · ${formatBytes(total)} no total</span>
    <div class="file-list">${rows}</div>
  `;
}

function validateFiles(uploads) {
  if (uploads.length > state.limits.max_upload_files) {
    return `Arquivos demais. Envie no maximo ${state.limits.max_upload_files} arquivos por vez.`;
  }
  const oversized = uploads.find((upload) => upload.size > state.limits.max_file_bytes);
  if (oversized) {
    return `Arquivo muito grande. ${oversized.name} esta acima do limite de ${formatBytes(state.limits.max_file_bytes)} por arquivo.`;
  }
  const totalBytes = uploads.reduce((sum, upload) => sum + upload.size, 0);
  if (totalBytes > state.limits.max_total_upload_bytes) {
    return `Arquivos acima do limite total. O limite atual e ${formatBytes(state.limits.max_total_upload_bytes)} por requisicao.`;
  }
  return null;
}

function llmConsentValue() {
  return Boolean(dom.llmConsent?.checked);
}

function selectedLLMProvider() {
  return dom.llmProvider?.value || state.limits.llm_default_provider || "mock";
}

function selectedLLMModel() {
  return dom.llmModel?.value.trim() || null;
}

function renderLLMProviders() {
  if (!dom.llmProvider) return;
  const providers = (state.limits.llm_allowed_providers || [])
    .filter((provider) => provider && provider !== "none");
  const fallback = providers.length ? providers : ["mock"];
  const current = selectedLLMProvider();
  dom.llmProvider.innerHTML = fallback.map((provider) => {
    const selected = provider === current || (!fallback.includes(current) && provider === state.limits.llm_default_provider);
    const label = PROVIDER_LABELS[provider] || provider;
    return `<option value="${provider}"${selected ? " selected" : ""}>${label}</option>`;
  }).join("");
  dom.llmProvider.disabled = !state.limits.llm_allow_client_provider;
  if (dom.llmModel && !dom.llmModel.value && state.limits.llm_default_model) {
    dom.llmModel.placeholder = `Padrao atual: ${state.limits.llm_default_model}`;
  }
}

function syncLLMExternalUI() {
  const needsConsent = EXTERNAL_LLM_PROVIDERS.has(selectedLLMProvider());
  if (dom.llmExternalWarning) dom.llmExternalWarning.hidden = !needsConsent;
  if (dom.llmConsentField) dom.llmConsentField.hidden = !needsConsent;
  if (!needsConsent && dom.llmConsent) dom.llmConsent.checked = false;
}

function validateBeforeGenerate() {
  const uploads = selectedFiles();
  if (EXTERNAL_LLM_PROVIDERS.has(selectedLLMProvider()) && !llmConsentValue()) {
    return "IA externa selecionada: confirme o consentimento antes de enviar dados.";
  }
  if (checkedPreflightCount() === 0) {
    return "Conferencia pendente: marque ao menos um item revisado antes de criar.";
  }
  if (uploads.length) return null;
  if (!dom.text.value.trim()) return "Nenhum conteudo informado. Envie um arquivo ou cole um texto antes de criar.";
  if (dom.text.value.length > state.limits.max_text_chars) {
    return `Texto acima do limite de ${state.limits.max_text_chars} caracteres.`;
  }
  return null;
}

async function loadTextPreviewFromFile(upload) {
  const suffix = upload.name.toLowerCase().split(".").pop();
  dom.text.value = ["txt", "md"].includes(suffix) ? await upload.text() : "";
}

async function loadLimits() {
  try {
    const { response, payload } = await getJson("/limits");
    if (response.ok) {
    setLimits(payload);
      renderLLMProviders();
      syncLLMExternalUI();
    }
  } catch (error) {
    console.warn("Nao foi possivel carregar limites da API; usando limites locais.", error);
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
    setMessage(dom.result, "Nao foi possivel carregar os perfis formais.", "warning");
  }
}

async function loadPieceTypes() {
  try {
    const { response, payload } = await getJson("/piece-types");
    if (!response.ok) throw new Error("falha ao carregar tipos de documento");
    setPieceTypes(payload.items || []);
    renderPieceTypes(dom.pieceType);
    renderPieceHint(dom.pieceHint, dom.pieceType.value);
  } catch (error) {
    console.error(error);
    setMessage(dom.result, "Nao foi possivel carregar os tipos de documento.", "warning");
  }
}

async function generateFromUpload(uploads) {
  const body = new FormData();
  for (const upload of uploads) body.append("files", upload);
  body.append("profile_id", dom.profile.value);
  body.append("piece_type_id", dom.pieceType.value);
  body.append("output_mode", dom.outputMode?.value || "minuta");
  body.append("llm_provider", selectedLLMProvider());
  if (selectedLLMModel()) body.append("llm_model", selectedLLMModel());
  body.append("llm_consent_external_provider", String(llmConsentValue()));
  body.append("remetente", "frontend.local@example.com");
  body.append("assunto", "Criacao por upload local");
  return postForm("/documents/upload", body, authHeaders());
}

async function generateFromText() {
  return postJson(
    "/documents",
    {
      text: dom.text.value,
      profile_id: dom.profile.value,
      piece_type_id: dom.pieceType.value,
      output_mode: dom.outputMode?.value || "minuta",
      consent_external_provider: llmConsentValue(),
      llm: {
        provider: selectedLLMProvider(),
        model: selectedLLMModel(),
        consent_external_provider: llmConsentValue(),
      },
      remetente: "frontend.local@example.com",
      assunto: "Criacao pelo painel local",
    },
    authHeaders(),
  );
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
      showFormAlert("");
      syncGenerateState();
      return;
    }
    const error = validateFiles(uploads);
    if (error) {
      setMessage(dom.result, error, "warning");
      dom.file.value = "";
      renderFileList([]);
      dom.clearFile.hidden = true;
      syncGenerateState();
      return;
    }
    renderFileList(uploads);
    dom.clearFile.hidden = false;
    setStep(2);
    showFormAlert("");
    await loadTextPreviewFromFile(uploads[0]);
    syncGenerateState();
  }

  dom.file.addEventListener("change", handleFileSelection);

  dom.clearFile.addEventListener("click", () => {
    dom.file.value = "";
    renderFileList([]);
    dom.clearFile.hidden = true;
    setStep(dom.text.value.trim() ? 2 : 1);
    syncGenerateState();
  });

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
      dropped.forEach((file) => dt.items.add(file));
      dom.file.files = dt.files;
      await handleFileSelection();
    });
  }

  dom.text.addEventListener("input", () => {
    setStep(dom.text.value.trim() || selectedFiles().length ? 2 : 1);
    showFormAlert("");
    syncGenerateState();
  });

  dom.profile.addEventListener("change", () => renderProfileDetails(dom.profileDetails, dom.profile.value));
  dom.pieceType.addEventListener("change", () => renderPieceHint(dom.pieceHint, dom.pieceType.value));
  dom.llmProvider?.addEventListener("change", syncLLMExternalUI);
  dom.preflightChecks?.forEach((checkbox) => checkbox.addEventListener("change", () => {
    syncChecklistStatus();
    showFormAlert("");
  }));
  dom.quickChips?.forEach((button) => {
    button.addEventListener("click", () => {
      const target = button.dataset.pieceQuick;
      const option = target ? dom.pieceType.querySelector(`option[value="${CSS.escape(target)}"]`) : null;
      if (!option) {
        setMessage(dom.result, "Tipo de peca rapido indisponivel nesta configuracao.", "warning");
        return;
      }
      dom.pieceType.value = target;
      renderPieceHint(dom.pieceHint, dom.pieceType.value);
      dom.quickChips.forEach((chip) => chip.classList.toggle("is-active", chip === button));
    });
  });
  dom.themeToggle?.addEventListener("click", () => applyTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark"));
  dom.clearText?.addEventListener("click", () => {
    dom.text.value = "";
    setStep(selectedFiles().length ? 2 : 1);
    syncGenerateState();
  });
  dom.insertExample?.addEventListener("click", () => {
    dom.text.value = EXAMPLE_TEXT;
    setStep(2);
    syncGenerateState();
    dom.text.focus();
  });
  dom.pasteText?.addEventListener("click", async () => {
    try {
      dom.text.value = await navigator.clipboard.readText();
      setStep(2);
      syncGenerateState();
      dom.text.focus();
    } catch (error) {
      console.error(error);
      setMessage(dom.result, "Nao foi possivel ler a area de transferencia. Cole manualmente com Ctrl+V.", "warning");
    }
  });

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
      showFormAlert(validationError);
      setMessage(dom.result, validationError, "warning");
      return;
    }

    showFormAlert("");
    setGenerateLoading(true);
    setStep(3);
    renderLoading(dom.result, selectedFiles().length ? "Extraindo texto e criando com IA" : "Criando documento com IA");
    try {
      const uploads = selectedFiles();
      const { response, payload } = uploads.length
        ? await generateFromUpload(uploads)
        : await generateFromText();
      if (!response.ok) {
        setMessage(dom.result, payload.detail || "Falha ao criar documento.", "warning");
        return;
      }
      renderResult(dom.result, payload);
    } catch (error) {
      console.error(error);
      setMessage(dom.result, "Nao foi possivel conectar a API local. Verifique se o servidor esta rodando em http://127.0.0.1:8000/.", "warning");
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
  renderFileList([]);
  syncGenerateState();
  syncChecklistStatus();
  syncLLMExternalUI();
  await loadLimits();
  await Promise.all([loadProfiles(), loadPieceTypes()]);
}

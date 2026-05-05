const API_BASE = "/api/v1";
const STORAGE_KEY = "lexdoc.pieces.v2";
const SETTINGS_KEY = "lexdoc.settings.v2";
const TOKEN_KEY = "sistemaPeticoesApiToken";
const TOKEN_TTL_MS = 12 * 60 * 60 * 1000;

const externalProviders = new Set(["openai", "anthropic", "gemini", "openrouter"]);
const providerLabels = {
  mock: "Mock local",
  ollama: "Ollama local",
  openai: "OpenAI",
  anthropic: "Claude",
  gemini: "Gemini",
  openrouter: "OpenRouter",
};

const providerBrand = {
  mock: {
    className: "provider-brand-mock",
    svg: '<svg viewBox="0 0 24 24"><path d="M5 6.5A2.5 2.5 0 0 1 7.5 4h9A2.5 2.5 0 0 1 19 6.5v11a2.5 2.5 0 0 1-2.5 2.5h-9A2.5 2.5 0 0 1 5 17.5v-11Z"/><path d="M8.5 9h7M8.5 15h4.5"/></svg>',
  },
  ollama: {
    className: "provider-brand-ollama",
    svg: '<svg viewBox="0 0 24 24"><path d="M7.4 10.5c0-3 2.1-5.5 4.6-5.5s4.6 2.5 4.6 5.5v7.2a2 2 0 0 1-2 2H9.4a2 2 0 0 1-2-2v-7.2Z"/><path d="M9.5 8.1 8.4 5.2M14.5 8.1l1.1-2.9"/><path d="M10 12.2h.01M14 12.2h.01M10.4 16h3.2"/></svg>',
  },
  openai: {
    className: "provider-brand-openai",
    svg: '<svg viewBox="0 0 24 24"><path d="M12 3.2a4.1 4.1 0 0 1 3.6 2.1 4.1 4.1 0 0 1 4.1 6 4.1 4.1 0 0 1-1.5 6.7 4.1 4.1 0 0 1-6.2 2.7 4.1 4.1 0 0 1-6.1-2.1 4.1 4.1 0 0 1-1.5-6.7 4.1 4.1 0 0 1 4-6.7A4.1 4.1 0 0 1 12 3.2Z"/><path d="M8.4 5.2 12 7.3l3.6-2M19.7 11.3 16.1 13.4v4.2M15.6 20.8v-4.2L12 14.5l-3.6 2.1M4.3 12.1l3.6-2.1V5.8M5.9 18.6l3.6-2.1v-4.2M18.1 5.4l-3.6 2.1v4.2L18.1 14"/></svg>',
  },
  anthropic: {
    className: "provider-brand-claude",
    svg: '<svg viewBox="0 0 24 24"><path d="M12 3.2 14.1 9.9 20.8 12l-6.7 2.1L12 20.8l-2.1-6.7L3.2 12l6.7-2.1L12 3.2Z"/><path d="M12 7.2 13.2 11l3.6 1-3.6 1.2L12 16.8 10.8 13.2 7.2 12l3.6-1L12 7.2Z"/></svg>',
  },
  gemini: {
    className: "provider-brand-gemini",
    svg: '<svg viewBox="0 0 24 24"><path d="M12 3.5c1.1 4.4 3.1 6.4 7.5 7.5-4.4 1.1-6.4 3.1-7.5 7.5-1.1-4.4-3.1-6.4-7.5-7.5 4.4-1.1 6.4-3.1 7.5-7.5Z"/></svg>',
  },
  openrouter: {
    className: "provider-brand-openrouter",
    svg: '<svg viewBox="0 0 24 24"><path d="M4 7h9.5l2.2 3H20"/><path d="M4 17h9.5l2.2-3H20"/><path d="M17.5 8.5 20 10l-2.5 1.5M17.5 12.5 20 14l-2.5 1.5"/></svg>',
  },
};

const state = {
  tab: "dashboard",
  limits: {
    llm_default_provider: "mock",
    llm_default_model: "",
    llm_allowed_providers: ["mock", "ollama", "openai", "anthropic"],
    llm_allow_client_provider: true,
  },
  pieces: loadPieces(),
  files: [],
  settings: loadSettings(),
  backendPieces: [],
  dashboard: null,
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

function escapeHTML(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function icon(id) {
  return `<svg aria-hidden="true"><use href="#${id}"></use></svg>`;
}

function providerIcon(provider) {
  const brand = providerBrand[provider];
  if (!brand) {
    return '<span class="provider-brand provider-brand-generic" aria-hidden="true">IA</span>';
  }
  return `<span class="provider-brand ${brand.className}" aria-hidden="true">${brand.svg}</span>`;
}

function loadPieces() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
  } catch {
    return [];
  }
}

function savePieces() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state.pieces.slice(0, 80)));
}

function loadSettings() {
  try {
    return {
      theme: "light",
      preferLocal: true,
      remember: true,
      strictReview: true,
      ...JSON.parse(localStorage.getItem(SETTINGS_KEY) || "{}"),
    };
  } catch {
    return { theme: "light", preferLocal: true, remember: true, strictReview: true };
  }
}

function saveSettings() {
  if (!state.settings.remember) return;
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(state.settings));
}

function loadStoredToken() {
  try {
    const stored = JSON.parse(localStorage.getItem(TOKEN_KEY) || "null");
    if (!stored || Date.now() - stored.savedAt > TOKEN_TTL_MS) {
      localStorage.removeItem(TOKEN_KEY);
      return "";
    }
    return stored.value || "";
  } catch {
    localStorage.removeItem(TOKEN_KEY);
    return "";
  }
}

function tokenHeaders(extra = {}) {
  const token = $("#api-token")?.value.trim();
  return token ? { ...extra, "X-API-Token": token } : extra;
}

async function getJson(path) {
  const response = await fetch(`${API_BASE}${path}`, { headers: tokenHeaders() });
  return { response, payload: await response.json().catch(() => ({})) };
}

async function postJson(path, body) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: tokenHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(body),
  });
  return { response, payload: await response.json().catch(() => ({})) };
}

async function postForm(path, body) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: tokenHeaders(),
    body,
  });
  return { response, payload: await response.json().catch(() => ({})) };
}

function applyTheme(theme) {
  state.settings.theme = theme;
  const resolved = theme === "system"
    ? (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")
    : theme;
  document.documentElement.dataset.theme = resolved;
  $$("[data-theme-choice]").forEach((button) => button.classList.toggle("is-active", button.dataset.themeChoice === theme));
  saveSettings();
}

function switchTab(tab) {
  state.tab = tab;
  document.body.dataset.activeTab = tab;
  $$(".tab-panel").forEach((panel) => {
    const active = panel.id === `tab-${tab}`;
    panel.classList.toggle("is-active", active);
    panel.hidden = !active;
    panel.style.display = active ? "block" : "none";
  });
  $$("[data-tab-target]").forEach((button) => {
    if (button.classList.contains("tab-button")) {
      button.classList.toggle("is-active", button.dataset.tabTarget === tab);
    }
  });
  const titles = { dashboard: "Início", ai: "IA", pieces: "Peças", settings: "Configurações" };
  $("#page-title").textContent = titles[tab] || "LexDoc";
  if (location.hash !== `#${tab}`) history.replaceState(null, "", `#${tab}`);
  if (tab === "pieces") renderPieces();
  if (tab === "dashboard") renderDashboard();
}

function statusChip(status) {
  const normalized = status === "Finalizado" ? "done" : status === "Falha" ? "failed" : "progress";
  return `<span class="status-chip ${normalized}">${escapeHTML(status)}</span>`;
}

function addMessage(role, html) {
  const template = $("#message-template").content.firstElementChild.cloneNode(true);
  template.classList.add(role);
  template.querySelector(".message-avatar").textContent = role === "user" ? "EU" : "IA";
  template.querySelector(".message-body").innerHTML = html;
  $("#chat-thread").appendChild(template);
  $("#chat-thread").scrollTop = $("#chat-thread").scrollHeight;
}

function addWelcomeMessage() {
  addMessage("assistant", `
    <p><strong>Pronto para conversar.</strong> Descreva no chat o tipo de peça, dados do caso, estratégia, comarca, cliente, processo e qualquer detalhe relevante.</p>
    <p>Quando você pedir uma minuta, eu aciono o backend, gero o DOCX e registro o resultado na aba <strong>Peças</strong>.</p>
  `);
}

function renderSelectOptions() {
  const providerSelect = $("#provider-select");
  if (!providerSelect) return;
  const providers = state.limits.llm_allowed_providers?.length ? state.limits.llm_allowed_providers : ["mock"];
  providerSelect.innerHTML = providers
    .map((provider) => `<option value="${escapeHTML(provider)}">${escapeHTML(providerLabels[provider] || provider)}</option>`)
    .join("");
  providerSelect.value = providers.includes(state.limits.llm_default_provider)
    ? state.limits.llm_default_provider
    : providers[0];
  renderProviderMenu(providers);
  syncProviderUI();
}

function renderProviderMenu(providers) {
  const menu = $("#provider-menu");
  if (!menu) return;
  menu.innerHTML = providers.map((provider) => `
    <button type="button" class="provider-option" data-provider-value="${escapeHTML(provider)}">
      ${providerIcon(provider)}
      <span>${escapeHTML(providerLabels[provider] || provider)}</span>
    </button>
  `).join("");
}

function syncProviderUI() {
  const provider = $("#provider-select").value;
  const external = externalProviders.has(provider);
  const providerIconButton = $("#provider-icon");
  if (providerIconButton) {
    const brand = providerBrand[provider];
    providerIconButton.className = `provider-brand ${brand?.className || "provider-brand-generic"}`;
    providerIconButton.innerHTML = brand?.svg || "IA";
    const label = providerLabels[provider] || provider || "IA";
    $("#provider-button")?.setAttribute("title", `Selecionar IA: ${label}`);
    $("#provider-button")?.setAttribute("aria-label", `Selecionar IA: ${label}`);
  }
  $$(".provider-option").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.providerValue === provider);
  });
  $("#external-consent-row").hidden = !external;
  if (!external) $("#external-consent").checked = false;
  $("#provider-note").textContent = external
    ? "Provider externo selecionado: confirme autorização antes de enviar dados."
    : "Provider local/seguro para testes nesta máquina.";
}

function renderAttachments() {
  const container = $("#attachment-list");
  container.innerHTML = state.files.length
    ? state.files.map((file, index) => `
      <span class="file-pill">
        ${icon("i-paperclip")}
        <span>${escapeHTML(file.name)} (${formatBytes(file.size)})</span>
        <button type="button" aria-label="Remover anexo ${escapeHTML(file.name)}" data-remove-file="${index}">×</button>
      </span>
    `).join("")
    : "";
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

function createLocalPiece(payload, request) {
  const piece = {
    id: crypto.randomUUID(),
    person: "Informado no chat",
    process: "Informado no chat",
    type: payload.piece_type?.nome || "Peça processual",
    status: payload.download_url ? "Finalizado" : "Em andamento",
    provider: payload.llm?.provider || request.provider,
    model: payload.llm?.model || state.limits.llm_default_model || "",
    location: "Informado no chat",
    createdAt: new Date().toISOString(),
    downloadUrl: payload.download_url || "",
    reportHtmlUrl: payload.report_html_url || "",
    reportJsonUrl: payload.report_json_url || "",
    document: payload.document || "",
  };
  state.pieces.unshift(piece);
  savePieces();
  renderDashboard();
  renderPieces();
  return piece;
}

function normalizeBackendPiece(item) {
  return {
    id: item.id || crypto.randomUUID(),
    person: item.person || "Registro local",
    process: item.process || "Não informado",
    type: item.type || item.document || "Peça processual",
    status: item.status || "Em andamento",
    provider: item.provider || state.limits.llm_default_provider,
    model: item.model || state.limits.llm_default_model || "",
    location: item.location || "Cidade/UF não informada",
    createdAt: item.created_at || item.createdAt || new Date().toISOString(),
    downloadUrl: item.download_url || item.downloadUrl || "",
    reportHtmlUrl: item.report_html_url || item.reportHtmlUrl || "",
    reportJsonUrl: item.report_json_url || item.reportJsonUrl || "",
    document: item.document || "",
  };
}

function allPieces() {
  const merged = new Map();
  for (const piece of state.backendPieces.map(normalizeBackendPiece)) merged.set(piece.id, piece);
  for (const piece of state.pieces) merged.set(piece.id, piece);
  return Array.from(merged.values()).sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
}

async function handleGenerate(event) {
  event.preventDefault();
  const text = $("#chat-input").value.trim();
  if (!text && !state.files.length) {
    addMessage("assistant", `<p>Envie uma mensagem ou anexe um arquivo para iniciar a conversa.</p>`);
    return;
  }
  const provider = $("#provider-select").value;
  if (externalProviders.has(provider) && !$("#external-consent").checked) {
    addMessage("assistant", `<p>Provider externo selecionado. Confirme o consentimento antes de enviar dados do caso.</p>`);
    return;
  }

  const request = {
    text,
    provider,
  };

  const fileNames = state.files.map((file) => file.name).join(", ");
  addMessage("user", `
    <p>${escapeHTML(text || "Mensagem com anexos.")}</p>
    ${fileNames ? `<p><strong>Anexos:</strong> ${escapeHTML(fileNames)}</p>` : ""}
  `);
  $("#chat-input").value = "";
  const generateDocument = shouldGenerateDocument(text, state.files);
  setGenerationState(generateDocument ? "Gerando" : "Conversando", "progress");
  $("#send-button").disabled = true;

  try {
    if (generateDocument) {
      addMessage("assistant", `<p><strong>Recebi.</strong> Vou gerar a minuta DOCX porque você pediu uma peça/documento explicitamente.</p>`);
      const { response, payload } = state.files.length
        ? await generateWithUpload(request)
        : await generateWithText(request);
      if (!response.ok) throw new Error(payload.detail || "Falha ao gerar documento.");
      const piece = createLocalPiece(payload, request);
      addMessage("assistant", renderGeneratedMessage(piece, payload));
      setGenerationState("Finalizado", "done");
    } else {
      const { response, payload } = state.files.length
        ? await chatWithUpload(request)
        : await chatWithText(request);
      if (!response.ok) throw new Error(payload.detail || "Falha ao conversar com a IA.");
      addMessage("assistant", renderChatMessage(payload));
      setGenerationState("Pronto", "neutral");
    }
    state.files = [];
    $("#file-input").value = "";
    renderAttachments();
    switchTab("ai");
  } catch (error) {
    console.error(error);
    addMessage("assistant", `<p><strong>Não consegui gerar agora.</strong> ${escapeHTML(error.message)}</p>`);
    setGenerationState("Falha", "failed");
  } finally {
    $("#send-button").disabled = false;
  }
}

function shouldGenerateDocument(text, files) {
  const normalized = text.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  const action = /\b(gerar|gere|criar|crie|elaborar|elabore|fazer|faca|produzir|produza|montar|monte|preparar|prepare)\b/.test(normalized);
  const artifact = /\b(peca|peticao|minuta|docx|documento|inicial|contestacao|recurso|agravo|procuracao|mandado|manifestacao)\b/.test(normalized);
  const explicitDocx = /\b(baixar|download|arquivo)\b.*\b(docx|word|documento)\b/.test(normalized);
  return (action && artifact) || explicitDocx;
}

async function generateWithText(request) {
  return postJson("/documents", {
    text: request.text,
    consent_external_provider: $("#external-consent").checked,
    remetente: "frontend.local@example.com",
    assunto: "Criação pelo chat LexDoc",
    llm: {
      provider: request.provider,
      consent_external_provider: $("#external-consent").checked,
    },
  });
}

async function generateWithUpload(request) {
  const body = new FormData();
  for (const file of state.files) body.append("files", file);
  body.append("llm_provider", request.provider);
  body.append("llm_consent_external_provider", String($("#external-consent").checked));
  body.append("remetente", "frontend.local@example.com");
  body.append("assunto", "Criação por upload no chat LexDoc");
  return postForm("/documents/upload", body);
}

async function chatWithText(request) {
  return postJson("/chat", {
    text: request.text,
    provider: request.provider,
    consent_external_provider: $("#external-consent").checked,
  });
}

async function chatWithUpload(request) {
  const body = new FormData();
  for (const file of state.files) body.append("files", file);
  body.append("text", request.text || "");
  body.append("provider", request.provider);
  body.append("consent_external_provider", String($("#external-consent").checked));
  return postForm("/chat/upload", body);
}

function renderChatMessage(payload) {
  return `
    <p>${escapeHTML(payload.answer || "Sem resposta retornada pela IA.").replaceAll("\n", "<br>")}</p>
    <p class="message-meta">${escapeHTML(providerLabels[payload.provider] || payload.provider || "IA")} ${payload.model ? `· ${escapeHTML(payload.model)}` : ""}</p>
  `;
}

function renderGeneratedMessage(piece, payload) {
  const problems = payload.problems?.length
    ? `<p><strong>Alertas:</strong> ${payload.problems.map(escapeHTML).join("; ")}</p>`
    : `<p>Minuta criada sem bloqueios formais retornados pelo backend.</p>`;
  return `
    <p><strong>${escapeHTML(piece.type)}</strong> ${statusChip(piece.status)}</p>
    <p>Resultado registrado a partir da conversa.</p>
    ${problems}
    <div class="message-actions">
      ${piece.downloadUrl ? `<button class="mini-action" type="button" data-download="${escapeHTML(piece.downloadUrl)}">${icon("i-download")}Baixar DOCX</button>` : ""}
      ${piece.reportHtmlUrl ? `<button class="mini-action" type="button" data-open="${escapeHTML(piece.reportHtmlUrl)}">${icon("i-eye")}Visualizar relatório</button>` : ""}
      <button class="mini-action" type="button" data-tab-target="pieces">${icon("i-file")}Ver na lista</button>
    </div>
  `;
}

function setGenerationState(label, kind) {
  const chip = $("#generation-state");
  chip.textContent = label;
  chip.className = `status-chip ${kind}`;
}

function renderDashboard() {
  const pieces = allPieces();
  const backendMetrics = state.dashboard?.metrics || {};
  const total = Math.max(pieces.length, Number(backendMetrics.total || 0));
  const final = Math.max(pieces.filter((piece) => piece.status === "Finalizado").length, Number(backendMetrics.finalized || 0));
  const progress = Math.max(
    pieces.filter((piece) => piece.status === "Em andamento").length,
    Number(backendMetrics.in_progress || 0),
  );
  $("#metric-total").textContent = total;
  $("#metric-progress").textContent = progress;
  $("#metric-final").textContent = final;
  $("#metric-provider").textContent = providerLabels[state.limits.llm_default_provider] || state.limits.llm_default_provider || "--";
  $("#metric-model").textContent = state.limits.llm_default_model || "Modelo definido pelo backend";
  $("#side-provider").textContent = `${providerLabels[state.limits.llm_default_provider] || state.limits.llm_default_provider || "Provider"} ativo`;
  $("#settings-provider").textContent = providerLabels[state.limits.llm_default_provider] || state.limits.llm_default_provider || "--";
  $("#settings-model").textContent = state.limits.llm_default_model || "--";
  $("#settings-allowed").textContent = (state.limits.llm_allowed_providers || []).join(", ") || "--";

  const recent = pieces.slice(0, 5);
  $("#recent-list").innerHTML = recent.length
    ? recent.map((piece) => `
      <article class="activity-item">
        <div>
          <strong>${escapeHTML(piece.person)}</strong>
          <p>${escapeHTML(piece.type)} - ${escapeHTML(piece.process)}</p>
        </div>
        ${statusChip(piece.status)}
      </article>
    `).join("")
    : `<p class="note">Nenhuma peça gerada ainda. Abra a aba IA para criar a primeira.</p>`;
  renderMonthlyEvolution(state.dashboard?.monthly_evolution || monthlyFallbackFromPieces(pieces));
  renderTopTypesChart(state.dashboard?.top_piece_types || topTypesFallbackFromPieces(pieces));
  renderLocationChart(state.dashboard?.by_location || locationFallbackFromPieces(pieces));
}

function monthlyFallbackFromPieces(pieces) {
  const formatter = new Intl.DateTimeFormat("pt-BR", { month: "short", year: "2-digit" });
  const counts = new Map();
  for (const piece of pieces) {
    const date = new Date(piece.createdAt);
    const label = Number.isNaN(date.getTime()) ? "Sem data" : formatter.format(date).replace(" de ", " ");
    counts.set(label, (counts.get(label) || 0) + 1);
  }
  return Array.from(counts, ([label, total]) => ({ label, total })).slice(-6);
}

function topTypesFallbackFromPieces(pieces) {
  const counts = new Map();
  for (const piece of pieces) counts.set(piece.type, (counts.get(piece.type) || 0) + 1);
  return Array.from(counts, ([label, total]) => ({ label, total }))
    .sort((a, b) => b.total - a.total)
    .slice(0, 5);
}

function locationFallbackFromPieces(pieces) {
  const counts = new Map();
  for (const piece of pieces) {
    const label = piece.location || "Cidade/UF não informada";
    counts.set(label, (counts.get(label) || 0) + 1);
  }
  return Array.from(counts, ([label, total]) => ({ label, total }))
    .sort((a, b) => b.total - a.total)
    .slice(0, 5);
}

function renderMonthlyEvolution(items) {
  const container = $("#monthly-chart");
  if (!container) return;
  const normalized = buildMonthlySeries(items);
  if (!normalized.some((item) => Number(item.total || 0) > 0)) {
    container.innerHTML = `<div class="chart-empty dark">${icon("i-chart")} Nenhuma evolução mensal registrada ainda.</div>`;
    return;
  }
  const maxValue = Math.max(...normalized.map((item) => Number(item.total || 0)), 1);
  const axisMax = maxValue <= 2 ? 2 : Math.ceil(maxValue / 2) * 2;
  const yTicks = axisMax === 2 ? [0, 0.5, 1, 1.5, 2] : [0, axisMax * 0.25, axisMax * 0.5, axisMax * 0.75, axisMax];
  const width = 680;
  const height = 315;
  const pad = { top: 28, right: 30, bottom: 58, left: 58 };
  const usableW = width - pad.left - pad.right;
  const usableH = height - pad.top - pad.bottom;
  const points = normalized.map((item, index) => {
    const x = pad.left + (normalized.length === 1 ? usableW / 2 : (index / (normalized.length - 1)) * usableW);
    const y = pad.top + usableH - (Number(item.total || 0) / axisMax) * usableH;
    return { x, y, item };
  });
  const baselineY = height - pad.bottom;
  const smoothPath = smoothPathFromPoints(points);
  const smoothArea = `${smoothPath} L${width - pad.right} ${baselineY} L${pad.left} ${baselineY} Z`;
  container.innerHTML = `
    <div class="line-chart-card">
      <svg class="line-chart-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="Evolução mensal de peças">
        <defs>
          <linearGradient id="monthlyFill" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stop-color="#d8a354" stop-opacity=".28"></stop>
            <stop offset="100%" stop-color="#7fb285" stop-opacity="0"></stop>
          </linearGradient>
        </defs>
        <g class="chart-grid dark-grid">
          ${yTicks.map((tick) => {
            const y = pad.top + usableH - (tick / axisMax) * usableH;
            return `<path d="M${pad.left} ${y}H${width - pad.right}"></path>`;
          }).join("")}
          ${points.map((point) => `<path d="M${point.x} ${pad.top}V${baselineY}"></path>`).join("")}
        </g>
        <path class="monthly-area" d="${smoothArea}"></path>
        <path class="monthly-line secondary" d="${smoothPath}"></path>
        <path class="monthly-line primary" d="${smoothPath}"></path>
        ${points.map((point, index) => `
          <g class="chart-hit monthly-hit" tabindex="0" role="listitem" aria-label="${escapeHTML(point.item.label)}: ${Number(point.item.total || 0)} peças">
            <title>${escapeHTML(point.item.label)}: ${Number(point.item.total || 0)} peças geradas</title>
            <rect x="${point.x - 22}" y="${pad.top}" width="44" height="${usableH}" rx="6"></rect>
            <circle class="monthly-point" cx="${point.x}" cy="${point.y}" r="${index === points.length - 1 ? 5.5 : 4.5}"></circle>
            <text class="chart-hover-label" x="${point.x}" y="${Math.max(18, point.y - 14)}" text-anchor="middle">${Number(point.item.total || 0)}</text>
          </g>
        `).join("")}
        ${yTicks.map((tick) => {
          const y = pad.top + usableH - (tick / axisMax) * usableH;
          return `<text class="chart-axis y" x="${pad.left - 12}" y="${y + 4}" text-anchor="end">${formatTick(tick)}</text>`;
        }).join("")}
        ${points.map((point) => `<text class="chart-axis x" x="${point.x}" y="${height - 28}" text-anchor="middle">${escapeHTML(point.item.label)}</text>`).join("")}
      </svg>
      <div class="chart-legend">
        <span><i class="legend-dot orange"></i>Peças geradas</span>
        <span><i class="legend-dot green"></i>Tendência</span>
      </div>
    </div>
  `;
}

function renderTopTypesChart(items) {
  const container = $("#top-types-chart");
  if (!container) return;
  const normalized = (items || []).filter((item) => Number(item.total || 0) > 0).slice(0, 5);
  if (!normalized.length) {
    container.innerHTML = `<div class="chart-empty dark">Nenhum tipo de peça gerado ainda.</div>`;
    return;
  }
  const maxValue = Math.max(...normalized.map((item) => Number(item.total || 0)), 1);
  const width = 680;
  const rowHeight = 74;
  const height = 116 + normalized.length * rowHeight;
  const pad = { top: 32, right: 32, bottom: 48, left: 150 };
  const usableW = width - pad.left - pad.right;
  const xTicks = maxValue === 1 ? [0, 0.25, 0.5, 0.75, 1] : [0, maxValue * 0.25, maxValue * 0.5, maxValue * 0.75, maxValue];
  container.innerHTML = `
    <svg class="ranking-chart-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="Top 5 tipos de peça">
      <g class="chart-grid dark-grid">
        ${xTicks.map((tick) => {
          const x = pad.left + (tick / maxValue) * usableW;
          return `<path d="M${x} ${pad.top}V${height - pad.bottom}"></path>`;
        }).join("")}
      </g>
      ${normalized.map((item, index) => {
        const total = Number(item.total || 0);
        const y = pad.top + index * rowHeight + 18;
        const barWidth = Math.max(8, (total / maxValue) * usableW);
        return `
          <text class="chart-axis y label" x="${pad.left - 12}" y="${y + 25}" text-anchor="end">${escapeHTML(shortLabel(item.label, 20))}</text>
          <g class="chart-hit bar-hit" tabindex="0" role="listitem" aria-label="${escapeHTML(item.label)}: ${total} peças">
            <title>${escapeHTML(item.label)}: ${total} peças</title>
            <rect class="horizontal-bar" x="${pad.left}" y="${y}" width="${barWidth}" height="44" rx="4"></rect>
            <text class="bar-value-label" x="${pad.left + barWidth - 14}" y="${y + 28}" text-anchor="end">${total}</text>
          </g>
        `;
      }).join("")}
      ${xTicks.map((tick) => {
        const x = pad.left + (tick / maxValue) * usableW;
        return `<text class="chart-axis x" x="${x}" y="${height - 16}" text-anchor="middle">${formatTick(tick)}</text>`;
      }).join("")}
    </svg>
  `;
}

function renderLocationChart(items) {
  const container = $("#location-chart");
  if (!container) return;
  const normalized = (items || []).filter((item) => Number(item.total || 0) > 0).slice(0, 5);
  if (!normalized.length) {
    container.innerHTML = `<div class="chart-empty dark">Nenhuma cidade/UF registrada nas peças geradas.</div>`;
    return;
  }
  const maxValue = Math.max(...normalized.map((item) => Number(item.total || 0)), 1);
  const axisMax = maxValue <= 2 ? 2 : Math.ceil(maxValue / 2) * 2;
  const yTicks = axisMax === 2 ? [0, 0.5, 1, 1.5, 2] : [0, axisMax * 0.25, axisMax * 0.5, axisMax * 0.75, axisMax];
  const width = 680;
  const height = 315;
  const pad = { top: 28, right: 28, bottom: 48, left: 58 };
  const usableW = width - pad.left - pad.right;
  const usableH = height - pad.top - pad.bottom;
  const slot = usableW / normalized.length;
  const barWidth = normalized.length === 1 ? usableW * 0.78 : Math.min(122, slot * 0.78);
  container.innerHTML = `
    <svg class="location-chart-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="Peças por cidade e UF">
      <g class="chart-grid dark-grid">
        ${yTicks.map((tick) => {
          const y = pad.top + usableH - (tick / axisMax) * usableH;
          return `<path d="M${pad.left} ${y}H${width - pad.right}"></path>`;
        }).join("")}
        ${normalized.map((_, index) => {
          const x = pad.left + index * slot + slot / 2;
          return `<path d="M${x} ${pad.top}V${pad.top + usableH}"></path>`;
        }).join("")}
      </g>
      ${yTicks.map((tick) => {
        const y = pad.top + usableH - (tick / axisMax) * usableH;
        return `<text class="chart-axis y" x="${pad.left - 12}" y="${y + 4}" text-anchor="end">${formatTick(tick)}</text>`;
      }).join("")}
      ${normalized.map((item, index) => {
        const total = Number(item.total || 0);
        const x = pad.left + index * slot + (slot - barWidth) / 2;
        const barHeight = (total / axisMax) * usableH;
        const y = pad.top + usableH - barHeight;
        return `
          <g class="chart-hit bar-hit" tabindex="0" role="listitem" aria-label="${escapeHTML(item.label)}: ${total} peças">
            <title>${escapeHTML(item.label)}: ${total} peças</title>
            <rect class="vertical-bar" x="${x}" y="${y}" width="${barWidth}" height="${barHeight}" rx="5"></rect>
            <text class="bar-value-label" x="${x + barWidth / 2}" y="${Math.max(18, y - 12)}" text-anchor="middle">${total}</text>
          </g>
          <text class="chart-axis x" x="${x + barWidth / 2}" y="${height - 17}" text-anchor="middle">${escapeHTML(shortLocationLabel(item.label))}</text>
        `;
      }).join("")}
    </svg>
  `;
}

function buildMonthlySeries(items) {
  const byLabel = new Map((items || []).map((item) => [String(item.label), Number(item.total || 0)]));
  const labels = lastSixMonthLabels();
  const series = labels.map((label) => ({ label, total: byLabel.get(label) || 0 }));
  if (series.some((item) => item.total > 0)) return series;
  return (items || []).slice(-6).map((item) => ({
    label: String(item.label || "Sem data"),
    total: Number(item.total || 0),
  }));
}

function lastSixMonthLabels() {
  const monthNames = ["jan.", "fev.", "mar.", "abr.", "mai.", "jun.", "jul.", "ago.", "set.", "out.", "nov.", "dez."];
  const today = new Date();
  return Array.from({ length: 6 }, (_, index) => {
    const date = new Date(today.getFullYear(), today.getMonth() - 5 + index, 1);
    return `${monthNames[date.getMonth()]} ${String(date.getFullYear()).slice(-2)}`;
  });
}

function smoothPathFromPoints(points) {
  if (!points.length) return "";
  if (points.length === 1) return `M${points[0].x} ${points[0].y}`;
  return points.reduce((path, point, index) => {
    if (index === 0) return `M${point.x} ${point.y}`;
    const previous = points[index - 1];
    const controlX = previous.x + (point.x - previous.x) * 0.55;
    return `${path} C${controlX} ${previous.y}, ${controlX} ${point.y}, ${point.x} ${point.y}`;
  }, "");
}

function formatTick(value) {
  const rounded = Math.round(value * 100) / 100;
  return Number.isInteger(rounded) ? String(rounded) : String(rounded).replace(".", ",");
}

function shortLabel(value, max = 18) {
  const text = String(value || "--");
  return text.length > max ? `${text.slice(0, max - 3)}...` : text;
}

function shortLocationLabel(value) {
  const text = String(value || "--");
  if (text.toLowerCase().includes("não informada") || text.toLowerCase().includes("nao informada")) {
    return "S/I";
  }
  const match = text.match(/([A-Z]{2})$/i);
  if (match) return match[1].toUpperCase();
  return shortLabel(text, 10).toUpperCase();
}

function renderPieces() {
  const query = ($("#piece-search")?.value || "").toLowerCase().trim();
  const rows = allPieces().filter((piece) => {
    const haystack = `${piece.person} ${piece.process} ${piece.type} ${piece.status}`.toLowerCase();
    return !query || haystack.includes(query);
  });
  $("#pieces-table-body").innerHTML = rows.length
    ? rows.map((piece) => `
      <tr>
        <td><strong>${escapeHTML(piece.person)}</strong><br><small>${new Date(piece.createdAt).toLocaleString("pt-BR")}</small></td>
        <td>${escapeHTML(piece.process)}</td>
        <td>${escapeHTML(piece.type)}</td>
        <td>${statusChip(piece.status)}</td>
        <td>${escapeHTML(providerLabels[piece.provider] || piece.provider || "--")}</td>
        <td>
          <div class="row-actions">
            ${piece.reportHtmlUrl ? `<button class="mini-action" type="button" data-open="${escapeHTML(piece.reportHtmlUrl)}">${icon("i-eye")}Visualizar</button>` : `<button class="mini-action" type="button" disabled>${icon("i-eye")}Visualizar</button>`}
            ${piece.downloadUrl ? `<button class="mini-action" type="button" data-download="${escapeHTML(piece.downloadUrl)}">${icon("i-download")}Baixar</button>` : `<button class="mini-action" type="button" disabled>${icon("i-download")}Baixar</button>`}
          </div>
        </td>
      </tr>
    `).join("")
    : `<tr><td class="empty-row" colspan="6">Nenhuma peça gerada encontrada.</td></tr>`;
}

async function openSecure(url, mode = "open") {
  const response = await fetch(url, { headers: tokenHeaders() });
  if (!response.ok) {
    addMessage("assistant", `<p>Não consegui abrir o arquivo. Verifique token ou permissão.</p>`);
    return;
  }
  const blob = await response.blob();
  const objectUrl = URL.createObjectURL(blob);
  if (mode === "download") {
    const anchor = document.createElement("a");
    anchor.href = objectUrl;
    anchor.download = url.split("/").at(-2) || url.split("/").at(-1) || "documento";
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(objectUrl);
    return;
  }
  window.open(objectUrl, "_blank", "noopener");
  setTimeout(() => URL.revokeObjectURL(objectUrl), 60000);
}

async function loadApiState() {
  try {
    const [{ response: limitsResponse, payload: limits }, dashboardResult, backendPiecesResult] = await Promise.all([
      getJson("/limits"),
      getJson("/dashboard").catch(() => ({ response: { ok: false }, payload: {} })),
      getJson("/pieces").catch(() => ({ response: { ok: false }, payload: {} })),
    ]);
    if (limitsResponse.ok) state.limits = { ...state.limits, ...limits };
    if (dashboardResult.response.ok) state.dashboard = dashboardResult.payload;
    if (backendPiecesResult.response.ok) state.backendPieces = backendPiecesResult.payload.items || [];
    $("#api-health-label").textContent = "Online em 127.0.0.1";
  } catch (error) {
    console.warn(error);
    $("#api-health-label").textContent = "Offline ou indisponível";
  }
  renderSelectOptions();
  renderDashboard();
  renderPieces();
}

async function syncReports() {
  try {
    const { response, payload } = await getJson("/pieces");
    if (!response.ok) return;
    state.backendPieces = payload.items || [];
    const dashboardResult = await getJson("/dashboard").catch(() => ({ response: { ok: false }, payload: {} }));
    if (dashboardResult.response.ok) state.dashboard = dashboardResult.payload;
    renderDashboard();
    renderPieces();
  } catch (error) {
    console.warn(error);
  }
}

function bindEvents() {
  document.addEventListener("click", async (event) => {
    const tabButton = event.target.closest("[data-tab-target]");
    if (tabButton) switchTab(tabButton.dataset.tabTarget);
    const removeFileButton = event.target.closest("[data-remove-file]");
    if (removeFileButton) {
      const index = Number(removeFileButton.dataset.removeFile);
      state.files.splice(index, 1);
      $("#file-input").value = "";
      renderAttachments();
      return;
    }
    const providerButton = event.target.closest("#provider-button");
    if (providerButton) {
      const menu = $("#provider-menu");
      const open = menu.hidden;
      menu.hidden = !open;
      providerButton.setAttribute("aria-expanded", String(open));
      return;
    }
    const providerOption = event.target.closest("[data-provider-value]");
    if (providerOption) {
      $("#provider-select").value = providerOption.dataset.providerValue;
      $("#provider-menu").hidden = true;
      $("#provider-button").setAttribute("aria-expanded", "false");
      syncProviderUI();
      return;
    }
    if (!event.target.closest(".provider-picker") && $("#provider-menu")) {
      $("#provider-menu").hidden = true;
      $("#provider-button")?.setAttribute("aria-expanded", "false");
    }
    const openButton = event.target.closest("[data-open]");
    if (openButton) await openSecure(openButton.dataset.open, "open");
    const downloadButton = event.target.closest("[data-download]");
    if (downloadButton) await openSecure(downloadButton.dataset.download, "download");
  });
  $("#chat-form").addEventListener("submit", handleGenerate);
  $("#file-input").addEventListener("change", (event) => {
    state.files = Array.from(event.target.files || []);
    renderAttachments();
  });
  $("#chat-input").addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      $("#chat-form").requestSubmit();
    }
  });
  $("#provider-select").addEventListener("change", syncProviderUI);
  $("#piece-search").addEventListener("input", renderPieces);
  $("#refresh-pieces").addEventListener("click", syncReports);
  $$("[data-theme-choice]").forEach((button) => {
    button.addEventListener("click", () => applyTheme(button.dataset.themeChoice));
  });
  $("#api-token").addEventListener("input", () => {
    localStorage.setItem(TOKEN_KEY, JSON.stringify({ value: $("#api-token").value.trim(), savedAt: Date.now() }));
  });
  $("#prefer-local").addEventListener("change", (event) => {
    state.settings.preferLocal = event.target.checked;
    saveSettings();
  });
  $("#remember-settings").addEventListener("change", (event) => {
    state.settings.remember = event.target.checked;
    saveSettings();
  });
  $("#strict-review").addEventListener("change", (event) => {
    state.settings.strictReview = event.target.checked;
    saveSettings();
  });
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
    if (state.settings.theme === "system") applyTheme("system");
  });
}

async function registerServiceWorker() {
  if (!("serviceWorker" in navigator)) return;
  try {
    const registrations = await navigator.serviceWorker.getRegistrations();
    await Promise.all(registrations.map((registration) => registration.unregister()));
  } catch (error) {
    console.warn("Service worker não removido.", error);
  }
}

function initSettings() {
  $("#api-token").value = loadStoredToken();
  $("#prefer-local").checked = state.settings.preferLocal;
  $("#remember-settings").checked = state.settings.remember;
  $("#strict-review").checked = state.settings.strictReview;
  applyTheme(state.settings.theme);
}

bindEvents();
initSettings();
addWelcomeMessage();
const initialTab = new URLSearchParams(location.search).get("tab") || location.hash.slice(1);
switchTab(["dashboard", "ai", "pieces", "settings"].includes(initialTab) ? initialTab : "dashboard");
await loadApiState();
await registerServiceWorker();

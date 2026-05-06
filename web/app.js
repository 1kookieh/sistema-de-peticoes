const API_BASE = "/api/v1";
const STORAGE_KEY = "lexdoc.pieces.v2";
const SETTINGS_KEY = "lexdoc.settings.v2";
const TOKEN_KEY = "sistemaPeticoesApiToken";
const TOKEN_TTL_MS = 12 * 60 * 60 * 1000;

const DEFAULT_PROVIDER = "groq";
const externalProviders = new Set([DEFAULT_PROVIDER]);
const providerLabels = {
  groq: "Groq",
};

const providerBrand = {
  groq: {
    className: "provider-brand-groq",
    svg: '<svg viewBox="0 0 24 24"><path d="M6 7.5A4.5 4.5 0 0 1 10.5 3h3A4.5 4.5 0 0 1 18 7.5v9A4.5 4.5 0 0 1 13.5 21h-3A4.5 4.5 0 0 1 6 16.5v-9Z"/><path d="M10.5 8.5h3A3.5 3.5 0 0 1 17 12v0a3.5 3.5 0 0 1-3.5 3.5h-3"/><path d="M10.5 8.5v7"/></svg>',
  },
};

const state = {
  tab: "dashboard",
  limits: {
    llm_default_provider: DEFAULT_PROVIDER,
    llm_default_model: "llama-3.3-70b-versatile",
    llm_allowed_providers: [DEFAULT_PROVIDER],
    llm_allow_client_provider: false,
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
      remember: true,
      ...JSON.parse(localStorage.getItem(SETTINGS_KEY) || "{}"),
    };
  } catch {
    return { theme: "light", remember: true };
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
  $("#page-title").textContent = titles[tab] || "Sistema de Petições";
  if (location.hash !== `#${tab}`) history.replaceState(null, "", `#${tab}`);
  if (tab === "pieces") renderPieces();
  if (tab === "dashboard") renderDashboard();
}

function statusChip(status) {
  const normalized = status === "Finalizado" ? "done" : status === "Falha" ? "failed" : "progress";
  return `<span class="status-chip ${normalized}">${escapeHTML(status)}</span>`;
}

function mutedDash() {
  return '<span class="muted-dash" aria-label="Não informado">--</span>';
}

function displayValue(value, fallback = mutedDash()) {
  const text = String(value || "").trim();
  if (!text || /^(n[aã]o informado|cidade\/uf n[aã]o informada|sem dado)$/i.test(text)) {
    return fallback;
  }
  return escapeHTML(text);
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
  // Conversa inicia em branco; sem mensagem automática da IA.
}

function renderSelectOptions() {
  syncProviderUI();
}

function syncProviderUI() {
  const provider = DEFAULT_PROVIDER;
  const providerIconButton = $("#provider-icon");
  if (providerIconButton) {
    const brand = providerBrand[provider];
    providerIconButton.className = `provider-brand ${brand?.className || "provider-brand-generic"}`;
    providerIconButton.innerHTML = brand?.svg || "IA";
    const label = providerLabels[provider] || provider || "IA";
    providerIconButton.setAttribute("title", label);
  }
  $("#external-consent-row").hidden = false;
  $("#provider-note").textContent = "Groq é a IA padrão: confirme autorização antes de enviar dados do caso para fora desta máquina.";
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
    provider: DEFAULT_PROVIDER,
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
    provider: item.provider || DEFAULT_PROVIDER,
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
  const provider = DEFAULT_PROVIDER;
  if (!$("#external-consent").checked) {
    addMessage("assistant", `<p>Confirme o consentimento antes de enviar dados do caso ao Groq.</p>`);
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
    addMessage("assistant", `<p><strong>Não consegui gerar agora.</strong> ${escapeHTML(friendlyChatError(error))}</p>`);
    setGenerationState("Falha", "failed");
  } finally {
    $("#send-button").disabled = false;
  }
}

function friendlyChatError(error) {
  const raw = String(error?.message || "").trim();
  if (!raw) return "Tente novamente em alguns instantes.";
  if (/413|too large|tokens per minute|tpm/i.test(raw)) {
    return "Sua mensagem ficou grande demais para o limite gratuito do Groq. Reduza o texto ou aguarde alguns instantes.";
  }
  if (/401|unauthorized|invalid api key/i.test(raw)) {
    return "A chave do Groq foi rejeitada. Confira GROQ_API_KEY no .env.";
  }
  if (/429|rate limit/i.test(raw)) {
    return "Limite de requisições do Groq atingido temporariamente. Aguarde alguns segundos e tente de novo.";
  }
  if (/403|cloudflare|1010/i.test(raw)) {
    return "O Groq bloqueou esta requisição. Verifique chave, rede ou tente novamente.";
  }
  if (/consent|consentimento/i.test(raw)) {
    return "Marque o consentimento de envio ao Groq antes de enviar.";
  }
  // default: keep first sentence only, drop URLs/IDs
  const firstLine = raw.split(/[.\n]/)[0].slice(0, 160);
  return firstLine + (raw.length > firstLine.length ? "..." : "");
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
    assunto: "Criação pelo chat Sistema de Petições",
    llm: {
      consent_external_provider: $("#external-consent").checked,
    },
  });
}

async function generateWithUpload(request) {
  const body = new FormData();
  for (const file of state.files) body.append("files", file);
  body.append("llm_consent_external_provider", String($("#external-consent").checked));
  body.append("remetente", "frontend.local@example.com");
  body.append("assunto", "Criação por upload no chat Sistema de Petições");
  return postForm("/documents/upload", body);
}

async function chatWithText(request) {
  return postJson("/chat", {
    text: request.text,
    consent_external_provider: $("#external-consent").checked,
  });
}

async function chatWithUpload(request) {
  const body = new FormData();
  for (const file of state.files) body.append("files", file);
  body.append("text", request.text || "");
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
    <p><strong>Revisão obrigatória:</strong> esta é uma minuta e deve ser conferida por advogado responsável antes de qualquer uso profissional.</p>
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
  $("#metric-provider").textContent = providerLabels[DEFAULT_PROVIDER];
  $("#metric-model").textContent = state.limits.llm_default_model || "Modelo definido pelo backend";
  $("#side-provider").textContent = `${providerLabels[DEFAULT_PROVIDER]} ativo`;
  $("#settings-provider").textContent = providerLabels[DEFAULT_PROVIDER];
  $("#settings-model").textContent = state.limits.llm_default_model || "--";
  $("#settings-allowed").textContent = state.limits.llm_allow_client_provider ? "Ativada" : "Desativada";

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
  const yTicks = integerTicks(axisMax);
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
            <stop offset="0%" stop-color="currentColor" stop-opacity=".22"></stop>
            <stop offset="100%" stop-color="currentColor" stop-opacity="0"></stop>
          </linearGradient>
        </defs>
        <g class="chart-grid dark-grid">
          ${yTicks.map((tick) => {
            const y = pad.top + usableH - (tick / axisMax) * usableH;
            return `<path d="M${pad.left} ${y}H${width - pad.right}"></path>`;
          }).join("")}
        </g>
        <path class="monthly-area" d="${smoothArea}"></path>
        <path class="monthly-line secondary" d="${smoothPath}"></path>
        <path class="monthly-line primary" d="${smoothPath}"></path>
        ${points.map((point, index) => `
          <g class="chart-hit monthly-hit" tabindex="0" role="listitem" aria-label="${escapeHTML(point.item.label)}: ${Number(point.item.total || 0)} peças">
            <title>${escapeHTML(point.item.label)}: ${Number(point.item.total || 0)} peças geradas</title>
            <rect x="${point.x - 22}" y="${pad.top}" width="44" height="${usableH}" rx="6" fill="transparent" stroke="none"></rect>
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
  const rowHeight = 88;
  const height = 116 + normalized.length * rowHeight;
  const pad = { top: 34, right: 34, bottom: 54, left: 38 };
  const usableW = width - pad.left - pad.right;
  const xTicks = integerTicks(maxValue);
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
        const y = pad.top + index * rowHeight + 32;
        const barWidth = Math.max(8, (total / maxValue) * usableW);
        return `
          <text class="chart-axis y label" x="${pad.left}" y="${y - 10}" text-anchor="start">${escapeHTML(shortLabel(item.label, 34))}</text>
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
  const onlyMissingLocation = normalized.every((item) => /n[aã]o informad|sem cidade|sem dado/i.test(String(item.label || "")));
  if (onlyMissingLocation) {
    container.innerHTML = `
      <div class="chart-empty chart-empty-guidance dark">
        ${icon("i-map")}
        <span>Cidade/UF não informada nas peças. Preencha o campo comarca ao gerar nova peça para popular este gráfico.</span>
      </div>
    `;
    return;
  }
  const maxValue = Math.max(...normalized.map((item) => Number(item.total || 0)), 1);
  const axisMax = maxValue <= 2 ? 2 : Math.ceil(maxValue / 2) * 2;
  const yTicks = integerTicks(axisMax);
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
  return String(Math.round(Number(value || 0)));
}

function integerTicks(maxValue) {
  const max = Math.max(1, Math.ceil(Number(maxValue || 1)));
  if (max <= 4) return Array.from({ length: max + 1 }, (_, index) => index);
  const step = Math.max(1, Math.ceil(max / 4));
  const ticks = [];
  for (let value = 0; value < max; value += step) ticks.push(value);
  if (ticks.at(-1) !== max) ticks.push(max);
  return ticks;
}

function shortLabel(value, max = 18) {
  const text = String(value || "--");
  return text.length > max ? `${text.slice(0, max - 3)}...` : text;
}

function shortLocationLabel(value) {
  const text = String(value || "--").trim();
  if (!text || text === "--") return "Sem dado";
  if (/n[aã]o informad[ao]/i.test(text)) return "Sem cidade";
  const match = text.match(/([A-Z]{2})$/i);
  if (match) return match[1].toUpperCase();
  return shortLabel(text, 14);
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
        <td><strong>${displayValue(piece.person)}</strong><br><small>${new Date(piece.createdAt).toLocaleString("pt-BR")}</small></td>
        <td>${displayValue(piece.process)}</td>
        <td>${displayValue(piece.type, escapeHTML("Peça processual"))}</td>
        <td>${statusChip(piece.status)}</td>
        <td>${displayValue(providerLabels[piece.provider] || piece.provider)}</td>
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
  $("#piece-search").addEventListener("input", renderPieces);
  $("#refresh-pieces").addEventListener("click", syncReports);
  $$("[data-theme-choice]").forEach((button) => {
    button.addEventListener("click", () => applyTheme(button.dataset.themeChoice));
  });
  $("#api-token").addEventListener("input", () => {
    localStorage.setItem(TOKEN_KEY, JSON.stringify({ value: $("#api-token").value.trim(), savedAt: Date.now() }));
  });
  $("#remember-settings").addEventListener("change", (event) => {
    state.settings.remember = event.target.checked;
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
  $("#remember-settings").checked = state.settings.remember;
  applyTheme(state.settings.theme);
}

bindEvents();
initSettings();
addWelcomeMessage();
const initialTab = new URLSearchParams(location.search).get("tab") || location.hash.slice(1);
switchTab(["dashboard", "ai", "pieces", "settings"].includes(initialTab) ? initialTab : "dashboard");
await loadApiState();
await registerServiceWorker();

import { AUTO_VALUE, state } from "./state/store.js";

export function escapeHTML(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

export function setMessage(target, message, kind = "muted") {
  target.innerHTML = `<p class="${kind}">${escapeHTML(message)}</p>`;
}

export function renderLoading(container, label = "Gerando documento") {
  container.classList.remove("has-problems");
  container.innerHTML = `
    <div class="loading-card" role="status">
      <strong>${escapeHTML(label)}</strong>
      <div class="progress-bar" aria-hidden="true"><span></span></div>
      <ol class="progress-steps">
        <li class="done">Arquivo recebido</li>
        <li class="done">Texto extraído</li>
        <li class="active">Detectando tipo de peça</li>
        <li>Gerando DOCX</li>
        <li>Validando riscos formais</li>
      </ol>
    </div>
  `;
}

export function renderPieceTypes(select) {
  const grouped = new Map();
  for (const item of state.pieceTypes) {
    if (!grouped.has(item.grupo)) grouped.set(item.grupo, []);
    grouped.get(item.grupo).push(item);
  }

  select.innerHTML = "";
  const autoOption = document.createElement("option");
  autoOption.value = AUTO_VALUE;
  autoOption.selected = true;
  autoOption.textContent = "Detectar automaticamente pelo texto";
  select.appendChild(autoOption);

  for (const [group, groupItems] of grouped) {
    const optgroup = document.createElement("optgroup");
    optgroup.label = group;
    for (const item of groupItems) {
      const option = document.createElement("option");
      option.value = item.id;
      option.textContent = item.nome;
      optgroup.appendChild(option);
    }
    select.appendChild(optgroup);
  }
}

export function renderProfiles(select) {
  select.innerHTML = "";
  const autoOption = document.createElement("option");
  autoOption.value = AUTO_VALUE;
  autoOption.selected = true;
  autoOption.textContent = "Detectar automaticamente (padrão: Inicial JEF/Federal)";
  select.appendChild(autoOption);

  for (const item of state.profiles) {
    const option = document.createElement("option");
    option.value = item.id;
    const isDefault = item.id === state.defaultProfileId ? " - padrão" : "";
    option.textContent = `${item.label}${isDefault}`;
    option.title = item.descricao;
    select.appendChild(option);
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
    .map((flag) => `<span class="badge badge-${flag.kind}">${escapeHTML(flag.label)}</span>`)
    .join("")}</div>`;
}

export function renderProfileDetails(container, selectedId) {
  if (!selectedId || selectedId === AUTO_VALUE) {
    container.innerHTML = `
      <strong>Detecção automática</strong>
      <span>auto</span>
      <p>O sistema escolhe o perfil pela peça detectada. Sem reconhecimento, usa <strong>Inicial JEF/Federal</strong>.</p>
    `;
    return;
  }

  const selected = state.profiles.find((item) => item.id === selectedId);
  if (!selected) {
    container.textContent = "Selecione um perfil para ver a regra formal aplicada.";
    return;
  }

  const sections = (selected.required_sections || []).length
    ? `<p class="muted">Seções mínimas: ${selected.required_sections.map(escapeHTML).join(" · ")}</p>`
    : "";
  container.innerHTML = `
    <strong>${escapeHTML(selected.label)}</strong>
    <span>${escapeHTML(selected.id)}</span>
    <p>${escapeHTML(selected.descricao)}</p>
    ${renderProfileBadges(selected)}
    ${sections}
  `;
}

export function renderPieceHint(container, selectedId) {
  if (!selectedId || selectedId === AUTO_VALUE) {
    container.innerHTML = `
      <strong>Detecção automática</strong>
      <p>Cole o texto e o sistema identifica a peça por título e palavras-chave.</p>
    `;
    return;
  }

  const selected = state.pieceTypes.find((item) => item.id === selectedId);
  if (!selected) {
    container.textContent = "Peça não encontrada.";
    return;
  }
  container.innerHTML = `
    <strong>${escapeHTML(selected.grupo)}</strong>
    <p>${escapeHTML(selected.exige_revisao)}</p>
  `;
}

export function renderHistory(container, reports, options = {}) {
  if (!reports.length) {
    container.innerHTML = "<p class='muted' style='margin-top:10px'>Nenhum relatório local encontrado ainda.</p>";
    return;
  }

  const query = (options.query || "").toLowerCase().trim();
  const filter = options.filter || "all";
  const filtered = reports.filter((item) => {
    const validos = Number(item.summary?.validos ?? 0);
    const bloqueados = Number(item.summary?.bloqueados ?? 0);
    const falhas = Number(item.summary?.falhas ?? 0);
    const matchesFilter =
      filter === "all" ||
      (filter === "valid" && validos > 0 && !bloqueados && !falhas) ||
      (filter === "blocked" && bloqueados > 0) ||
      (filter === "failed" && falhas > 0);
    const haystack = `${item.profile || ""} ${item.name || ""} ${item.first_docx || ""}`.toLowerCase();
    return matchesFilter && (!query || haystack.includes(query));
  }).slice(0, 3);

  if (!filtered.length) {
    container.innerHTML = "<p class='muted' style='margin-top:10px'>Nenhum item encontrado com esse filtro.</p>";
    return;
  }

  container.innerHTML = filtered.map((item) => {
    const validos = Number(item.summary?.validos ?? 0);
    const bloqueados = Number(item.summary?.bloqueados ?? 0);
    const falhas = Number(item.summary?.falhas ?? 0);
    let statusBadge = '<span class="badge badge-ok">válido</span>';
    if (bloqueados) statusBadge = '<span class="badge badge-warn">bloqueado</span>';
    if (falhas) statusBadge = '<span class="badge badge-danger">falha</span>';
    return `
    <article class="history-item">
      <div class="history-main">
        <strong>${escapeHTML(item.profile || item.name)}</strong>
        ${statusBadge}
      </div>
      <p class="muted small">${escapeHTML(item.generated_at || "sem data")} · Válidos: ${validos} · Bloqueados: ${bloqueados} · Falhas: ${falhas}</p>
      <div class="link-row">
        ${item.first_docx ? `<button class="link-button primary-link" aria-label="Baixar DOCX" data-download="/api/v1/documents/${encodeURIComponent(item.first_docx)}/download">DOCX</button>` : ""}
        <button class="link-button" aria-label="Abrir relatório HTML" data-open="/api/v1/reports/${encodeURIComponent(item.html_name)}">HTML</button>
        <button class="link-button" aria-label="Abrir relatório JSON" data-open="/api/v1/reports/${encodeURIComponent(item.name)}">JSON</button>
      </div>
    </article>`;
  }).join("");
}

export function renderResult(container, payload) {
  const hasProblems = Boolean(payload.problems?.length);
  const inferredTag = '<span class="badge badge-ok">detectado</span>';
  const statusKind = hasProblems ? "warn" : (payload.status === "ok_no_outbox" ? "ok" : "neutral");
  const statusLabel = hasProblems ? "Concluído com alertas" : "Geração concluída com sucesso";
  const statusBadge = `<span class="badge badge-${statusKind}">${escapeHTML(payload.status)}</span>`;

  const pieceLine = payload.piece_type
    ? `<p class="muted"><strong>Tipo detectado:</strong> ${escapeHTML(payload.piece_type.nome)} ${payload.piece_type_inferred ? inferredTag : ""}</p>`
    : `<p class="muted"><strong>Tipo:</strong> <em>não identificado</em> — validação aplicada pelo perfil.</p>`;
  const profileLine = payload.profile
    ? `<p class="muted"><strong>Perfil:</strong> ${escapeHTML(payload.profile.label || payload.profile.id)} ${payload.profile_inferred ? inferredTag : ""}</p>`
    : "";
  const sourceLine = payload.source_filename
    ? `<p class="muted"><strong>Fonte:</strong> ${escapeHTML(payload.source_filename)}</p>`
    : "";

  const alerts = hasProblems
    ? payload.problems.map((problem) => `<li>⚠ ${escapeHTML(problem)}</li>`).join("")
    : [
        "Conferir DER, NB e documentos anexos conforme o caso.",
        "Confirmar competência, valor da causa, OAB e procuração.",
        "Revisar mérito jurídico antes de qualquer protocolo.",
      ].map((problem) => `<li>○ ${escapeHTML(problem)}</li>`).join("");
  const problems = hasProblems
    ? `<div class="warning"><strong>Documento bloqueado ou com alertas:</strong><ul class="alert-list">${alerts}</ul></div>`
    : `<div class="legal-alerts"><strong>Alertas de revisão humana</strong><ul class="alert-list">${alerts}</ul></div>`;

  container.classList.toggle("has-problems", hasProblems);
  container.innerHTML = `
    <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
      <h3>${escapeHTML(statusLabel)}</h3>
      ${statusBadge}
    </div>
    ${pieceLine}
    ${profileLine}
    ${sourceLine}
    ${problems}
    <div class="link-row">
      ${payload.download_url ? `<button class="link-button primary-link" aria-label="Baixar documento DOCX" data-download="${escapeHTML(payload.download_url)}">⬇ Baixar DOCX</button>` : ""}
      <button class="link-button" aria-label="Abrir relatório HTML" data-open="${escapeHTML(payload.report_html_url)}">Relatório HTML</button>
      <button class="link-button" aria-label="Abrir relatório JSON" data-open="${escapeHTML(payload.report_json_url)}">JSON</button>
    </div>
  `;
}

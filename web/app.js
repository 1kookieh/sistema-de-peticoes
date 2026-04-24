const profile = document.querySelector("#profile");
const text = document.querySelector("#text");
const file = document.querySelector("#file");
const generate = document.querySelector("#generate");
const result = document.querySelector("#result");
const history = document.querySelector("#history");
const refresh = document.querySelector("#refresh");

function escapeHTML(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function loadProfiles() {
  const response = await fetch("/api/profiles");
  const profiles = await response.json();
  profile.innerHTML = profiles
    .map((item) => `<option value="${escapeHTML(item.id)}">${escapeHTML(item.id)} — ${escapeHTML(item.descricao)}</option>`)
    .join("");
}

async function loadHistory() {
  const response = await fetch("/api/reports");
  const payload = await response.json();
  const reports = payload.reports || [];
  history.innerHTML = reports.length
    ? reports.map((item) => `
      <div class="history-item">
        <strong>${escapeHTML(item.name)}</strong>
        <p class="muted">${escapeHTML(item.generated_at || "sem data")} · perfil ${escapeHTML(item.profile || "-")}</p>
        <p>Válidos: ${escapeHTML(item.summary?.validos ?? 0)} · Bloqueados: ${escapeHTML(item.summary?.bloqueados ?? 0)} · Falhas: ${escapeHTML(item.summary?.falhas ?? 0)}</p>
        <a href="/api/reports/${encodeURIComponent(item.name)}" target="_blank">JSON</a>
        · <a href="/api/reports/${encodeURIComponent(item.html_name)}" target="_blank">HTML</a>
        ${item.first_docx ? `· <a href="/api/documents/${encodeURIComponent(item.first_docx)}/download">DOCX</a>` : ""}
      </div>
    `).join("")
    : "<p class='muted'>Nenhum relatório local encontrado.</p>";
}

file.addEventListener("change", async () => {
  const selected = file.files?.[0];
  if (!selected) return;
  text.value = await selected.text();
});

generate.addEventListener("click", async () => {
  result.innerHTML = "<p>Gerando documento...</p>";
  const response = await fetch("/api/documents", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text: text.value,
      profile_id: profile.value,
      remetente: "frontend.local@example.com",
      assunto: "Geração pelo painel local"
    })
  });
  const payload = await response.json();
  if (!response.ok) {
    result.innerHTML = `<p class="warning">Erro: ${escapeHTML(payload.detail || "falha ao gerar")}</p>`;
    return;
  }
  const problems = payload.problems?.length
    ? `<p><strong>Problemas:</strong> ${escapeHTML(payload.problems.join("; "))}</p>`
    : "<p><strong>Validação formal:</strong> sem violações detectadas.</p>";
  result.innerHTML = `
    <h3>Resultado: ${escapeHTML(payload.status)}</h3>
    ${problems}
    ${payload.download_url ? `<a href="${escapeHTML(payload.download_url)}">Baixar DOCX</a> · ` : ""}
    <a href="${escapeHTML(payload.report_json_url)}" target="_blank">Relatório JSON</a> ·
    <a href="${escapeHTML(payload.report_html_url)}" target="_blank">Relatório HTML</a>
  `;
  await loadHistory();
});

refresh.addEventListener("click", loadHistory);

loadProfiles();
loadHistory();

# Project Snapshot
- Sistema de Petições: AI-first pipeline that drafts, validates and renders Brazilian legal petitions as `.docx`.
- Goal: structured-JSON LLM output -> validated DOCX via python-docx, with audit reports.
- Users: lawyers/paralegals; every output requires human attorney review before filing.
- Constraints: `LLM_REQUIRED=true`; providers from backend allowlist (`mock`, `ollama`, `openai`, `anthropic`); external providers need explicit per-request consent; partial PII redaction (CPF/CNPJ/NIT/NB/RG/CEP/phone/email) — not full anonymization.

# Stack & Commands
- Python 3 + FastAPI/Uvicorn, python-docx, pytest, ruff, mypy (gradual), bandit, pip-audit.
- Setup: `python -m venv .venv` then `.\.venv\Scripts\Activate.ps1` then `pip install -r requirements.txt` then `python -m src --setup`.
- Run API: `uvicorn src.interfaces.api:app --host 127.0.0.1 --port 8000 --reload` (serves `http://127.0.0.1:8000`).
- Compile: `python -m compileall config.py src tests`.
- Tests: `pytest -q`. Lint: `ruff check .`. Types (scoped): `mypy config.py src/infra/llm`.
- Security: `pip-audit -r requirements.txt --strict` and `bandit -q -r src`.
- Pipeline demo: `python -m src --inbox examples/inbox_valid.json --profile judicial-inicial-jef --strict --no-outbox --report reports/demo_report.json`.

# Structure Rules
- `src/core/` domain, piece types, profiles, prompts, validations.
- `src/adapters/` inbox/outbox + file extraction.
- `src/infra/` DOCX, LLM, locks, logging, local state.
- `src/interfaces/` API, CLI, desktop.
- `src/orchestration/` pipeline, reports, retention, setup.
- Versioned prompts live in `prompts/` (`prompt_peticao.md`, `prompt_formatacao_word.md`) — single source for LLM guidance.
- Fixtures only in `examples/` and `tests/`. No business logic in `interfaces/` beyond glue.

# Agent Workflow
- Think Before Coding: read README/CLAUDE.md and target file; check `git status`; state assumptions; surface ambiguity before editing.
- Simplicity First: smallest change that satisfies the request; no speculative abstractions, flags or configurability.
- Surgical Changes: touch only required files; match existing style; no drive-by refactor or formatting churn; remove only dead code your change creates.
- Goal-Driven Execution: define success criteria; reproduce bugs with a focused test when practical; run validation or report why it was skipped.

# Testing & Validation
- After code changes run `python -m compileall config.py src tests` then `pytest -q`.
- Touching prompts/LLM/DOCX: add or update fixtures and unit tests in `tests/`.
- UI changes: open `http://127.0.0.1:8000` and verify console + basic flow.
- Default `LLM_PROVIDER=mock` for tests/dev. Never call external providers with real client data.

# Security Rules
- NEVER commit `.env`, `output/*.docx`, `reports/*.json|*.html`, `mcp_inbox.json`, `mcp_outbox.json`, `mcp_status.json`, or real client documents.
- NEVER log full prompts, petition bodies or PII; reports store prompt SHA-256, not prompt text.
- NEVER call external LLM providers without `consent_external_provider=true` (request/upload/CLI flag).
- NEVER weaken `API_REQUIRE_TOKEN`; in Docker set `API_TOKEN` and require `X-API-Token` for sensitive routes.
- NEVER claim full anonymization — redaction is pattern-based and partial.
- Keep `/api/v1` as the API contract.

# Sensitive Areas
- `prompts/prompt_peticao.md`, `prompts/prompt_formatacao_word.md` (changes shift LLM behavior; audit hashes in reports).
- `src/infra/llm/` (provider allowlist, redaction, consent gating).
- `src/infra/` DOCX renderer (formatting contract).
- `config.py`, `Dockerfile`, API token handling.
- `requirements.txt` (pip-audit gate).
- Inbox/outbox/state files at repo root [INFERENCE — CONFIRM paths in code].

# Known Pitfalls
- DO NOT invent facts, OAB, NB, dates, monetary values or jurisprudence — mark gaps as `[REVISAR]`.
- DO NOT state a petition is ready to file; human attorney review is mandatory.
- Prefer plain text output for DOCX targets; avoid heavy Markdown in generated content.
- `mypy` is gradual — only `config.py` and `src/infra/llm` are CI-enforced.

# Final Checklist
- [ ] No invented data or jurisprudence.
- [ ] Human review preserved as mandatory.
- [ ] No secrets, sensitive files or real client data added.
- [ ] `/api/v1` contract intact; versioned prompts respected.
- [ ] `compileall` + `pytest -q` ran (or limitation reported).
- [ ] Docs updated only if behavior changed.
- [ ] Assumptions and `[INFERENCE — CONFIRM]` items called out.

# Sistema de Petições — Codex Instructions

# Project Snapshot
- Local-first system that generates, validates, reviews, and renders Brazilian legal petition drafts as `.docx`.
- AI-first pipeline: `LLM_REQUIRED=true`; backend uses Groq (`llama-3.3-70b-versatile`) as the sole external provider, with `mock` reserved for tests.
- Main flow: user input/files -> structured LLM JSON -> validation -> DOCX rendering -> JSON/HTML report.
- Output is always a draft for a responsible lawyer; never claim it is ready to file, submit, or protocol.
- Sensitive personal/legal data flows through input files, prompts, reports, generated DOCX, logs, and local state.

# Stack & Commands
- Python 3 + FastAPI + python-docx + Jinja2 + Pydantic Settings.
- Static web client in `web/` using vanilla JavaScript, CSS, and service worker.
- Install: `pip install -r requirements.txt`.
- Setup: `python -m src --setup`.
- Run API/web: `uvicorn src.interfaces.api:app --host 127.0.0.1 --port 8000 --reload`.
- CLI help: `python -m src --help`.
- Compile check: `python -m compileall config.py src tests`.
- Tests: `pytest -q`.
- Lint: `ruff check .`.
- Types: `mypy config.py src/infra/llm`.
- Audit: `pip-audit -r requirements.txt --strict` and `bandit -q -r src`.
- CLI smoke: `python -m src --inbox examples/inbox_valid.json --profile judicial-inicial-jef --strict --no-outbox --report reports/demo_report.json`.

# Repository Map
- `src/core/`: domain rules, piece types, profiles, prompt loading, and validations.
- `src/adapters/`: inbox/outbox handling and file extraction.
- `src/infra/`: DOCX generation, LLM clients, locks, logging, and local state.
- `src/interfaces/`: FastAPI API, CLI, and desktop entry points.
- `src/orchestration/`: pipeline, reports, retention, history, and setup.
- `prompts/`: versioned prompt contracts; load via pipeline, never duplicate inline.
- `web/`: static frontend only; do not place business logic there.
- `tests/`: mirrors `src/`; fixtures must be fictitious.
- `output/`, `reports/`, and local MCP files are runtime artifacts, not source code.

# Architecture Rules
- Keep `/api/v1` as the stable API contract.
- Never render DOCX directly from raw LLM prose; validate structured JSON before rendering.
- Treat `prompts/prompt_peticao.md` and `prompts/prompt_formatacao_word.md` as source-of-truth contracts.
- Preserve prompt usage auditing: prompt name, path, hash, provider/model metadata, and relevant flags.
- Preserve `LLM_REQUIRED=true`; do not bypass AI-required paths unless explicitly scoped for tests.
- External providers require explicit per-request consent; missing consent must return `llm_error`, not call or silently fallback.
- Redaction is partial masking only; never describe it as full anonymization.
- Processing should be idempotent where practical: repeated runs must not silently overwrite, duplicate, or lose outputs/reports/state.
- Keep legal-safety disclaimers visible in user-facing flows: AI drafts require responsible lawyer review.

# UI & Design Rules
- Before creating or changing UI, CSS, components, icons, charts, or visual states, read `DESIGN.md`.
- Preserve the existing legal workspace identity: paper/ink/gold, Portuguese UI, local-first review workflow.
- Do not introduce Tailwind, frontend build tooling, or a component library unless explicitly requested.
- Keep business rules out of `web/`; frontend should call API contracts and render states clearly.
- If changing static assets, CSS, or UI behavior, check `web/sw.js` cache/version behavior.
- External provider consent, redaction warnings, LLM errors, generated reports, downloads, and human-review states must be visible and textual.

# Agent Workflow
- Think before coding: read `README.md`, this file, `git status`, and affected files before editing.
- State assumptions for non-trivial changes; surface risks around LLM, validation, API, security, DOCX, retention, or UI safety.
- Simplicity first: implement the smallest safe change; no speculative providers, abstractions, dashboards, or configurability.
- Surgical changes: touch only required files; no unrelated refactors, formatting churn, or drive-by cleanup.
- Goal-driven execution: convert tasks into verifiable criteria; reproduce bugs with a test when practical.
- Match existing style and Portuguese user-facing text unless the touched file already uses English.

# Testing & Validation
- Add/update tests for validators, parsers, profiles, prompt loading, LLM providers, API contracts, extraction, retention, and DOCX rendering.
- After code changes, run `python -m compileall config.py src tests` and `pytest -q`.
- Run `ruff check .`, `mypy config.py src/infra/llm`, `bandit -q -r src`, and `pip-audit -r requirements.txt --strict` when touching quality, typing, LLM, API, dependencies, or security.
- Use `LLM_PROVIDER=mock` for automated tests unless explicitly validating a real provider.
- For UI changes, open `http://127.0.0.1:8000`, verify the affected flow, and check the browser console.
- If validation cannot run, report the exact skipped command and reason.

# Security & Privacy
- NEVER commit `.env`, secrets, provider keys, OAuth tokens, real client documents, private legal facts, or generated sensitive artifacts.
- NEVER version `output/*.docx`, `reports/*.json`, `reports/*.html`, `mcp_inbox.json`, `mcp_outbox.json`, or `mcp_status.json`.
- NEVER send real client data to external providers without explicit consent.
- NEVER weaken auth, validation, provider allowlist, consent checks, or the `API_REQUIRE_TOKEN=1` Docker contract.
- Honor `X-API-Token` on sensitive routes.
- Store secrets only in environment variables or local ignored config.
- Use only fictitious fixtures in `examples/` and `tests/`.
- Do not log full prompt bodies, raw legal facts, full document text, provider tokens, or sensitive fields by default.

# Sensitive Areas
- `src/infra/llm/`: provider selection, structured output, redaction, consent gating, prompt hashes.
- `prompts/prompt_peticao.md` and `prompts/prompt_formatacao_word.md`: versioned prompt contracts.
- `src/interfaces/api.py`: token enforcement, uploads, `/api/v1`, and sensitive routes.
- DOCX rendering code: formatting, validation, generated file safety, and output paths.
- `src/orchestration/`: pipeline, reports, history, retention, and local state.
- `web/`, `DESIGN.md`, and `web/sw.js`: UI states, static cache, and user-facing legal warnings.
- `Dockerfile`: `API_REQUIRE_TOKEN=1` and runtime security defaults.
- `.gitignore`: must keep local artifacts and sensitive files ignored.

# Known Pitfalls
- External provider calls without explicit consent are security bugs.
- Missing external consent must fail closed with `llm_error`, not fallback silently.
- `mypy` is gradual; current enforced scope is `config.py` and `src/infra/llm`.
- Service worker cache can hide frontend changes if versioning is not updated.
- `/api/v1` is stable; do not break it without explicit scope.
- Redaction masks known identifiers but may leave names, context, and legal facts.
- The system validates form, structure, and obvious risks; it does not decide jurisdiction, deadlines, legal thesis, evidence sufficiency, calculations, strategy, or filing viability.
- Human legal review must remain explicit in user-facing behavior.

# Final Checklist
- Scope respected; no unrelated refactor or formatting churn.
- `/api/v1`, prompt contracts, structured JSON validation, and DOCX rendering flow preserved.
- No secrets, real client data, private legal facts, generated DOCX, or reports committed.
- External provider consent, allowlist, redaction behavior, and review warnings preserved.
- `compileall` and `pytest -q` run, or skip reason stated.
- Extra checks run when relevant, or limitation reported.
- UI changes checked against `DESIGN.md` and service worker cache behavior.
- Documentation updated if behavior, commands, API, prompts, UI, or security changed.
- Assumptions and uncertainties documented.
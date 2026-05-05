# Sistema de Petições — Claude Code Instructions

# Project Snapshot
- Local-first system that generates, validates, and renders Brazilian legal petition drafts as `.docx`.
- AI-first pipeline: `LLM_REQUIRED=true`; providers come from backend allowlist: `mock`, `ollama`, `openai`, `anthropic`.
- Main flow: user input/files -> structured LLM JSON -> validation -> DOCX rendering -> JSON/HTML report.
- Output is always a draft for a responsible lawyer; never claim it is ready to file or protocol.
- Sensitive personal/legal data flows through the pipeline; treat all inputs, outputs, reports, and logs as confidential.

# Stack & Commands
- Python 3 + FastAPI + python-docx + Jinja2 + Pydantic Settings.
- Static web client in `web/` using vanilla JS and service worker.
- Install: `pip install -r requirements.txt`.
- Setup: `python -m src --setup`.
- Run API/web: `uvicorn src.interfaces.api:app --host 127.0.0.1 --port 8000 --reload`.
- Compile check: `python -m compileall config.py src tests`.
- Tests: `pytest -q`.
- Lint: `ruff check .`.
- Types: `mypy config.py src/infra/llm`.
- Audit: `pip-audit -r requirements.txt --strict` and `bandit -q -r src`.
- CLI smoke: `python -m src --inbox examples/inbox_valid.json --profile judicial-inicial-jef --strict --no-outbox --report reports/demo_report.json`.

# Structure Rules
- `src/core/`: domain rules, piece types, profiles, prompt loading, and validations.
- `src/adapters/`: inbox/outbox handling and file extraction.
- `src/infra/`: DOCX generation, LLM clients, locks, logging, and local state.
- `src/interfaces/`: FastAPI API, CLI, and desktop entry points.
- `src/orchestration/`: pipeline, reports, retention, history, and setup.
- `prompts/`: versioned prompt contracts; load via pipeline, never duplicate inline.
- `tests/`: mirrors `src/`; fixtures must be fictitious.
- `web/`: static frontend only; do not place business logic there.
- Runtime artifacts belong in `output/`, `reports/`, and local MCP files; do not treat them as source code.

# Architecture Rules
- Keep `/api/v1` as the stable API contract.
- Never render DOCX directly from raw LLM prose; validate structured JSON before rendering.
- Treat `prompts/prompt_peticao.md` and `prompts/prompt_formatacao_word.md` as source-of-truth contracts.
- Preserve prompt usage auditing: prompt name, path, hash, provider/model metadata, and relevant flags.
- Do not log full prompt bodies, raw legal facts, full document text, provider tokens, or sensitive fields by default.
- Preserve `LLM_REQUIRED=true` behavior; do not bypass AI-required paths unless explicitly scoped for tests.
- External providers require explicit per-request consent; missing consent must return `llm_error`, not silently call or fallback.
- Redaction is partial masking only; never describe it as full anonymization.
- Processing should be idempotent where practical: repeated runs must not silently overwrite, duplicate, or lose outputs/reports/state.

# Agent Workflow
- Think before coding: read `README.md`, this file, `git status`, and affected files before editing.
- State assumptions for non-trivial changes; surface risks around LLM, validation, API, security, DOCX, or data retention.
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
- If changing static assets, consider `web/sw.js` cache/version behavior.
- If validation cannot run, report the exact skipped command and reason.

# Security Rules
- NEVER commit `.env`, secrets, provider keys, OAuth tokens, real client documents, private legal facts, or generated sensitive artifacts.
- NEVER version `output/*.docx`, `reports/*.json`, `reports/*.html`, `mcp_inbox.json`, `mcp_outbox.json`, or `mcp_status.json`.
- NEVER send real client data to external providers without explicit consent.
- NEVER weaken auth, validation, provider allowlist, consent checks, or the `API_REQUIRE_TOKEN=1` Docker contract.
- Honor `X-API-Token` on sensitive routes.
- Store secrets only in environment variables or local ignored config.
- Use only fictitious fixtures in `examples/` and `tests/`.

# Sensitive Areas
- `src/infra/llm/`: provider selection, structured output, redaction, consent gating, prompt hashes.
- `prompts/prompt_peticao.md` and `prompts/prompt_formatacao_word.md`: versioned prompt contracts.
- `src/interfaces/api.py`: token enforcement, uploads, `/api/v1`, and sensitive routes.
- `src/infra/docx/` or DOCX rendering code: formatting, validation, and output safety.
- `src/orchestration/`: pipeline, reports, history, retention, and local state.
- `Dockerfile`: `API_REQUIRE_TOKEN=1` and runtime security defaults.
- `.gitignore`: must keep local artifacts and sensitive files ignored.
- `web/sw.js`: service worker cache behavior for static UI updates.

# Known Pitfalls
- External provider calls without explicit consent are security bugs.
- Missing external consent must fail closed with `llm_error`, not fallback silently.
- `mypy` is gradual; current enforced scope is `config.py` and `src/infra/llm`.
- Service worker cache can hide frontend changes if versioning is not updated.
- `/api/v1` is a stable contract; do not break it without explicit scope.
- The system validates form, structure, and obvious risks; it does not decide jurisdiction, deadlines, legal thesis, evidence sufficiency, calculations, strategy, or filing viability.
- Human legal review must remain explicit in user-facing behavior.

# Final Checklist
- Scope respected; no unrelated refactor or formatting churn.
- `/api/v1`, prompt contracts, structured JSON validation, and DOCX rendering flow preserved.
- No secrets, real client data, private legal facts, generated DOCX, or reports committed.
- External provider consent, allowlist, and redaction behavior preserved.
- `compileall` and `pytest -q` run, or skip reason stated.
- Extra checks run when relevant, or limitation reported.
- Documentation updated if behavior, commands, API, prompts, or security changed.
- Assumptions and uncertainties documented.
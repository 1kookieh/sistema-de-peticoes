# Sistema de Petições

[Portuguese version](README.md)

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-local-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Frontend](https://img.shields.io/badge/Frontend-HTML%2FCSS%2FJS-F7DF1E?logo=javascript&logoColor=black)](web/)
[![CI](https://github.com/1kookieh/sistema-de-peticoes/actions/workflows/ci.yml/badge.svg)](https://github.com/1kookieh/sistema-de-peticoes/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A local-first system for generating, validating, reviewing, and downloading Brazilian legal petition drafts as `.docx` files, with a FastAPI API, static web interface, CLI, versioned prompts, audit reports, and an AI-first Groq integration.

> **Supervised use:** this project generates drafts for review by a responsible lawyer. It does not decide litigation strategy, verify deadlines or legal merit, and must not be used for filing without human legal review.

## Overview

The main flow receives case text or uploaded files, extracts and normalizes content, infers the petition type and validation profile when possible, calls the backend-configured LLM layer, validates the structured response, renders a `.docx` with `python-docx`, and writes JSON/HTML audit reports to disk.

The project is designed for local, controlled, single-user use. Its current state is file-based (`output/`, `reports/`, `mcp_*.json`) instead of database-backed. Multi-user or production deployments still require additional authentication, authorization, transactional persistence, observability, and operational retention policies.

## Features

- Local web workspace served by FastAPI, with no frontend build step.
- Free-form chat in the **IA** tab using Groq as the single external provider.
- `.docx` draft generation from text or uploads.
- Upload support for `.txt`, `.md`, `.docx`, `.pdf`, `.png`, `.jpg`, `.jpeg`, and `.webp`.
- Image OCR through Tesseract when installed and configured.
- Catalog of legal document types and formal validation profiles.
- Automatic petition type and profile inference when not provided.
- Output modes: `minuta` and `final`.
- Text validation and structural DOCX validation.
- JSON/HTML reports with execution, prompt, and LLM metadata.
- Local dashboard with metrics derived from reports.
- Versioned REST API under `/api/v1`.
- CLI for processing a local JSON inbox.
- Simple Tkinter desktop interface.
- Dockerfile with `API_REQUIRE_TOKEN=1` by default.
- CI for Python 3.11/3.12 with Ruff, gradual mypy, pip-audit, Bandit, pytest, and a pipeline smoke test.

## Stack

| Area | Confirmed technologies |
|---|---|
| Backend/API | Python 3.11+, FastAPI, Uvicorn, Pydantic Settings |
| LLM | Groq (`llama-3.3-70b-versatile`) as the single external provider; `mock` reserved for tests |
| Documents | `python-docx`, Jinja2 |
| Extraction | `pypdf`, Pillow, pytesseract |
| Frontend | Vanilla HTML, CSS, and JavaScript in `web/` |
| Desktop | Tkinter |
| Testing/quality | pytest, httpx, pytest-cov, Ruff, mypy, Bandit, pip-audit |
| DevOps | Docker, GitHub Actions, Dependabot |

## Architecture

```text
src/
  adapters/        inbox reading, outbox handling, and file extraction
  core/            domain rules, document types, profiles, prompts, validations
  infra/           DOCX, LLM, logging, locks, and local state
  interfaces/      FastAPI API, CLI, and desktop interface
  orchestration/   pipeline, reports, retention, and setup
web/               local static frontend
prompts/           versioned prompt contracts
templates/         HTML report template
docs/              complementary documentation
examples/          fictitious fixtures and examples
tests/             automated test suite
output/            runtime-generated DOCX files, ignored by Git
reports/           runtime JSON/HTML reports, ignored by Git
```

Flow summary:

```text
input/upload
  -> text extraction
  -> document type/profile inference
  -> versioned prompts
  -> Groq or mock in tests
  -> validated structured JSON
  -> renderable text
  -> DOCX
  -> formal validation
  -> report and download
```

## Requirements

- Python 3.11 or newer.
- `pip`.
- Groq API key (`GROQ_API_KEY`) to use the real AI flow.
- Tesseract OCR only if you want OCR for images.
- Docker, optional.

## Installation

```bash
git clone https://github.com/1kookieh/sistema-de-peticoes.git
cd sistema-de-peticoes
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Linux/macOS:

```bash
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

Prepare local runtime folders:

```bash
python -m src --setup
```

For a minimal runtime installation, use `requirements.txt`. For development, tests, and audits, use `requirements-dev.txt`.

## Configuration

Settings are loaded from `.env` through `pydantic-settings`. Use `.env.example` as the reference and never commit a real `.env` file.

Minimal Groq configuration:

```env
EMAIL_ADVOGADO=advogado-responsavel@example.com
LLM_REQUIRED=true
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile
LLM_ALLOW_CLIENT_PROVIDER=false
LLM_CLIENT_ALLOWED_PROVIDERS=["groq"]
GROQ_API_KEY=your-key-here
```

Key variables:

| Variable | Purpose |
|---|---|
| `EMAIL_ADVOGADO` | Email used by CLI/outbox flows. |
| `API_TOKEN` | Optional token for sensitive routes. |
| `API_REQUIRE_TOKEN` | Requires a token even when `API_TOKEN` would otherwise be empty. |
| `API_ALLOWED_ORIGINS` | Origins allowed for mutating requests. |
| `MAX_TEXT_CHARS` | Text size limit accepted by the API. |
| `MAX_DOCX_BYTES` | Maximum accepted size for generated DOCX files. |
| `RATE_LIMIT_WINDOW_SECONDS` | Local rate-limit window. |
| `RATE_LIMIT_MAX_MUTATIONS` | Mutating request limit per window. |
| `MCP_INBOX_PATH` | Local JSON inbox path. |
| `MCP_OUTBOX_PATH` | Local JSON outbox path. |
| `MCP_STATUS_PATH` | Local JSON status path. |
| `RETENTION_ENABLED` | Enables automatic retention cleanup. |
| `LLM_REQUIRED` | Keeps AI mandatory in the main flow. |
| `LLM_PROVIDER` | Fixed app provider: `groq`. |
| `LLM_MODEL` | Groq model used by the backend. |
| `LLM_ALLOW_MOCK` | Allows `mock` for automated tests. |
| `LLM_FALLBACK_ENABLED` | Mock fallback; disabled by default. |
| `LLM_LOG_PROMPT` | Controls prompt logging; keep `false` with sensitive data. |
| `GROQ_API_KEY` | Groq API key. |

## Running

API + web:

```bash
uvicorn src.interfaces.api:app --host 127.0.0.1 --port 8000 --reload
```

On Windows, using the venv directly:

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.interfaces.api:app --host 127.0.0.1 --port 8000 --reload
```

Local URLs:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/api/v1/health
```

There is no `package.json` and no frontend build step. Files in `web/` are served directly by FastAPI.

## Web Workspace

1. Open `http://127.0.0.1:8000/`.
2. In the **IA** tab, confirm consent before sending data to Groq.
3. Chat, attach files, or explicitly request a draft/document generation.
4. After a document is generated, download the `.docx` or open the HTML/JSON report.
5. Use **Peças** and **Início** to inspect local results derived from reports.

## REST API

Main endpoints:

| Method | Route | Description |
|---|---|---|
| `GET` | `/` | Serves the web interface. |
| `GET` | `/api/v1/health` | Healthcheck. |
| `POST` | `/api/v1/setup` | Creates/checks local folders. |
| `GET` | `/api/v1/profiles` | Lists formal validation profiles. |
| `GET` | `/api/v1/piece-types` | Lists document types. |
| `GET` | `/api/v1/limits` | Returns limits and public AI settings. |
| `POST` | `/api/v1/chat` | Free-form AI chat; does not generate DOCX. |
| `POST` | `/api/v1/chat/upload` | Chat with extracted attachment text. |
| `POST` | `/api/v1/documents` | Generates DOCX from text. |
| `POST` | `/api/v1/documents/upload` | Extracts files and generates DOCX. |
| `GET` | `/api/v1/documents/{filename}/download` | Downloads a generated DOCX. |
| `GET` | `/api/v1/pieces` | Lists pieces derived from local reports. |
| `GET` | `/api/v1/dashboard` | Local operational metrics. |
| `GET` | `/api/v1/reports` | Lists local reports. |
| `GET` | `/api/v1/reports/{filename}` | Opens a JSON or HTML report. |

Create a document from text:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/documents \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"Client reports denial of a social-security benefit by INSS. Fictitious test data.\",\"remetente\":\"cliente@example.com\",\"output_mode\":\"minuta\",\"consent_external_provider\":true}"
```

Upload:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/documents/upload \
  -F "files=@relato.pdf" \
  -F "output_mode=minuta" \
  -F "remetente=cliente@example.com" \
  -F "llm_consent_external_provider=true"
```

If `API_TOKEN` is configured, send:

```http
X-API-Token: your-token
```

## CLI

Help:

```bash
python -m src --help
```

List profiles:

```bash
python -m src --list-profiles
```

Process a fictitious inbox with mock and no outbox:

```bash
python -m src --inbox examples/inbox_valid.json --mock --no-outbox --report reports/demo_report.json
```

Process with Groq:

```bash
python -m src --inbox examples/inbox_valid.json --no-outbox --llm-consent-external --report reports/demo_report.json
```

Validate a generated DOCX:

```bash
python -m src.core.validation.docx output/nome-do-arquivo.docx --profile judicial-inicial-jef
```

Apply configured retention:

```bash
python -m src --cleanup-only --apply-retention
```

Desktop interface:

```bash
python -m src.interfaces.desktop
```

## Docker

Build:

```bash
docker build -t sistema-peticoes .
```

Run with token:

```bash
docker run --rm -p 8000:8000 \
  -e API_TOKEN=replace-this-token \
  -e GROQ_API_KEY=your-groq-key \
  sistema-peticoes
```

The `Dockerfile` sets `API_REQUIRE_TOKEN=1` by default. To persist documents and reports:

```bash
docker run --rm -p 8000:8000 \
  -e API_TOKEN=replace-this-token \
  -e GROQ_API_KEY=your-groq-key \
  -v ./output:/app/output \
  -v ./reports:/app/reports \
  sistema-peticoes
```

Do not use `API_REQUIRE_TOKEN=false` on a public network.

## Tests and Quality

Main commands:

```bash
python -m compileall config.py src tests
pytest -q
ruff check .
mypy config.py src/infra/llm
bandit -q -r src
pip-audit -r requirements.txt --strict
```

On Windows, the project also includes:

```powershell
.\scripts\audit.ps1
```

For automated tests, use the mock provider:

```powershell
$env:LLM_PROVIDER='mock'
.\.venv\Scripts\python -m pytest -q
```

If you change `web/app.js`, validate it with:

```bash
node --check web/app.js
```

## Security and Privacy

Treat the following as sensitive:

- `.env`;
- `GROQ_API_KEY` and `API_TOKEN`;
- legal texts and attachments sent to AI;
- `output/*.docx`;
- `reports/*.json` and `reports/*.html`;
- `mcp_inbox.json`, `mcp_outbox.json`, and `mcp_status.json`;
- screenshots containing real data.

Important safeguards:

- Use fictitious data in tests, demos, issues, and public documentation.
- Do not send real data to Groq without authorization and explicit consent.
- Redaction is partial: it reduces exposure of CPF, CNPJ, NIT, NB, RG, CEP, phone numbers, and email addresses, but it does not guarantee full anonymization.
- Do not expose the API publicly without strong authentication, TLS, authorization, controlled logs, and appropriate retention.
- Review legal merit, jurisdiction, deadlines, powers of attorney, claim value, attachments, calculations, and requested relief before any professional use.

See also [SECURITY.md](SECURITY.md) and [docs/legal-limitations.md](docs/legal-limitations.md).

## Current Limitations

- Does not replace a lawyer or human legal review.
- Does not perform real-time case-law research.
- Does not guarantee a correct legal theory, deadline, jurisdiction, or court acceptance.
- No relational database; state is based on local files.
- No multi-user authentication.
- Piece lists and dashboard metrics depend on local reports.
- OCR depends on Tesseract being installed and accessible.
- Groq is external; treat its use as data sharing with a third party.

## Additional Documentation

| Document | Content |
|---|---|
| [docs/api.md](docs/api.md) | API contracts and examples. |
| [docs/architecture.md](docs/architecture.md) | Architecture overview and internal flow. |
| [docs/usage.md](docs/usage.md) | Practical usage guide. |
| [docs/prompts.md](docs/prompts.md) | Versioned prompts and maintenance. |
| [docs/legal-limitations.md](docs/legal-limitations.md) | Legal and LGPD limitations. |
| [docs/roadmap.md](docs/roadmap.md) | Planned improvements. |
| [SECURITY.md](SECURITY.md) | Security and sensitive data. |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute. |

## Short Roadmap

Improvements aligned with the current state:

- Migrate local JSON state to SQLite or another transactional store.
- Add real authentication and authorization for multi-user use.
- Add pagination, filters, and search for pieces and reports.
- Expand frontend E2E tests.
- Improve DOCX/PDF visual preview.
- Improve observability and operational logs.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md). Contributions must preserve:

- mandatory human review;
- sensitive data protection;
- fictitious data in tests and examples;
- explicit consent before using an external provider;
- tests for changes to API, pipeline, DOCX, prompts, LLM, or security.

## License

Distributed under the [MIT](LICENSE) license.

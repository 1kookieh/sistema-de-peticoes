# Sistema de Petições

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![JavaScript](https://img.shields.io/badge/JavaScript-ESM-F7DF1E?logo=javascript&logoColor=black)](web/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)](Dockerfile)
[![Tests](https://img.shields.io/badge/tests-82%20passing-brightgreen.svg)](tests)
[![CI](https://github.com/1kookieh/sistema-de-peticoes/actions/workflows/ci.yml/badge.svg)](https://github.com/1kookieh/sistema-de-peticoes/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Sistema local em **Python + FastAPI + HTML/CSS/JavaScript** para transformar texto, PDF, Word, Markdown ou imagem em documentos jurídicos `.docx`, com validação formal, detector automático de tipo de peça, relatórios JSON/HTML e interface web/desktop.

> **Uso jurídico supervisionado.** O projeto ajuda na preparação formal e na revisão técnica de documentos, mas não substitui advogado, não valida mérito jurídico e não deve ser usado para protocolo sem revisão humana. Veja [docs/legal-limitations.md](docs/legal-limitations.md).

## Destaques

- **Geração local de DOCX:** saída em `output/*.docx`, sem envio para serviços externos no fluxo padrão.
- **Entradas flexíveis:** texto colado, `.txt`, `.md`, `.docx`, `.pdf` e imagens com OCR via Tesseract.
- **API e interface web:** FastAPI em `/api/v1` e front-end local sem build, feito em HTML/CSS/JavaScript modular.
- **Detector automático:** identifica mais de 70 tipos de peças e escolhe perfil formal quando o usuário deixa em automático.
- **Validação dupla:** pré-validação textual e validação estrutural do `.docx` com `python-docx`.
- **Relatórios auditáveis:** JSON e HTML em `reports/`, com histórico local e flags de inferência.
- **Prompts versionados:** `prompt_peticao.md` guia a preparação da peça e `prompt_formatacao_word.md` guia a formatação Word.
- **Arquitetura em camadas:** domínio, infraestrutura, adapters, interfaces e orchestration separados.
- **Docker e CI:** ambiente reprodutível e testes automatizados no GitHub Actions.

## Stack

| Área | Tecnologias |
|---|---|
| Backend | Python 3.11+, FastAPI, Pydantic Settings |
| Documentos | python-docx, validação estrutural de `.docx` |
| Front-end | HTML, CSS, JavaScript ES Modules, Service Worker |
| Desktop | Tkinter |
| Testes | pytest, TestClient, golden files estruturais |
| DevOps | Docker, GitHub Actions |

## Quick Start

### 1. Instalar

```bash
git clone https://github.com/1kookieh/sistema-de-peticoes.git
cd sistema-de-peticoes
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Linux/macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 2. Preparar pastas locais

```bash
python -m src --setup
```

Esse comando cria `output/` e `reports/`, preservando apenas `.gitkeep` no Git.

### 3. Rodar API + web

```bash
uvicorn src.interfaces.api:app --host 127.0.0.1 --port 8000 --reload
```

Abra [http://127.0.0.1:8000](http://127.0.0.1:8000), cole um texto ou envie arquivo e clique em **Gerar e validar DOCX**.

## Comandos úteis

```bash
# CLI em lote
python -m src --inbox examples/inbox_valid.json --profile judicial-inicial-jef --strict --no-outbox --report reports/demo_report.json

# Validação de um DOCX gerado
python -m src.core.validation.docx output/nome-do-arquivo.docx --profile judicial-inicial-jef

# Interface desktop
python -m src.interfaces.desktop

# Docker
docker build -t sistema-peticoes .
docker run --rm -p 8000:8000 sistema-peticoes
```

## Como funciona

```text
Entrada do usuário
  -> extração de texto de arquivo ou OCR
  -> preparação da peça com contrato do prompt_peticao.md
  -> inferência do tipo de peça e perfil formal
  -> pré-validação textual
  -> renderização DOCX com contrato do prompt_formatacao_word.md
  -> validação estrutural do DOCX
  -> relatório JSON/HTML + download do documento
```

Se houver falha em etapa crítica, o documento é bloqueado e o relatório explica o motivo.

## Interfaces disponíveis

| Interface | Comando/rota | Uso |
|---|---|---|
| Web local | `http://127.0.0.1:8000` | Uso diário e demonstração |
| API REST | `/api/v1/*` | Integração local e automações |
| CLI | `python -m src` | Processamento em lote |
| Desktop | `python -m src.interfaces.desktop` | Uso local sem navegador |

Endpoints principais:

```text
GET    /api/v1/health
GET    /api/v1/profiles
GET    /api/v1/piece-types
GET    /api/v1/limits
POST   /api/v1/documents
POST   /api/v1/documents/upload
GET    /api/v1/documents/{filename}/download
GET    /api/v1/reports
GET    /api/v1/reports/{filename}
```

## Estrutura do projeto

```text
src/
  core/                 domínio puro, perfis, tipos de peça, inferência, validações
  adapters/             entrada, saída e extração de arquivos
  infra/                renderização DOCX, locks, logging e estado local
  interfaces/           API, CLI e desktop
  orchestration/        pipeline, relatórios, retenção e setup
web/                    interface local em HTML/CSS/JavaScript
templates/              template HTML de relatório
prompts/                prompts versionados jurídicos e de formatação
docs/                   arquitetura, API, limitações jurídicas e roadmap
tests/                  testes automatizados
examples/               entradas e documentos fictícios de exemplo
```

## Configuração

Use `.env` local, baseado em `.env.example`. Não versione dados reais.

```env
EMAIL_ADVOGADO=advogado-responsavel@example.com
API_TOKEN=
API_ALLOWED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
VALIDATION_PROFILE=judicial-inicial-jef
REMETENTES_AUTORIZADOS=
MAX_JSON_BYTES=2097152
RETENTION_ENABLED=false
RETENTION_OUTPUT_DAYS=30
RETENTION_REPORTS_DAYS=30
RETENTION_QUEUE_DAYS=7
RETENTION_STATUS_DAYS=30
```

Quando `API_TOKEN` estiver preenchido, rotas sensíveis exigem o header `X-API-Token`.

## Testes

```bash
pip install -r requirements-dev.txt
python -m compileall config.py src tests
pytest -q
```

Estado atual local: **82 testes passando**.

## Segurança e LGPD

Trate como sensíveis:

- `output/*.docx`
- `reports/*.json` e `reports/*.html`
- `mcp_inbox.json`, `mcp_outbox.json`, `mcp_status.json`
- `.env`

Boas práticas recomendadas:

- usar apenas dados fictícios em demonstrações públicas;
- manter `output/` e `reports/` fora do Git;
- configurar retenção/expurgo quando houver dados reais;
- usar `API_TOKEN` se a API não estiver restrita ao próprio computador;
- revisar mérito, competência, prazo, OAB, procuração e documentos antes de qualquer uso real.

## Documentação

| Documento | Conteúdo |
|---|---|
| [CLAUDE.md](CLAUDE.md) | Uso com Claude, prompts e integração supervisionada |
| [docs/api.md](docs/api.md) | Contratos REST e exemplos |
| [docs/architecture.md](docs/architecture.md) | Arquitetura e responsabilidades |
| [docs/legal-limitations.md](docs/legal-limitations.md) | Limitações jurídicas, LGPD e revisão humana |
| [docs/roadmap.md](docs/roadmap.md) | Próximas melhorias |
| [prompts/prompt_peticao.md](prompts/prompt_peticao.md) | Prompt jurídico principal |
| [prompts/prompt_formatacao_word.md](prompts/prompt_formatacao_word.md) | Prompt de formatação Word |

## O que este projeto demonstra

- Arquitetura Python em camadas.
- API local com FastAPI e contrato versionado em `/api/v1`.
- Front-end sem framework, modular e responsivo.
- Manipulação real de `.docx` com validação automatizada.
- Preocupação com LGPD, retenção, auditoria e revisão humana.
- Testes automatizados e CI para fluxo crítico.

## Licença

Distribuído sob a licença [MIT](LICENSE).

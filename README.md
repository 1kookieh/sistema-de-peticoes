# Sistema de Petições

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![JavaScript](https://img.shields.io/badge/JavaScript-ESM-F7DF1E?logo=javascript&logoColor=black)](web/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)](Dockerfile)
[![Tests](https://img.shields.io/badge/tests-82%20passing-brightgreen.svg)](tests)
[![CI](https://github.com/1kookieh/sistema-de-peticoes/actions/workflows/ci.yml/badge.svg)](https://github.com/1kookieh/sistema-de-peticoes/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Sistema local em **Python + FastAPI + HTML/CSS/JavaScript** para **validar e renderizar** texto jurídico em documentos `.docx` no padrão forense, com detector automático de tipo de peça, perfis formais por contexto e relatórios JSON/HTML.

> **O sistema não gera texto jurídico com IA.** Ele recebe um texto pronto (digitado, colado ou extraído de PDF/DOCX/imagem via OCR), aplica validações determinísticas (placeholders, OAB, fechamento, valor da causa, seções mínimas) e renderiza um `.docx` no padrão forense. Os prompts em `prompts/` são contratos versionados auditáveis usados como referência para quem prepara o texto, não para chamada a LLM.
>
> **Uso jurídico supervisionado.** Não substitui advogado, não valida mérito e não deve ser usado para protocolo sem revisão humana. Veja [docs/legal-limitations.md](docs/legal-limitations.md).

## Destaques

- **Renderização local de DOCX:** saída em `output/*.docx`, sem envio para serviços externos no fluxo padrão.
- **Entradas flexíveis:** texto colado, `.txt`, `.md`, `.docx`, `.pdf` e imagens com OCR via Tesseract (UTF-8 obrigatório).
- **API e interface web:** FastAPI em `/api/v1` e front-end local sem build, feito em HTML/CSS/JavaScript modular.
- **Detector automático:** identifica mais de 70 tipos de peças e escolhe perfil formal quando o usuário deixa em automático.
- **Validação dupla:** pré-validação textual (placeholders, OAB, fechamento, seções) e validação estrutural do `.docx` com `python-docx` (margens, fontes, recuos, linha de assinatura proibida).
- **Relatórios auditáveis:** JSON e HTML em `reports/`, com histórico local, hash dos prompts e flags de inferência.
- **Prompts versionados:** `prompt_peticao.md` é contrato de redação para advogado/usuário; `prompt_formatacao_word.md` é contrato do padrão Word. **Nenhum dos dois é enviado a um LLM pelo pipeline.** Ambos têm SHA-256 registrado no relatório.
- **Arquitetura em camadas:** domínio, infraestrutura, adapters, interfaces e orchestration separados.
- **Docker e CI:** ambiente reprodutível e testes automatizados no GitHub Actions.

## Demonstração

Fluxo principal:

1. O usuário cola um texto pronto ou envia um arquivo (PDF, DOCX, TXT, MD ou imagem).
2. O sistema extrai o texto bruto e infere o tipo de peça por regras determinísticas.
3. A pré-validação textual bloqueia placeholders, dados fictícios, ausência de OAB ou de seções mínimas.
4. O renderizador aplica o padrão forense determinístico (A4, Times 12, 1,5, recuo 2,5 cm, 7 linhas após endereçamento).
5. O `.docx` gerado é reaberto e revalidado; relatório JSON/HTML registra perfil, hash dos prompts e violações.

> Demonstração visual recomendada: adicionar um GIF curto da interface web mostrando upload, geração e download.

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
Entrada do usuário (texto pronto)
  -> extração de texto de arquivo ou OCR (UTF-8 obrigatório)
  -> inferência determinística do tipo de peça e perfil formal
  -> pré-validação textual (placeholders, OAB, fechamento, seções, valor da causa)
  -> renderização DOCX no padrão forense (sem chamada a LLM)
  -> validação estrutural do DOCX gerado (margens, fontes, recuos, assinatura)
  -> relatório JSON/HTML com hash dos prompts e download do documento
```

> O contrato dos prompts versionados (`prompts/prompt_peticao.md` e `prompts/prompt_formatacao_word.md`) é **carregado e auditado** pelo pipeline (hash SHA-256 no relatório), mas o texto **não é reescrito por IA**. Eles servem como referência humana para quem prepara a minuta e como contrato versionado de formatação.

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

## Roadmap curto

- Adicionar screenshots/GIFs reais da interface web.
- Criar release estável `v1.0.0` no GitHub.
- Ampliar exemplos fictícios de peças geradas.
- Evoluir testes de regressão para mais tipos de peça.
- Melhorar relatórios visuais sem expor dados sensíveis.

## Licença

Distribuído sob a licença [MIT](LICENSE).

# Sistema de Petições

[English version](README.en.md)

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-local-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Frontend](https://img.shields.io/badge/Frontend-HTML%2FCSS%2FJS-F7DF1E?logo=javascript&logoColor=black)](web/)
[![CI](https://github.com/1kookieh/sistema-de-peticoes/actions/workflows/ci.yml/badge.svg)](https://github.com/1kookieh/sistema-de-peticoes/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Sistema local-first para gerar, validar, revisar e baixar minutas jurídicas brasileiras em `.docx`, com API FastAPI, interface web estática, CLI, prompts versionados, relatórios de auditoria e integração AI-first com Groq.

> **Uso supervisionado:** o projeto gera rascunhos/minutas para revisão de advogado responsável. Ele não decide estratégia processual, não verifica prazos ou mérito jurídico e não deve ser usado para protocolo sem revisão humana.

## Visão Geral

O fluxo principal recebe texto ou arquivos do caso, extrai e normaliza o conteúdo, infere tipo de peça/perfil formal quando possível, chama a camada LLM configurada no backend, valida a resposta estruturada, renderiza um `.docx` com `python-docx` e grava relatórios JSON/HTML em disco.

O projeto foi pensado para uso local/controlado e single-user. O estado atual usa arquivos locais (`output/`, `reports/`, `mcp_*.json`) em vez de banco de dados. Para uso multiusuário ou em produção, ainda são necessárias camadas adicionais de autenticação, autorização, persistência transacional, observabilidade e política operacional de retenção.

## Funcionalidades

- Workspace web local servido pelo FastAPI, sem build frontend.
- Chat livre na aba **IA** usando Groq como provider externo único.
- Geração de minutas `.docx` a partir de texto ou upload.
- Upload de `.txt`, `.md`, `.docx`, `.pdf`, `.png`, `.jpg`, `.jpeg` e `.webp`.
- OCR de imagens via Tesseract quando instalado/configurado.
- Catálogo de tipos de peça e perfis formais por contexto.
- Inferência automática de tipo de peça e perfil quando o usuário não informa.
- Modos de saída `minuta` e `final`.
- Validação textual e validação estrutural do DOCX gerado.
- Relatórios JSON/HTML com metadados de execução, prompt e LLM.
- Dashboard local com métricas derivadas dos relatórios.
- API REST versionada em `/api/v1`.
- CLI para processamento de inbox JSON local.
- Interface desktop simples em Tkinter.
- Dockerfile com `API_REQUIRE_TOKEN=1` por padrão.
- CI com Python 3.11/3.12, Ruff, mypy gradual, pip-audit, Bandit, pytest e smoke test do pipeline.

## Stack

| Área | Tecnologias confirmadas |
|---|---|
| Backend/API | Python 3.11+, FastAPI, Uvicorn, Pydantic Settings |
| LLM | Groq (`llama-3.3-70b-versatile`) como provider externo único; `mock` reservado para testes |
| Documentos | `python-docx`, Jinja2 |
| Extração | `pypdf`, Pillow, pytesseract |
| Frontend | HTML, CSS e JavaScript vanilla em `web/` |
| Desktop | Tkinter |
| Testes/qualidade | pytest, httpx, pytest-cov, Ruff, mypy, Bandit, pip-audit |
| DevOps | Docker, GitHub Actions, Dependabot |

## Arquitetura

```text
src/
  adapters/        leitura de inbox, outbox e extração de arquivos
  core/            domínio, tipos de peça, perfis, prompts e validações
  infra/           DOCX, LLM, logging, locks e estado local
  interfaces/      API FastAPI, CLI e desktop
  orchestration/   pipeline, relatórios, retenção e setup
web/               frontend estático local
prompts/           contratos versionados dos prompts
templates/         template HTML dos relatórios
docs/              documentação complementar
examples/          fixtures e exemplos fictícios
tests/             suíte automatizada
output/            DOCX gerados em runtime, ignorado pelo Git
reports/           relatórios JSON/HTML em runtime, ignorado pelo Git
```

Fluxo resumido:

```text
entrada/upload
  -> extração de texto
  -> inferência de peça/perfil
  -> prompts versionados
  -> Groq ou mock em testes
  -> JSON estruturado validado
  -> texto renderizável
  -> DOCX
  -> validação formal
  -> relatório e download
```

## Requisitos

- Python 3.11 ou superior.
- `pip`.
- Chave Groq (`GROQ_API_KEY`) para usar o fluxo real de IA.
- Tesseract OCR somente se for usar OCR em imagens.
- Docker opcional.

## Instalação

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

Prepare as pastas locais:

```bash
python -m src --setup
```

Para instalação mínima de runtime, use `requirements.txt`. Para desenvolvimento, testes e auditoria, use `requirements-dev.txt`.

## Configuração

As configurações são lidas de `.env` por `pydantic-settings`. Use `.env.example` como base e nunca versione `.env` real.

Configuração mínima para usar Groq:

```env
EMAIL_ADVOGADO=advogado-responsavel@example.com
LLM_REQUIRED=true
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile
LLM_ALLOW_CLIENT_PROVIDER=false
LLM_CLIENT_ALLOWED_PROVIDERS=["groq"]
GROQ_API_KEY=coloque-sua-chave
```

Variáveis mais relevantes:

| Variável | Finalidade |
|---|---|
| `EMAIL_ADVOGADO` | E-mail usado nos fluxos de CLI/outbox. |
| `API_TOKEN` | Token opcional para rotas sensíveis. |
| `API_REQUIRE_TOKEN` | Exige token mesmo quando `API_TOKEN` estaria vazio. |
| `API_ALLOWED_ORIGINS` | Origens permitidas para chamadas mutadoras. |
| `MAX_TEXT_CHARS` | Limite de texto aceito pela API. |
| `MAX_DOCX_BYTES` | Tamanho máximo aceito para DOCX gerado. |
| `RATE_LIMIT_WINDOW_SECONDS` | Janela do rate limit local. |
| `RATE_LIMIT_MAX_MUTATIONS` | Limite de chamadas mutadoras por janela. |
| `MCP_INBOX_PATH` | Caminho do inbox JSON local. |
| `MCP_OUTBOX_PATH` | Caminho do outbox JSON local. |
| `MCP_STATUS_PATH` | Caminho do status JSON local. |
| `RETENTION_ENABLED` | Habilita retenção automática. |
| `LLM_REQUIRED` | Mantém IA obrigatória no fluxo principal. |
| `LLM_PROVIDER` | Provider fixo do app: `groq`. |
| `LLM_MODEL` | Modelo Groq usado pelo backend. |
| `LLM_ALLOW_MOCK` | Permite `mock` para testes automatizados. |
| `LLM_FALLBACK_ENABLED` | Fallback para mock; desativado por padrão. |
| `LLM_LOG_PROMPT` | Controla logging de prompt; mantenha `false` com dados sensíveis. |
| `GROQ_API_KEY` | Chave da Groq. |

## Como Executar

API + web:

```bash
uvicorn src.interfaces.api:app --host 127.0.0.1 --port 8000 --reload
```

No Windows, usando a venv diretamente:

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.interfaces.api:app --host 127.0.0.1 --port 8000 --reload
```

URLs locais:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/api/v1/health
```

Não há `package.json` nem etapa de build para o frontend. Os arquivos em `web/` são servidos diretamente pelo FastAPI.

## Uso Pelo Workspace Web

1. Abra `http://127.0.0.1:8000/`.
2. Na aba **IA**, confirme o consentimento antes de enviar dados ao Groq.
3. Converse, anexe arquivos ou peça explicitamente a geração de uma minuta/documento.
4. Ao gerar uma peça, baixe o `.docx` ou abra o relatório HTML/JSON.
5. Use **Peças** e **Início** para consultar resultados locais derivados dos relatórios.

## API REST

Endpoints principais:

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Serve a interface web. |
| `GET` | `/api/v1/health` | Healthcheck. |
| `POST` | `/api/v1/setup` | Cria/verifica pastas locais. |
| `GET` | `/api/v1/profiles` | Lista perfis formais. |
| `GET` | `/api/v1/piece-types` | Lista tipos de peça. |
| `GET` | `/api/v1/limits` | Retorna limites e configuração pública da IA. |
| `POST` | `/api/v1/chat` | Conversa livre com IA; não gera DOCX. |
| `POST` | `/api/v1/chat/upload` | Conversa com texto extraído de anexos. |
| `POST` | `/api/v1/documents` | Gera DOCX a partir de texto. |
| `POST` | `/api/v1/documents/upload` | Extrai arquivos e gera DOCX. |
| `GET` | `/api/v1/documents/{filename}/download` | Baixa DOCX gerado. |
| `GET` | `/api/v1/pieces` | Lista peças derivadas de relatórios locais. |
| `GET` | `/api/v1/dashboard` | Métricas operacionais locais. |
| `GET` | `/api/v1/reports` | Lista relatórios locais. |
| `GET` | `/api/v1/reports/{filename}` | Abre relatório JSON ou HTML. |

Criar documento por texto:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/documents \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"Cliente relata indeferimento de benefício pelo INSS. Dados fictícios para teste.\",\"remetente\":\"cliente@example.com\",\"output_mode\":\"minuta\",\"consent_external_provider\":true}"
```

Upload:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/documents/upload \
  -F "files=@relato.pdf" \
  -F "output_mode=minuta" \
  -F "remetente=cliente@example.com" \
  -F "llm_consent_external_provider=true"
```

Se `API_TOKEN` estiver configurado, envie:

```http
X-API-Token: valor-do-token
```

## CLI

Ajuda:

```bash
python -m src --help
```

Listar perfis:

```bash
python -m src --list-profiles
```

Processar inbox fictício com mock e sem outbox:

```bash
python -m src --inbox examples/inbox_valid.json --mock --no-outbox --report reports/demo_report.json
```

Processar com Groq:

```bash
python -m src --inbox examples/inbox_valid.json --no-outbox --llm-consent-external --report reports/demo_report.json
```

Validar um DOCX gerado:

```bash
python -m src.core.validation.docx output/nome-do-arquivo.docx --profile judicial-inicial-jef
```

Aplicar retenção configurada:

```bash
python -m src --cleanup-only --apply-retention
```

Interface desktop:

```bash
python -m src.interfaces.desktop
```

## Docker

Build:

```bash
docker build -t sistema-peticoes .
```

Executar com token:

```bash
docker run --rm -p 8000:8000 \
  -e API_TOKEN=troque-este-token \
  -e GROQ_API_KEY=sua-chave-groq \
  sistema-peticoes
```

O `Dockerfile` define `API_REQUIRE_TOKEN=1` por padrão. Para preservar documentos e relatórios:

```bash
docker run --rm -p 8000:8000 \
  -e API_TOKEN=troque-este-token \
  -e GROQ_API_KEY=sua-chave-groq \
  -v ./output:/app/output \
  -v ./reports:/app/reports \
  sistema-peticoes
```

Não use `API_REQUIRE_TOKEN=false` em rede pública.

## Testes e Qualidade

Comandos principais:

```bash
python -m compileall config.py src tests
pytest -q
ruff check .
mypy config.py src/infra/llm
bandit -q -r src
pip-audit -r requirements.txt --strict
```

No Windows, o projeto também inclui:

```powershell
.\scripts\audit.ps1
```

Para testes automatizados, use provider mock:

```powershell
$env:LLM_PROVIDER='mock'
.\.venv\Scripts\python -m pytest -q
```

Se alterar `web/app.js`, valide:

```bash
node --check web/app.js
```

## Segurança e Privacidade

Considere sensíveis:

- `.env`;
- `GROQ_API_KEY` e `API_TOKEN`;
- textos jurídicos e anexos enviados para IA;
- `output/*.docx`;
- `reports/*.json` e `reports/*.html`;
- `mcp_inbox.json`, `mcp_outbox.json` e `mcp_status.json`;
- prints da interface com dados reais.

Cuidados importantes:

- Use dados fictícios em testes, demos, issues e documentação pública.
- Não envie dados reais ao Groq sem autorização e consentimento explícito.
- A redaction é parcial: reduz exposição de CPF, CNPJ, NIT, NB, RG, CEP, telefone e e-mail, mas não garante anonimização completa.
- Não exponha a API publicamente sem autenticação forte, TLS, autorização, logs controlados e retenção adequada.
- Revise mérito, competência, prazos, procuração, valor da causa, anexos, cálculos e pedidos antes de qualquer uso profissional.

Veja também [SECURITY.md](SECURITY.md) e [docs/legal-limitations.md](docs/legal-limitations.md).

## Limitações Atuais

- Não substitui advogado nem revisão jurídica humana.
- Não pesquisa jurisprudência em tempo real.
- Não garante tese correta, prazo correto, competência correta ou aceitação por tribunal.
- Não há banco de dados relacional; o estado é baseado em arquivos locais.
- Não há autenticação multiusuário.
- A listagem de peças e o dashboard dependem de relatórios locais.
- OCR depende de Tesseract instalado e acessível no ambiente.
- Groq é externo; trate o uso como compartilhamento de dados com terceiro.

## Documentação Complementar

| Documento | Conteúdo |
|---|---|
| [docs/api.md](docs/api.md) | Contratos e exemplos da API. |
| [docs/architecture.md](docs/architecture.md) | Visão de arquitetura e fluxo interno. |
| [docs/usage.md](docs/usage.md) | Guia prático de uso. |
| [docs/prompts.md](docs/prompts.md) | Prompts versionados e manutenção. |
| [docs/legal-limitations.md](docs/legal-limitations.md) | Limitações jurídicas e LGPD. |
| [docs/roadmap.md](docs/roadmap.md) | Melhorias planejadas. |
| [SECURITY.md](SECURITY.md) | Segurança e dados sensíveis. |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Como contribuir. |

## Roadmap Resumido

Melhorias coerentes com o estado atual:

- Migrar estado local JSON para SQLite ou outro armazenamento transacional.
- Adicionar autenticação e autorização reais para multiusuário.
- Ampliar filtros e busca em peças e relatórios.
- Ampliar testes E2E do frontend.
- Evoluir preview visual de DOCX/PDF.
- Melhorar observabilidade e logs operacionais.

## Contribuição

Leia [CONTRIBUTING.md](CONTRIBUTING.md). Contribuições devem preservar:

- revisão humana obrigatória;
- proteção de dados sensíveis;
- uso de dados fictícios em testes e exemplos;
- consentimento explícito antes de provider externo;
- testes para mudanças em API, pipeline, DOCX, prompts, LLM ou segurança.

## Licença

Distribuído sob a licença [MIT](LICENSE).

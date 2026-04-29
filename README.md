# Sistema de Petições

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-local-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![JavaScript](https://img.shields.io/badge/JavaScript-ESM-F7DF1E?logo=javascript&logoColor=black)](web/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)](Dockerfile)
[![CI](https://github.com/1kookieh/sistema-de-peticoes/actions/workflows/ci.yml/badge.svg)](https://github.com/1kookieh/sistema-de-peticoes/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Sistema local AI-first para criar minutas jurídicas em `.docx`, com API FastAPI, interface web, CLI, prompts versionados e camada LLM obrigatória no fluxo principal.

> Uso supervisionado: este projeto não substitui advogado, não decide mérito jurídico e não deve ser usado para protocolo sem revisão humana.

## Visão Geral

O projeto resolve um problema prático: transformar texto do caso, arquivos ou uma resposta estruturada de IA em um documento Word com padrão forense, validações automáticas e relatório de auditoria.

O fluxo principal sempre passa pela camada de IA configurada no backend. O padrão de desenvolvimento usa provider `mock`, sem envio externo; providers reais, como `openai` e `anthropic`, exigem configuração de chave e consentimento explícito por requisição.

## Principais Funcionalidades

- Geração de `.docx` jurídico com `python-docx`.
- Interface web local em HTML, CSS e JavaScript puro.
- API REST versionada em `/api/v1`.
- CLI para uso em lote com inbox JSON.
- Interface desktop simples com Tkinter.
- Upload de `.txt`, `.md`, `.docx`, `.pdf` e imagens para OCR.
- Detecção automática do tipo de peça e do perfil formal.
- Modos de saída de criação: `minuta` e `final`.
- Camada LLM obrigatória no fluxo principal, com providers `mock`, `ollama`, `openai` e `anthropic`.
- Prompts versionados em `prompts/`.
- Validação textual e validação estrutural do DOCX.
- Relatórios JSON/HTML em `reports/`.
- Dockerfile e CI com testes automatizados.

## Fluxo de Uso

```text
Entrada do usuário ou upload
  -> extração/normalização do texto
  -> inferência do tipo de peça e perfil formal
  -> geração por IA com JSON estruturado
  -> validação textual
  -> renderização DOCX
  -> validação estrutural do DOCX
  -> relatório JSON/HTML
  -> download do documento
```

## Tecnologias Utilizadas

| Área | Tecnologias |
|---|---|
| Backend | Python 3.11+, FastAPI, Pydantic Settings |
| IA/LLM | Camada de providers, mock local, Ollama local, OpenAI e Anthropic via HTTP |
| DOCX | python-docx |
| Extração | pypdf, Pillow, pytesseract |
| Front-end | HTML, CSS, JavaScript ES Modules, Service Worker |
| Desktop | Tkinter |
| Testes | pytest, FastAPI TestClient |
| DevOps | Docker, GitHub Actions |

## Estrutura do Projeto

```text
src/
  core/            domínio, perfis, tipos de peça, prompts e validações
  adapters/        inbox, outbox e extração de arquivos
  infra/           DOCX, LLM, locks, logging e estado local
  interfaces/      API, CLI e desktop
  orchestration/   pipeline, relatórios, retenção e setup
web/               interface local
templates/         template HTML de relatório
prompts/           prompts jurídicos e de formatação
docs/              documentação técnica
tests/             testes automatizados
examples/          exemplos fictícios
```

## Pré-requisitos

- Python 3.11 ou superior.
- Windows PowerShell, Linux ou macOS.
- Tesseract OCR instalado apenas se você quiser extrair texto de imagens.
- Docker opcional.
- Chave de API somente se você ativar IA externa (`openai` ou `anthropic`).

## Instalação

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

Prepare as pastas locais:

```bash
python -m src --setup
```

## Como Rodar

API + interface web:

```bash
uvicorn src.interfaces.api:app --host 127.0.0.1 --port 8000 --reload
```

Abra:

```text
http://127.0.0.1:8000
```

Na tela web:

1. Escolha o tipo de peça ou deixe em detecção automática.
2. Escolha o perfil formal ou deixe em detecção automática.
3. Cole o texto do caso ou envie arquivos.
4. Escolha o modo de saída.
5. Clique em `Criar documento com IA` para gerar a minuta DOCX.

## Configuração AI-first

```env
LLM_REQUIRED=true
LLM_ALLOW_MOCK=true
LLM_ALLOW_CLIENT_PROVIDER=true
LLM_CLIENT_ALLOWED_PROVIDERS=mock,ollama,openai,anthropic
LLM_MODE=mock
LLM_PROVIDER=mock
```

Com `LLM_REQUIRED=true`, o endpoint principal de criação sempre chama a camada LLM. O cliente não precisa enviar `llm.enabled=true`; o backend define allowlist, modelo padrão, temperatura, timeout e prompts. Quando `LLM_ALLOW_CLIENT_PROVIDER=true`, a interface permite escolher apenas providers liberados em `LLM_CLIENT_ALLOWED_PROVIDERS`; `none` não é oferecido no fluxo principal.

## Uso Com IA/LLM

Quando cria um documento, o sistema monta um prompt final usando:

- `prompts/prompt_peticao.md`;
- `prompts/prompt_formatacao_word.md`;
- texto do caso;
- tipo de peça;
- perfil formal;
- instruções de segurança e saída JSON.

A resposta da IA deve ser JSON estruturado validável. O DOCX é renderizado a partir dessa estrutura, não do texto livre cru.

| Provider | Descrição | Requer chave |
|---|---|---|
| `mock` | Simula resposta estruturada para testes | Não |
| `openai` | Usa API da OpenAI | Sim |
| `anthropic` | Usa API da Anthropic/Claude | Sim |
| `ollama` | Usa modelo local via Ollama em `OLLAMA_BASE_URL` | Não |

### IA mock

Use para testar o fluxo sem enviar dados para fora:

```env
LLM_PROVIDER=mock
LLM_MODEL=
```

### OpenAI

Use apenas em ambiente local/controlado:

```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=coloque-sua-chave-no-env-local
LLM_FALLBACK_ENABLED=false
```

### Anthropic / Claude

Use apenas em ambiente local/controlado:

```env
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-haiku-latest
ANTHROPIC_API_KEY=coloque-sua-chave-no-env-local
LLM_FALLBACK_ENABLED=false
```

### Ollama local

Use quando quiser IA local sem enviar dados para API externa. Instale o Ollama, baixe um modelo compatível e mantenha o serviço ativo:

```env
LLM_PROVIDER=ollama
LLM_MODEL=llama3.1:8b
OLLAMA_BASE_URL=http://localhost:11434
```

Cuidados:

- Nunca commite `.env` real.
- Nunca coloque chave de API no README, issue, print ou log.
- Ao usar IA externa, o texto informado pode ser enviado ao provedor configurado.
- A API exige consentimento explícito por requisição para providers externos, via
  `llm.consent_external_provider=true` ou campo de upload `llm_consent_external_provider=true`.
- Antes do envio a provider externo, o pipeline mascara identificadores como CPF,
  CNPJ, NIT, NB, RG, CEP, telefone e e-mail quando detectados.
- Esse mascaramento é parcial e não garante anonimização completa: nomes, fatos,
  contexto jurídico e outros dados sensíveis podem permanecer no texto enviado.
- O fallback para mock só ocorre se `LLM_FALLBACK_ENABLED=true`.

## Geração de DOCX

Os arquivos gerados ficam em:

```text
output/
```

Os relatórios ficam em:

```text
reports/
```

Essas pastas são runtime local. Não versione documentos reais, relatórios reais ou dados de clientes.

## API

Documentação interativa:

```text
http://127.0.0.1:8000/docs
```

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

Exemplo com IA mock:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/documents \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"Relato do caso para teste.\",\"output_mode\":\"minuta\",\"llm\":{\"provider\":\"mock\"}}"
```

Veja mais em [docs/api.md](docs/api.md).

## CLI

Ajuda:

```bash
python -m src --help
```

Processar inbox fictício sem outbox:

```bash
python -m src --inbox examples/inbox_valid.json --profile judicial-inicial-jef --strict --no-outbox --report reports/demo_report.json
```

Usar IA mock pela CLI:

```bash
python -m src --inbox examples/inbox_valid.json --no-outbox --mock --output-mode minuta
```

Interface desktop:

```bash
python -m src.interfaces.desktop
```

Guia passo a passo: [docs/usage.md](docs/usage.md).

## Prompts

Os prompts ficam em [prompts/](prompts/):

| Arquivo | Função |
|---|---|
| `prompt_peticao.md` | Regras jurídicas, limites, estrutura e cautelas de geração |
| `prompt_formatacao_word.md` | Regras de formatação esperadas para Word/DOCX |

Ao alterar prompts, rode os testes e gere um DOCX fictício para revisar o resultado.

Veja [docs/prompts.md](docs/prompts.md).

## Documentação Complementar

| Documento | Conteúdo |
|---|---|
| [docs/usage.md](docs/usage.md) | Guia prático de uso |
| [docs/api.md](docs/api.md) | API, payloads e exemplos |
| [docs/architecture.md](docs/architecture.md) | Arquitetura e fluxo interno |
| [docs/prompts.md](docs/prompts.md) | Uso e manutenção dos prompts |
| [docs/legal-limitations.md](docs/legal-limitations.md) | Limitações jurídicas e LGPD |
| [SECURITY.md](SECURITY.md) | Segurança e dados sensíveis |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribuição |
| [CLAUDE.md](CLAUDE.md) | Orientações para agentes Claude |

## Testes

Instale dependências de desenvolvimento:

```bash
pip install -r requirements-dev.txt
```

Execute:

```bash
python -m compileall config.py src tests
pytest -q
```

Validações de qualidade usadas no CI:

```bash
ruff check .
mypy config.py src/infra/llm
pip-audit -r requirements.txt --strict
bandit -q -r src
```

O type-check ainda é gradual: o projeto valida `config.py` e `src/infra/llm` no CI.

No Windows deste projeto, caso `python` global não esteja no PATH, use:

```powershell
.\.venv\Scripts\python.exe -m compileall config.py src tests
.\.venv\Scripts\python.exe -m pytest -q
```

## Docker

```bash
docker build -t sistema-peticoes .
docker run --rm -p 8000:8000 -e API_TOKEN=troque-este-token sistema-peticoes
```

O `Dockerfile` exige token por padrão (`API_REQUIRE_TOKEN=1`). Use o mesmo valor em `X-API-Token` para rotas sensíveis:

```bash
curl http://127.0.0.1:8000/api/v1/health
curl -H "X-API-Token: troque-este-token" http://127.0.0.1:8000/api/v1/reports
```

Para demonstração local isolada, é possível desativar explicitamente:

```bash
docker run --rm -p 8000:8000 -e API_REQUIRE_TOKEN=false sistema-peticoes
```

Para dados reais, monte volumes locais protegidos:

```bash
docker run --rm -p 8000:8000 -e API_TOKEN=troque-este-token -v ./output:/app/output -v ./reports:/app/reports sistema-peticoes
```

## Segurança e Privacidade

Considere sensíveis:

- `.env`;
- `output/*.docx`;
- `reports/*.json`;
- `reports/*.html`;
- inbox, outbox e status locais;
- textos jurídicos enviados para IA externa.

Recomendações:

- Use dados fictícios em demonstrações públicas.
- Configure `API_TOKEN` se expuser a API fora do loopback.
- Não envie dados reais para IA externa sem autorização e sem marcar o consentimento explícito no fluxo.
- Mesmo com mascaramento automático parcial, revise manualmente o texto antes de usar provider externo.
- Não trate redaction como anonimização jurídica, técnica ou operacional.
- Revise sempre mérito, competência, prazo, OAB, procuração, anexos e valor da causa.
- Leia [SECURITY.md](SECURITY.md) e [docs/legal-limitations.md](docs/legal-limitations.md).

## Limitações

- Não substitui advogado.
- Não garante aceitação por tribunal, cartório ou órgão administrativo.
- Não pesquisa jurisprudência em tempo real.
- Não valida estratégia processual.
- Não garante que dados fornecidos pelo usuário sejam verdadeiros.

Nota atual: providers implementados nesta versão: `mock`, `ollama`, `openai` e `anthropic`. Gemini/OpenRouter seguem como evolução futura.

## Roadmap

- Adicionar screenshots/GIFs reais da interface.
- Evoluir providers futuros como Gemini/OpenRouter e melhorar suporte local via Ollama.
- Melhorar validações jurídicas específicas por tipo de peça.
- Adicionar paginação/filtros avançados em relatórios.
- Evoluir exportação PDF opcional via ferramenta local.

Veja [docs/roadmap.md](docs/roadmap.md).

## Contribuição

Leia [CONTRIBUTING.md](CONTRIBUTING.md). Contribuições devem preservar revisão humana obrigatória, não expor dados sensíveis e incluir testes quando alterarem geração, validação, API ou prompts.

## Licença

Distribuído sob a licença [MIT](LICENSE).

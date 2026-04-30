# Sistema de Petições

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-local-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![JavaScript](https://img.shields.io/badge/Frontend-HTML%2FCSS%2FJS-F7DF1E?logo=javascript&logoColor=black)](web/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)](Dockerfile)
[![CI](https://github.com/1kookieh/sistema-de-peticoes/actions/workflows/ci.yml/badge.svg)](https://github.com/1kookieh/sistema-de-peticoes/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Sistema local para criar, revisar e baixar minutas jurídicas em `.docx` com apoio de IA, API FastAPI, interface web, CLI, prompts versionados e relatórios de auditoria.

> **Uso supervisionado:** este projeto não substitui advogado, não decide estratégia processual e não deve ser usado para protocolo sem revisão humana.

## Visão Geral

O projeto transforma relatos de caso e arquivos anexados em documentos Word com padrão forense. O fluxo principal usa uma camada LLM configurada no backend, gera uma resposta estruturada, renderiza o DOCX e registra relatórios JSON/HTML em disco.

A interface web atual é um workspace local com:

- aba **Início**, com métricas operacionais e gráficos;
- aba **IA**, com conversa, anexos e seleção de provider;
- aba **Peças**, com listagem de peças geradas e ações de visualizar/baixar;
- aba **Configurações**, com preferências locais e dados públicos da configuração do backend.

O projeto foi desenhado para execução local/controlada. Para uso em rede, produção ou multiusuário, ainda são necessárias camadas adicionais de autenticação, autorização, persistência e observabilidade.

## Funcionalidades Implementadas

- Geração de minutas `.docx` com `python-docx`.
- API REST versionada em `/api/v1`.
- Interface web estática servida pelo FastAPI.
- Chat local com IA para conversa livre.
- Geração de peça a partir de texto ou arquivos.
- Upload de `.txt`, `.md`, `.docx`, `.pdf` e imagens com OCR.
- Dashboard local com métricas, evolução mensal, top tipos de peça e peças por cidade/UF.
- Lista de peças geradas a partir dos relatórios locais.
- Inferência automática de tipo de peça e perfil formal.
- Providers LLM: `mock`, `ollama`, `openai` e `anthropic`.
- Redaction parcial antes de envio para providers externos.
- Prompts versionados em `prompts/`.
- Validações textuais e estruturais do DOCX.
- Relatórios JSON/HTML em `reports/`.
- CLI para processamento por inbox JSON.
- Interface desktop simples com Tkinter.
- Dockerfile e CI com validações automatizadas.

## Estado Atual Importante

- O fluxo principal de criação de documentos é **AI-first**: por padrão, documentos passam pela camada LLM.
- O provider `mock` é o caminho mais seguro para testes e desenvolvimento.
- O provider `ollama` usa IA local via `OLLAMA_BASE_URL`.
- Providers externos (`openai` e `anthropic`) exigem chave e consentimento explícito.
- O chat direto da API local está implementado para `mock` e `ollama`. A geração de documentos usa a camada LLM completa.
- Não há banco de dados relacional: peças e métricas são derivadas de arquivos locais em `reports/` e `output/`.

## Tecnologias

| Área | Tecnologias |
|---|---|
| Backend/API | Python 3.11+, FastAPI, Uvicorn, Pydantic Settings |
| IA/LLM | Mock local, Ollama, OpenAI, Anthropic/Claude |
| Documentos | python-docx |
| Extração | pypdf, Pillow, pytesseract |
| Front-end | HTML, CSS e JavaScript puro |
| Desktop | Tkinter |
| Testes | pytest, FastAPI TestClient, pytest-cov |
| Qualidade | ruff, mypy, bandit, pip-audit |
| DevOps | Docker, GitHub Actions |

## Estrutura Do Projeto

```text
src/
  adapters/        inbox, outbox e extração de arquivos
  core/            domínio, perfis, tipos de peça, prompts e validações
  infra/           DOCX, LLM, locks, logging e estado local
  interfaces/      API FastAPI, CLI e interface desktop
  orchestration/   pipeline, relatórios, retenção e setup
web/               interface web local
prompts/           prompts jurídicos e de formatação
templates/         template HTML de relatório
docs/              documentação técnica complementar
examples/          exemplos fictícios
tests/             testes automatizados
output/            DOCX gerados em runtime
reports/           relatórios JSON/HTML em runtime
```

## Pré-Requisitos

- Python 3.11 ou superior.
- `pip`.
- Tesseract OCR instalado somente se for usar OCR em imagens.
- Ollama opcional, apenas para provider local real.
- Docker opcional.
- Chave OpenAI ou Anthropic opcional, apenas para provider externo.

## Instalação Local

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

## Configuração De Ambiente

As configurações ficam em `.env`. O arquivo real não deve ser versionado.

| Variável | Uso |
|---|---|
| `EMAIL_ADVOGADO` | E-mail usado nos fluxos de outbox/CLI. |
| `API_TOKEN` | Token opcional para proteger rotas sensíveis. |
| `API_REQUIRE_TOKEN` | Quando `true`, exige token mesmo que o ambiente tente rodar sem ele. |
| `API_ALLOWED_ORIGINS` | Origens permitidas para chamadas mutadoras. |
| `MAX_TEXT_CHARS` | Limite de caracteres para entrada textual. |
| `MAX_JSON_BYTES` | Limite de payload JSON. |
| `REMETENTES_AUTORIZADOS` | Allowlist opcional para fluxos de inbox. |
| `MCP_INBOX_PATH` | Caminho do inbox local JSON. |
| `MCP_OUTBOX_PATH` | Caminho do outbox local JSON. |
| `MCP_STATUS_PATH` | Caminho do status local JSON. |
| `RETENTION_ENABLED` | Ativa limpeza por retenção. |
| `RETENTION_OUTPUT_DAYS` | Retenção de arquivos em `output/`. |
| `RETENTION_REPORTS_DAYS` | Retenção de relatórios em `reports/`. |
| `LLM_REQUIRED` | Mantém IA obrigatória no fluxo principal. |
| `LLM_ALLOW_MOCK` | Permite provider mock. |
| `LLM_ALLOW_CLIENT_PROVIDER` | Permite o cliente escolher provider dentro da allowlist. |
| `LLM_CLIENT_ALLOWED_PROVIDERS` | Providers permitidos para seleção pelo cliente. |
| `LLM_PROVIDER` | Provider padrão: `mock`, `ollama`, `openai` ou `anthropic`. |
| `LLM_MODEL` | Modelo padrão do provider. |
| `LLM_TEMPERATURE` | Temperatura do modelo. |
| `LLM_MAX_OUTPUT_TOKENS` | Limite de tokens da resposta. |
| `LLM_TIMEOUT_SECONDS` | Timeout das chamadas LLM. |
| `LLM_RETRY_ATTEMPTS` | Tentativas de retry. |
| `LLM_REQUIRE_STRUCTURED_OUTPUT` | Exige saída estruturada para geração. |
| `LLM_FALLBACK_ENABLED` | Permite fallback para mock quando configurado. |
| `LLM_LOG_PROMPT` | Controla logging de prompt. Deve ficar `false` para dados sensíveis. |
| `OPENAI_API_KEY` | Chave da OpenAI. |
| `ANTHROPIC_API_KEY` | Chave da Anthropic/Claude. |
| `OLLAMA_BASE_URL` | URL local do Ollama. |

Exemplo seguro para desenvolvimento:

```env
LLM_REQUIRED=true
LLM_ALLOW_MOCK=true
LLM_ALLOW_CLIENT_PROVIDER=true
LLM_CLIENT_ALLOWED_PROVIDERS=mock,ollama,openai,anthropic
LLM_PROVIDER=mock
LLM_MODEL=
```

Exemplo com Ollama local:

```env
LLM_PROVIDER=ollama
LLM_MODEL=llama3.1:8b
OLLAMA_BASE_URL=http://localhost:11434
```

## Como Executar

API + web:

```bash
uvicorn src.interfaces.api:app --host 127.0.0.1 --port 8000 --reload
```

Abra:

```text
http://127.0.0.1:8000/
```

Documentação interativa da API:

```text
http://127.0.0.1:8000/docs
```

No Windows, se `python` global não estiver no PATH, use o Python da venv:

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.interfaces.api:app --host 127.0.0.1 --port 8000 --reload
```

## Interface Web

A interface web fica em `web/` e é servida pelo próprio FastAPI. Não há build front-end separado nem `package.json`.

Fluxo básico:

1. Acesse `http://127.0.0.1:8000/`.
2. Use a aba **IA** para conversar, anexar arquivos e pedir uma peça.
3. Quando a peça for gerada, baixe o DOCX ou abra o relatório.
4. Use a aba **Peças** para consultar resultados locais.
5. Use a aba **Início** para acompanhar métricas da máquina local.

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
| `POST` | `/api/v1/chat` | Conversa livre com IA local. |
| `POST` | `/api/v1/chat/upload` | Conversa livre com arquivos anexados. |
| `POST` | `/api/v1/documents` | Gera DOCX a partir de texto. |
| `POST` | `/api/v1/documents/upload` | Extrai arquivos e gera DOCX. |
| `GET` | `/api/v1/documents/{filename}/download` | Baixa DOCX gerado. |
| `GET` | `/api/v1/pieces` | Lista peças locais derivadas de relatórios. |
| `GET` | `/api/v1/dashboard` | Métricas operacionais locais. |
| `GET` | `/api/v1/reports` | Lista relatórios locais. |
| `GET` | `/api/v1/reports/{filename}` | Abre relatório JSON ou HTML. |

Criar documento com provider mock:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/documents \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"Cliente relata indeferimento de benefício pelo INSS. Dados fictícios para teste.\",\"output_mode\":\"minuta\",\"llm\":{\"provider\":\"mock\",\"consent_external_provider\":false}}"
```

Upload:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/documents/upload \
  -F "files=@relato.pdf" \
  -F "output_mode=minuta" \
  -F "llm_provider=mock" \
  -F "llm_consent_external_provider=false"
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

Processar exemplo fictício com mock e sem outbox:

```bash
python -m src --inbox examples/inbox_valid.json --no-outbox --mock --report reports/demo_report.json
```

Processar com Ollama:

```bash
python -m src --inbox examples/inbox_valid.json --no-outbox --llm-provider ollama --llm-model llama3.1:8b
```

Validar DOCX gerado:

```bash
python -m src.core.validation.docx output/nome-do-arquivo.docx --profile judicial-inicial-jef
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
docker run --rm -p 8000:8000 -e API_TOKEN=troque-este-token sistema-peticoes
```

O Dockerfile define `API_REQUIRE_TOKEN=1` por padrão. Para acessar rotas sensíveis, use o header `X-API-Token`.

Com volumes para preservar documentos e relatórios:

```bash
docker run --rm -p 8000:8000 \
  -e API_TOKEN=troque-este-token \
  -v ./output:/app/output \
  -v ./reports:/app/reports \
  sistema-peticoes
```

Para demonstração local isolada, é possível desativar explicitamente:

```bash
docker run --rm -p 8000:8000 -e API_REQUIRE_TOKEN=false sistema-peticoes
```

Não use `API_REQUIRE_TOKEN=false` em rede pública.

## Testes E Qualidade

Instale dependências de desenvolvimento:

```bash
pip install -r requirements-dev.txt
```

Validações principais:

```bash
python -m compileall config.py src tests
pytest -q
ruff check .
mypy config.py src/infra/llm
bandit -q -r src
pip-audit -r requirements.txt --strict
```

No Windows, use a venv se necessário:

```powershell
.\.venv\Scripts\python.exe -m compileall config.py src tests
.\.venv\Scripts\python.exe -m pytest -q
```

Observação: a suíte de testes deve rodar em ambiente controlado com provider mock. Se o `.env` local estiver apontando para Ollama ou provider externo, force as variáveis do processo de teste para `LLM_PROVIDER=mock`.

## Segurança E Privacidade

Considere sensíveis:

- `.env`;
- chaves de API;
- `output/*.docx`;
- `reports/*.json`;
- `reports/*.html`;
- arquivos de inbox/outbox/status;
- textos jurídicos e anexos enviados para IA.

Cuidados:

- Use dados fictícios em testes, demonstrações e CI.
- Não versione `.env` real.
- Não envie dados reais a provider externo sem autorização e consentimento.
- Redaction é parcial: CPF, CNPJ, NIT, NB, RG, CEP, telefone e e-mail podem ser mascarados, mas nomes, fatos e contexto sensível podem permanecer.
- Não exponha a API publicamente sem autenticação forte, TLS, autorização, logs controlados e política de retenção.
- Revise sempre mérito, competência, prazo, procuração, valor da causa, anexos e pedidos antes de qualquer uso profissional.

Mais detalhes em [SECURITY.md](SECURITY.md) e [docs/legal-limitations.md](docs/legal-limitations.md).

## Limitações Atuais

- Não substitui advogado nem revisão jurídica humana.
- Não pesquisa jurisprudência em tempo real.
- Não garante tese correta nem aceitação por tribunais.
- Não há banco de dados relacional ou autenticação multiusuário.
- A listagem de peças e o dashboard dependem de arquivos locais de relatório.
- OCR depende de Tesseract configurado no ambiente.
- Chat direto externo ainda não é o fluxo principal; use providers externos principalmente na geração estruturada e com consentimento.
- Gemini/OpenRouter aparecem como chaves de configuração futura, mas não são providers completos implementados no pipeline atual.

## Documentação Complementar

| Documento | Conteúdo |
|---|---|
| [docs/api.md](docs/api.md) | API, payloads e exemplos. |
| [docs/architecture.md](docs/architecture.md) | Arquitetura e fluxo interno. |
| [docs/usage.md](docs/usage.md) | Guia prático de uso. |
| [docs/prompts.md](docs/prompts.md) | Prompts e manutenção. |
| [docs/legal-limitations.md](docs/legal-limitations.md) | Limitações jurídicas e LGPD. |
| [SECURITY.md](SECURITY.md) | Segurança e dados sensíveis. |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribuição. |

## Roadmap

Melhorias futuras coerentes com o estado atual:

- Persistir conversas, peças e métricas em banco de dados.
- Adicionar autenticação e autorização reais.
- Melhorar suporte de chat para providers externos.
- Adicionar paginação, filtros e busca avançada em peças.
- Ampliar validações jurídicas por tipo de peça.
- Evoluir preview visual de DOCX/PDF.
- Adicionar screenshots reais da interface ao repositório.
- Melhorar cobertura de testes do front-end.

## Contribuição

Leia [CONTRIBUTING.md](CONTRIBUTING.md). Contribuições devem preservar:

- revisão humana obrigatória;
- proteção de dados sensíveis;
- uso de dados fictícios em testes;
- testes para mudanças em geração, validação, API, prompts ou segurança.

## Licença

Distribuído sob a licença [MIT](LICENSE).

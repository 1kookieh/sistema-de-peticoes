# Sistema de Petições

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-supervisionado-yellow.svg)]()
[![Tests](https://img.shields.io/badge/tests-65%20passing-brightgreen.svg)](tests)
[![CI](https://github.com/1kookieh/sistema-de-peticoes/actions/workflows/ci.yml/badge.svg)](https://github.com/1kookieh/sistema-de-peticoes/actions/workflows/ci.yml)

Pipeline local em **Python** que transforma texto, PDF, DOCX, MD ou imagem em um
documento `.docx` no padrão forense brasileiro, com **detecção automática do
tipo de peça**, validação determinística antes e depois da geração, perfis
formais por contexto e relatórios de conformidade.

> ⚠️ **Uso jurídico supervisionado.** O sistema reduz trabalho mecânico de
> formatação, mas **não substitui advogado**, não valida mérito, prazo,
> competência ou tese, e não deve ser usado para protocolo sem revisão humana.
> Veja [`docs/legal-limitations.md`](docs/legal-limitations.md).

---

## Sumário

- [Destaques](#destaques)
- [Quick start](#quick-start)
- [Como funciona](#como-funciona)
- [Detecção automática de peça e perfil](#detecção-automática-de-peça-e-perfil)
- [Interfaces disponíveis](#interfaces-disponíveis)
- [Configuração](#configuração)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Testes e CI](#testes-e-ci)
- [Segurança e LGPD](#segurança-e-lgpd)
- [Documentação adicional](#documentação-adicional)
- [Licença](#licença)

---

## Destaques

- **Zero fricção.** Cole o texto, gere o `.docx`. Peça e perfil são opcionais â€”
  o sistema detecta. Padrão `judicial-inicial-jef` (PJE / Projudi) quando nada é
  reconhecido.
- **Quatro entradas suportadas.** Texto colado, upload de `.txt`/`.md`/`.docx`/`.pdf`
  e **OCR de imagem** via Tesseract.
- **Validação dupla.** Pré-validação textual (placeholders, OAB fictícia, dados
  zerados, seções mínimas) + validação do `.docx` gerado (A4, margens, fonte,
  recuos, 7 linhas após endereçamento, OAB).
- **Quatro interfaces.** CLI, API REST local com FastAPI, front-end web em
  HTML/CSS/JS puro e desktop em Tkinter â€” tudo sobre o mesmo pipeline.
- **Relatórios JSON e HTML** por execução, com histórico local navegável.
- **Auditável.** Detector de peça é determinístico (sem LLM no core), perfis
  são tipados, e cada decisão automática é marcada na resposta com flag
  `*_inferred`.
- **Privado.** 100% local. `output/`, `reports/`, `mcp_*.json` no `.gitignore`.
  Política de retenção configurável. `API_TOKEN` opcional na API.
- **Integração com IA.** Trabalha em conjunto com o modelo **Claude** via
  orquestrador externo (MCP, SDK ou Claude Code). Detalhes em
  [`CLAUDE.md`](CLAUDE.md).

---

## Quick start

### Instalação

```bash
git clone https://github.com/1kookieh/sistema-de-peticoes.git
cd sistema-de-peticoes
python -m venv .venv
source .venv/bin/activate            # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env                  # Windows: Copy-Item .env.example .env
```

### Subir API + front-end

```bash
uvicorn src.interfaces.api:app --host 127.0.0.1 --port 8000 --reload
```

Abra **http://127.0.0.1:8000**, cole um texto e clique em **Gerar e validar
DOCX**. O sistema detecta a peça, escolhe o perfil e devolve o `.docx` formatado
com relatório de conformidade.

### Outras formas de rodar

```bash
python -m src --inbox examples/inbox_valid.json --no-outbox    # CLI em lote
python -m src.interfaces.desktop                                          # GUI Tkinter
docker build -t sistema-peticoes . && docker run --rm -p 8000:8000 sistema-peticoes
```

---

## Como funciona

```text
texto / arquivo / imagem
        â”‚
        â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ extração (file_extractors)          â”‚  txt/md/docx/pdf + OCR
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
               â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ infer_piece_type_id (heurística)    â”‚  â†’ tipo de peça
â”‚ resolve perfil (peça â†’ perfil)      â”‚  â†’ fallback judicial-inicial-jef
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
               â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ validar_texto_protocolavel          â”‚  bloqueia placeholders / OAB falsa
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
               â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ formatar_docx.renderizar            â”‚  python-docx + regras forenses
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
               â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ validar (.docx)                     â”‚  reabre e confere o arquivo
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
               â–¼
   output/*.docx + reports/*.{json,html}
```

Falha em qualquer etapa **bloqueia o enfileiramento** e marca o item no
`mcp_status.json` para evitar reprocessamento acidental.

---

## Detecção automática de peça e perfil

Na API e no front-end, **`piece_type_id` e `profile_id` são opcionais**.

| Cenário | O que acontece |
|---|---|
| Usuário não escolhe nada | `infer_piece_type_id` analisa o texto. Sem peça reconhecida â†’ perfil padrão `judicial-inicial-jef` (PJE/Projudi). |
| Usuário escolhe só a peça | Perfil herda o sugerido pela peça (ex.: procuração â†’ `instrumento-mandato`). |
| Usuário escolhe só o perfil | Sistema tenta inferir a peça mesmo assim, para registro no relatório. |
| Usuário escolhe ambos | Inferência é ignorada; valores explícitos prevalecem. |

A resposta inclui `piece_type_inferred: bool` e `profile_inferred: bool` para
auditar o que foi escolhido automaticamente.

**Cobertura do detector** (mais de 70 tipos): procurações, substabelecimentos,
declarações, recursos (inominado, apelação, agravo, embargos, especial, RE,
PEDILEF, CRPS), cumprimento de sentença (RPV, precatório, astreintes),
mandado de segurança, sucessório (inventário, arrolamento, usucapião,
sobrepartilha), administrativos INSS/CRPS, BPC/LOAS, aposentadorias (idade,
tempo, especial, invalidez, híbrida, PCD), auxílios, pensão por morte,
salário-maternidade.

### Perfis formais disponíveis

| Perfil | Uso |
|---|---|
| `judicial-inicial-jef` | Petição inicial JEF / Justiça Federal â€” **padrão (PJE/Projudi)** |
| `judicial-inicial-estadual` | Petição inicial â€” Justiça Estadual |
| `administrativo-inss` | Requerimento, recurso ou manifestação ao INSS / CRPS |
| `extrajudicial-tabelionato` | Requerimentos e minutas para tabelionato |
| `instrumento-mandato` | Procurações, substabelecimentos, declarações |
| `forense-basico` | Validação formal mínima (recursos, manifestações genéricas) |

`GET /api/v1/profiles` devolve `{items, default}` com label PT-BR, exigências
formais (`require_oab`, `require_value_cause`, `required_sections`...) e flag
`is_default` no padrão.

---

## Interfaces disponíveis

| Interface | Comando | Quando usar |
|---|---|---|
| **API REST + web** | `uvicorn src.interfaces.api:app` | Demonstração, uso diário, OCR de imagem. |
| **CLI** | `python -m src` | Processamento em lote, integração via `mcp_inbox.json`. |
| **Desktop** | `python -m src.interfaces.desktop` | Uso local sem navegador, fluxo único. |
| **Direto** | `python -m src.infra.docx_render in.txt out.docx` | Reformatação pontual. |

Endpoints principais (detalhes em [`docs/api.md`](docs/api.md)):

```text
GET    /                                    # front-end
GET    /api/v1/health                          # healthcheck
GET    /api/v1/profiles                        # {items, default}
GET    /api/v1/piece-types                     # catálogo agrupado
GET    /api/v1/limits                          # limites de texto/upload/docx
POST   /api/v1/documents                       # gera por texto colado
POST   /api/v1/documents/upload                # gera por upload (txt, md, docx, pdf, png, jpg, webp)
GET    /api/v1/documents/{file}/download       # baixa o .docx gerado
GET    /api/v1/reports                         # histórico
GET    /api/v1/reports/{file}                  # relatório JSON ou HTML
```

---

## Configuração

Todas as variáveis ficam em `.env` (não versionado). Mínimo viável: nada â€” a
API e o front-end rodam com defaults. Para o fluxo CLI com inbox externa,
defina `EMAIL_ADVOGADO`.

```env
EMAIL_ADVOGADO=advogado-responsavel@example.com
API_TOKEN=                              # se vazio, API local sem auth
VALIDATION_PROFILE=judicial-inicial-jef
REMETENTES_AUTORIZADOS=                 # CSV opcional para filtrar inbox
MAX_JSON_BYTES=2097152

RETENTION_ENABLED=false                 # política de expurgo
RETENTION_OUTPUT_DAYS=30
RETENTION_REPORTS_DAYS=30
RETENTION_QUEUE_DAYS=7
RETENTION_STATUS_DAYS=30
```

`API_TOKEN`, quando definido, exige cabeçalho `X-API-Token` nas rotas de
geração, download e relatórios.

---

## Estrutura do projeto

```text
.
â”œâ”€â”€ CLAUDE.md                  # integração com o modelo Claude
â”œâ”€â”€ README.md
â”œâ”€â”€ CHANGELOG.md
â”œâ”€â”€ LICENSE
â”œâ”€â”€ Dockerfile
â”œâ”€â”€ config.py                  # carga do .env e constantes globais
â”œâ”€â”€ requirements*.txt
â”œâ”€â”€ prompts/                   # prompts versionados (jurídico + formatação)
â”œâ”€â”€ src/
â”‚   â”œâ”€â”€ api.py                 # FastAPI (REST + estáticos)
â”‚   â”œâ”€â”€ cli.py                 # CLI (python -m src)
â”‚   â”œâ”€â”€ desktop.py             # GUI Tkinter
â”‚   â”œâ”€â”€ domain.py              # tipos compartilhados
â”‚   â”œâ”€â”€ piece_types.py         # catálogo + infer_piece_type_id
â”‚   â”œâ”€â”€ profiles.py            # perfis formais tipados
â”‚   â”œâ”€â”€ formatar_docx.py       # geração com python-docx
â”‚   â”œâ”€â”€ validar_docx.py        # validação formal determinística
â”‚   â”œâ”€â”€ file_extractors.py     # extração de texto + OCR
â”‚   â”œâ”€â”€ gmail_reader.py        # leitor de mcp_inbox.json
â”‚   â”œâ”€â”€ gmail_sender.py        # escritor atômico de mcp_outbox.json
â”‚   â”œâ”€â”€ pipeline_state.py      # estado em mcp_status.json
â”‚   â”œâ”€â”€ reporting.py           # relatórios JSON e HTML
â”‚   â”œâ”€â”€ retention.py           # política de expurgo
â”‚   â”œâ”€â”€ setup_runtime.py       # cria pastas locais e checa recursos
â”‚   â””â”€â”€ main.py                # orquestrador interno
â”œâ”€â”€ web/                       # HTML, CSS, JS â€” sem build, sem Node
â”œâ”€â”€ tests/                     # 65 testes (pytest)
â”œâ”€â”€ docs/
â”‚   â”œâ”€â”€ api.md
â”‚   â”œâ”€â”€ architecture.md
â”‚   â””â”€â”€ legal-limitations.md
â””â”€â”€ examples/                  # inbox e .docx fictícios
```

---

## Testes e CI

```bash
pip install -r requirements-dev.txt
pytest -q
python -m compileall config.py src tests
```

Cobertura: parser `.env`, contrato JSON da inbox, formatador, validador,
inferência (26 cenários parametrizados), bloqueio de placeholders, golden
file estrutural, CLI com relatório, retenção em dry-run e modo aplicado,
API local, painel de histórico e relatório HTML.

CI roda em GitHub Actions a cada push e PR (`compileall` + `pytest`).

---

## Segurança e LGPD

Trate como sensível por padrão:

- `output/*.docx` â€” peças geradas
- `reports/*.json` / `reports/*.html` â€” relatórios com metadados
- `mcp_inbox.json`, `mcp_outbox.json`, `mcp_status.json` â€” runtime do pipeline

Esses arquivos ficam no `.gitignore`, mas continuam existindo localmente.
Para uso real:

- Diretório protegido com controle de acesso.
- Política de retenção curta (`RETENTION_*_DAYS`).
- Backups com criptografia.
- `API_TOKEN` se a API for acessada de outra máquina na rede interna.
- **Nunca** publique inbox/outbox/relatórios em repositórios ou issues.
- Demonstrações usam apenas os fixtures em `examples/`.

Detalhes em [`docs/legal-limitations.md`](docs/legal-limitations.md).

---

## Documentação adicional

| Documento | Conteúdo |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | Integração com o modelo Claude, prompts, parâmetros, prompt engineering, casos de uso. |
| [`docs/architecture.md`](docs/architecture.md) | Componentes, fluxos, falhas e segurança. |
| [`docs/api.md`](docs/api.md) | Contratos REST, exemplos `curl`, deploy Docker. |
| [`docs/legal-limitations.md`](docs/legal-limitations.md) | Limites jurídicos, LGPD, revisão humana obrigatória. |
| [`prompts/prompt_peticao.md`](prompts/prompt_peticao.md) | Prompt jurídico mestre (regras, hierarquia, catálogo). |
| [`prompts/prompt_formatacao_word.md`](prompts/prompt_formatacao_word.md) | Padrão Word/DOCX exigido pelo validador. |
| [`CHANGELOG.md`](CHANGELOG.md) | Histórico de versões. |

---

## Licença

Distribuído sob a licença [MIT](LICENSE).


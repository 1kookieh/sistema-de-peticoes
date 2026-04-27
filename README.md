# Sistema de PetiÃ§Ãµes

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-supervisionado-yellow.svg)]()
[![Tests](https://img.shields.io/badge/tests-65%20passing-brightgreen.svg)](tests)
[![CI](https://github.com/1kookieh/sistema-de-peticoes/actions/workflows/ci.yml/badge.svg)](https://github.com/1kookieh/sistema-de-peticoes/actions/workflows/ci.yml)

Pipeline local em **Python** que transforma texto, PDF, DOCX, MD ou imagem em um
documento `.docx` no padrÃ£o forense brasileiro, com **detecÃ§Ã£o automÃ¡tica do
tipo de peÃ§a**, validaÃ§Ã£o determinÃ­stica antes e depois da geraÃ§Ã£o, perfis
formais por contexto e relatÃ³rios de conformidade.

> âš ï¸ **Uso jurÃ­dico supervisionado.** O sistema reduz trabalho mecÃ¢nico de
> formataÃ§Ã£o, mas **nÃ£o substitui advogado**, nÃ£o valida mÃ©rito, prazo,
> competÃªncia ou tese, e nÃ£o deve ser usado para protocolo sem revisÃ£o humana.
> Veja [`docs/legal-limitations.md`](docs/legal-limitations.md).

---

## SumÃ¡rio

- [Destaques](#destaques)
- [Quick start](#quick-start)
- [Como funciona](#como-funciona)
- [DetecÃ§Ã£o automÃ¡tica de peÃ§a e perfil](#detecÃ§Ã£o-automÃ¡tica-de-peÃ§a-e-perfil)
- [Interfaces disponÃ­veis](#interfaces-disponÃ­veis)
- [ConfiguraÃ§Ã£o](#configuraÃ§Ã£o)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Testes e CI](#testes-e-ci)
- [SeguranÃ§a e LGPD](#seguranÃ§a-e-lgpd)
- [DocumentaÃ§Ã£o adicional](#documentaÃ§Ã£o-adicional)
- [LicenÃ§a](#licenÃ§a)

---

## Destaques

- **Zero fricÃ§Ã£o.** Cole o texto, gere o `.docx`. PeÃ§a e perfil sÃ£o opcionais â€”
  o sistema detecta. PadrÃ£o `judicial-inicial-jef` (PJE / Projudi) quando nada Ã©
  reconhecido.
- **Quatro entradas suportadas.** Texto colado, upload de `.txt`/`.md`/`.docx`/`.pdf`
  e **OCR de imagem** via Tesseract.
- **ValidaÃ§Ã£o dupla.** PrÃ©-validaÃ§Ã£o textual (placeholders, OAB fictÃ­cia, dados
  zerados, seÃ§Ãµes mÃ­nimas) + validaÃ§Ã£o do `.docx` gerado (A4, margens, fonte,
  recuos, 7 linhas apÃ³s endereÃ§amento, OAB).
- **Quatro interfaces.** CLI, API REST local com FastAPI, front-end web em
  HTML/CSS/JS puro e desktop em Tkinter â€” tudo sobre o mesmo pipeline.
- **RelatÃ³rios JSON e HTML** por execuÃ§Ã£o, com histÃ³rico local navegÃ¡vel.
- **AuditÃ¡vel.** Detector de peÃ§a Ã© determinÃ­stico (sem LLM no core), perfis
  sÃ£o tipados, e cada decisÃ£o automÃ¡tica Ã© marcada na resposta com flag
  `*_inferred`.
- **Privado.** 100% local. `output/`, `reports/`, `mcp_*.json` no `.gitignore`.
  PolÃ­tica de retenÃ§Ã£o configurÃ¡vel. `API_TOKEN` opcional na API.
- **IntegraÃ§Ã£o com IA.** Trabalha em conjunto com o modelo **Claude** via
  orquestrador externo (MCP, SDK ou Claude Code). Detalhes em
  [`CLAUDE.md`](CLAUDE.md).

---

## Quick start

### InstalaÃ§Ã£o

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
DOCX**. O sistema detecta a peÃ§a, escolhe o perfil e devolve o `.docx` formatado
com relatÃ³rio de conformidade.

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
â”‚ extraÃ§Ã£o (file_extractors)          â”‚  txt/md/docx/pdf + OCR
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
               â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ infer_piece_type_id (heurÃ­stica)    â”‚  â†’ tipo de peÃ§a
â”‚ resolve perfil (peÃ§a â†’ perfil)      â”‚  â†’ fallback judicial-inicial-jef
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

## DetecÃ§Ã£o automÃ¡tica de peÃ§a e perfil

Na API e no front-end, **`piece_type_id` e `profile_id` sÃ£o opcionais**.

| CenÃ¡rio | O que acontece |
|---|---|
| UsuÃ¡rio nÃ£o escolhe nada | `infer_piece_type_id` analisa o texto. Sem peÃ§a reconhecida â†’ perfil padrÃ£o `judicial-inicial-jef` (PJE/Projudi). |
| UsuÃ¡rio escolhe sÃ³ a peÃ§a | Perfil herda o sugerido pela peÃ§a (ex.: procuraÃ§Ã£o â†’ `instrumento-mandato`). |
| UsuÃ¡rio escolhe sÃ³ o perfil | Sistema tenta inferir a peÃ§a mesmo assim, para registro no relatÃ³rio. |
| UsuÃ¡rio escolhe ambos | InferÃªncia Ã© ignorada; valores explÃ­citos prevalecem. |

A resposta inclui `piece_type_inferred: bool` e `profile_inferred: bool` para
auditar o que foi escolhido automaticamente.

**Cobertura do detector** (mais de 70 tipos): procuraÃ§Ãµes, substabelecimentos,
declaraÃ§Ãµes, recursos (inominado, apelaÃ§Ã£o, agravo, embargos, especial, RE,
PEDILEF, CRPS), cumprimento de sentenÃ§a (RPV, precatÃ³rio, astreintes),
mandado de seguranÃ§a, sucessÃ³rio (inventÃ¡rio, arrolamento, usucapiÃ£o,
sobrepartilha), administrativos INSS/CRPS, BPC/LOAS, aposentadorias (idade,
tempo, especial, invalidez, hÃ­brida, PCD), auxÃ­lios, pensÃ£o por morte,
salÃ¡rio-maternidade.

### Perfis formais disponÃ­veis

| Perfil | Uso |
|---|---|
| `judicial-inicial-jef` | PetiÃ§Ã£o inicial JEF / JustiÃ§a Federal â€” **padrÃ£o (PJE/Projudi)** |
| `judicial-inicial-estadual` | PetiÃ§Ã£o inicial â€” JustiÃ§a Estadual |
| `administrativo-inss` | Requerimento, recurso ou manifestaÃ§Ã£o ao INSS / CRPS |
| `extrajudicial-tabelionato` | Requerimentos e minutas para tabelionato |
| `instrumento-mandato` | ProcuraÃ§Ãµes, substabelecimentos, declaraÃ§Ãµes |
| `forense-basico` | ValidaÃ§Ã£o formal mÃ­nima (recursos, manifestaÃ§Ãµes genÃ©ricas) |

`GET /api/v1/profiles` devolve `{items, default}` com label PT-BR, exigÃªncias
formais (`require_oab`, `require_value_cause`, `required_sections`...) e flag
`is_default` no padrÃ£o.

---

## Interfaces disponÃ­veis

| Interface | Comando | Quando usar |
|---|---|---|
| **API REST + web** | `uvicorn src.interfaces.api:app` | DemonstraÃ§Ã£o, uso diÃ¡rio, OCR de imagem. |
| **CLI** | `python -m src` | Processamento em lote, integraÃ§Ã£o via `mcp_inbox.json`. |
| **Desktop** | `python -m src.interfaces.desktop` | Uso local sem navegador, fluxo Ãºnico. |
| **Direto** | `python -m src.infra.docx_render in.txt out.docx` | ReformataÃ§Ã£o pontual. |

Endpoints principais (detalhes em [`docs/api.md`](docs/api.md)):

```text
GET    /                                    # front-end
GET    /api/v1/health                          # healthcheck
GET    /api/v1/profiles                        # {items, default}
GET    /api/v1/piece-types                     # catÃ¡logo agrupado
GET    /api/v1/limits                          # limites de texto/upload/docx
POST   /api/v1/documents                       # gera por texto colado
POST   /api/v1/documents/upload                # gera por upload (txt, md, docx, pdf, png, jpg, webp)
GET    /api/v1/documents/{file}/download       # baixa o .docx gerado
GET    /api/v1/reports                         # histÃ³rico
GET    /api/v1/reports/{file}                  # relatÃ³rio JSON ou HTML
```

---

## ConfiguraÃ§Ã£o

Todas as variÃ¡veis ficam em `.env` (nÃ£o versionado). MÃ­nimo viÃ¡vel: nada â€” a
API e o front-end rodam com defaults. Para o fluxo CLI com inbox externa,
defina `EMAIL_ADVOGADO`.

```env
EMAIL_ADVOGADO=advogado-responsavel@example.com
API_TOKEN=                              # se vazio, API local sem auth
VALIDATION_PROFILE=judicial-inicial-jef
REMETENTES_AUTORIZADOS=                 # CSV opcional para filtrar inbox
MAX_JSON_BYTES=2097152

RETENTION_ENABLED=false                 # polÃ­tica de expurgo
RETENTION_OUTPUT_DAYS=30
RETENTION_REPORTS_DAYS=30
RETENTION_QUEUE_DAYS=7
RETENTION_STATUS_DAYS=30
```

`API_TOKEN`, quando definido, exige cabeÃ§alho `X-API-Token` nas rotas de
geraÃ§Ã£o, download e relatÃ³rios.

---

## Estrutura do projeto

```text
.
â”œâ”€â”€ CLAUDE.md                  # integraÃ§Ã£o com o modelo Claude
â”œâ”€â”€ README.md
â”œâ”€â”€ CHANGELOG.md
â”œâ”€â”€ LICENSE
â”œâ”€â”€ Dockerfile
â”œâ”€â”€ config.py                  # carga do .env e constantes globais
â”œâ”€â”€ requirements*.txt
â”œâ”€â”€ prompts/                   # prompts versionados (jurÃ­dico + formataÃ§Ã£o)
â”œâ”€â”€ src/
â”‚   â”œâ”€â”€ api.py                 # FastAPI (REST + estÃ¡ticos)
â”‚   â”œâ”€â”€ cli.py                 # CLI (python -m src)
â”‚   â”œâ”€â”€ desktop.py             # GUI Tkinter
â”‚   â”œâ”€â”€ domain.py              # tipos compartilhados
â”‚   â”œâ”€â”€ piece_types.py         # catÃ¡logo + infer_piece_type_id
â”‚   â”œâ”€â”€ profiles.py            # perfis formais tipados
â”‚   â”œâ”€â”€ formatar_docx.py       # geraÃ§Ã£o com python-docx
â”‚   â”œâ”€â”€ validar_docx.py        # validaÃ§Ã£o formal determinÃ­stica
â”‚   â”œâ”€â”€ file_extractors.py     # extraÃ§Ã£o de texto + OCR
â”‚   â”œâ”€â”€ gmail_reader.py        # leitor de mcp_inbox.json
â”‚   â”œâ”€â”€ gmail_sender.py        # escritor atÃ´mico de mcp_outbox.json
â”‚   â”œâ”€â”€ pipeline_state.py      # estado em mcp_status.json
â”‚   â”œâ”€â”€ reporting.py           # relatÃ³rios JSON e HTML
â”‚   â”œâ”€â”€ retention.py           # polÃ­tica de expurgo
â”‚   â”œâ”€â”€ setup_runtime.py       # cria pastas locais e checa recursos
â”‚   â””â”€â”€ main.py                # orquestrador interno
â”œâ”€â”€ web/                       # HTML, CSS, JS â€” sem build, sem Node
â”œâ”€â”€ tests/                     # 65 testes (pytest)
â”œâ”€â”€ docs/
â”‚   â”œâ”€â”€ api.md
â”‚   â”œâ”€â”€ architecture.md
â”‚   â””â”€â”€ legal-limitations.md
â””â”€â”€ examples/                  # inbox e .docx fictÃ­cios
```

---

## Testes e CI

```bash
pip install -r requirements-dev.txt
pytest -q
python -m compileall config.py src tests
```

Cobertura: parser `.env`, contrato JSON da inbox, formatador, validador,
inferÃªncia (26 cenÃ¡rios parametrizados), bloqueio de placeholders, golden
file estrutural, CLI com relatÃ³rio, retenÃ§Ã£o em dry-run e modo aplicado,
API local, painel de histÃ³rico e relatÃ³rio HTML.

CI roda em GitHub Actions a cada push e PR (`compileall` + `pytest`).

---

## SeguranÃ§a e LGPD

Trate como sensÃ­vel por padrÃ£o:

- `output/*.docx` â€” peÃ§as geradas
- `reports/*.json` / `reports/*.html` â€” relatÃ³rios com metadados
- `mcp_inbox.json`, `mcp_outbox.json`, `mcp_status.json` â€” runtime do pipeline

Esses arquivos ficam no `.gitignore`, mas continuam existindo localmente.
Para uso real:

- DiretÃ³rio protegido com controle de acesso.
- PolÃ­tica de retenÃ§Ã£o curta (`RETENTION_*_DAYS`).
- Backups com criptografia.
- `API_TOKEN` se a API for acessada de outra mÃ¡quina na rede interna.
- **Nunca** publique inbox/outbox/relatÃ³rios em repositÃ³rios ou issues.
- DemonstraÃ§Ãµes usam apenas os fixtures em `examples/`.

Detalhes em [`docs/legal-limitations.md`](docs/legal-limitations.md).

---

## DocumentaÃ§Ã£o adicional

| Documento | ConteÃºdo |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | IntegraÃ§Ã£o com o modelo Claude, prompts, parÃ¢metros, prompt engineering, casos de uso. |
| [`docs/architecture.md`](docs/architecture.md) | Componentes, fluxos, falhas e seguranÃ§a. |
| [`docs/api.md`](docs/api.md) | Contratos REST, exemplos `curl`, deploy Docker. |
| [`docs/legal-limitations.md`](docs/legal-limitations.md) | Limites jurÃ­dicos, LGPD, revisÃ£o humana obrigatÃ³ria. |
| [`prompts/prompt_peticao.md`](prompts/prompt_peticao.md) | Prompt jurÃ­dico mestre (regras, hierarquia, catÃ¡logo). |
| [`prompts/prompt_formatacao_word.md`](prompts/prompt_formatacao_word.md) | PadrÃ£o Word/DOCX exigido pelo validador. |
| [`CHANGELOG.md`](CHANGELOG.md) | HistÃ³rico de versÃµes. |

---

## LicenÃ§a

DistribuÃ­do sob a licenÃ§a [MIT](LICENSE).


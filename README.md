# Sistema de Petições

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-ativo-brightgreen.svg)]()
[![CI](https://github.com/1kookieh/sistema-de-peticoes/actions/workflows/ci.yml/badge.svg)](https://github.com/1kookieh/sistema-de-peticoes/actions/workflows/ci.yml)

Pipeline em Python que gera peças jurídicas em `.docx` no **padrão forense brasileiro** a partir de texto simples. O sistema formata, valida automaticamente e entrega o documento pronto para protocolo — sem dependência de APIs pagas, usando apenas `python-docx`.

> **Destaques técnicos:** pipeline autossuficiente (formata → valida → autocorrige), validador determinístico de regras ABNT/forenses, arquitetura modular orientada a filas (inbox/outbox JSON) e integração opcional com e-mail via orquestrador externo.

---

## Sumário

- [Objetivo](#objetivo)
- [Contexto](#contexto)
- [Visão geral do fluxo](#visão-geral-do-fluxo)
- [Funcionalidades](#funcionalidades)
- [Tecnologias](#tecnologias)
- [Instalação](#instalação)
- [Como executar](#como-executar)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Arquitetura](#arquitetura)
- [Decisões técnicas](#decisões-técnicas)
- [Desafios](#desafios)
- [Aprendizados](#aprendizados)
- [Melhorias futuras](#melhorias-futuras)
- [Como contribuir](#como-contribuir)
- [Licença](#licença)
- [Contato](#contato)

---

## Objetivo

Automatizar a etapa mecânica da produção de peças jurídicas — formatação em padrão forense, conferência de margens, fontes, alinhamentos e elementos obrigatórios — para que o advogado dedique 100% do tempo ao conteúdo jurídico. A meta é eliminar o retrabalho com Word, garantir uniformidade visual em todo o escritório e produzir documentos prontos para protocolo em qualquer tribunal brasileiro.

## Contexto

O projeto nasceu de uma dor real observada em escritórios de advocacia de pequeno/médio porte: cada advogado acaba aplicando manualmente regras de formatação (margens 3/3/2/2 cm, Times New Roman 12, recuo 2,5 cm, 7 linhas após o endereçamento, negrito restrito a elementos específicos) e erros sutis passam despercebidos até a devolução pela secretaria ou pelo próprio juízo. O `Sistema de Petições` codifica essas regras em Python puro, transformando uma checklist informal em pipeline determinístico.

## Visão geral do fluxo

```
   Texto da peça (stdin / JSON / e-mail)
                  │
                  ▼
   ┌──────────────────────────────┐
   │ src/formatar_docx.py         │  Aplica padrão forense:
   │  A4 · TNR 12 · 3/3/2/2cm     │  margens, fonte, recuo,
   │  justificado · 1,5 entre     │  negrito, centralizações,
   │  linhas · recuo 2,5 cm       │  7 linhas após vara.
   └──────────────┬───────────────┘
                  ▼
   ┌──────────────────────────────┐
   │ src/validar_docx.py          │  Verificação determinística:
   │  margens · fontes · OAB      │  margens, fontes, alinhamento,
   │  7 linhas · alinhamentos     │  vara centralizada, OAB, etc.
   └──────────────┬───────────────┘
                  ▼
   .docx pronto em `output/` + relatório de conformidade
```

---

## Funcionalidades

- **Formatação forense/ABNT automática** — `src/formatar_docx.py` aplica:
  A4, margens 3/3/2/2 cm, Times New Roman 12, justificado, 1,5 entre linhas, recuo 2,5 cm, 7 linhas em branco após o endereçamento, negrito restrito aos elementos autorizados, nome e OAB centralizados sem linha de assinatura.
- **Validador determinístico** — `src/validar_docx.py` relê o `.docx` gerado e verifica margens, fontes, alinhamentos, presença da OAB no fechamento e ausência de linhas de assinatura. Retorna lista de violações por item, permitindo loops de autocorreção.
- **Arquitetura orientada a filas** — `mcp_inbox.json` de entrada e `mcp_outbox.json` de saída desacoplam a produção do texto (humano ou integrador externo) da formatação, permitindo integrar qualquer fonte de dados.
- **Prompts customizáveis** — `prompts/prompt_peticao.md` (regras jurídicas) e `prompts/prompt_formatacao_word.md` (regras de formatação) ficam versionados e são editáveis sem tocar no código.
- **Zero dependências pagas** — apenas `python-docx`. Sem chamadas a APIs de LLM pagas.
- **Exit codes semânticos** — `0` sucesso, `1` falha, `2` configuração ausente, `3` gerado com violações (ideal para pipelines de CI/CD).

---

## Tecnologias

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.11+ |
| Geração de Word | [`python-docx`](https://python-docx.readthedocs.io/) |
| Validação | Módulo próprio sobre `python-docx` (regras determinísticas) |
| Configuração | `.env` (loader nativo, sem `python-dotenv`) |
| Entrega | Filas JSON locais (`mcp_inbox.json` / `mcp_outbox.json`) |
| CI | GitHub Actions (lint + compile) |

---

## Instalação

### Pré-requisitos

- **Python 3.11 ou superior**
- **Git**

### 1. Clone o repositório

```bash
git clone https://github.com/1kookieh/sistema-de-peticoes.git
cd sistema-de-peticoes
```

### 2. Crie um ambiente virtual e instale dependências

**Windows (PowerShell):**
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Windows (bash / Git Bash):**
```bash
py -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure variáveis de ambiente

```bash
cp .env.example .env
```

Edite `.env` com o e-mail do advogado responsável pelas peças:

```
EMAIL_ADVOGADO=seu-email@exemplo.com
```

### 4. Configure os advogados do escritório

Em `prompts/prompt_peticao.md`, substitua os placeholders:

```
[NOME COMPLETO DO ADVOGADO 1] — OAB/UF 00.000
[NOME COMPLETO DO ADVOGADO 2] — OAB/UF 00.000
```

pelos nomes e números da OAB reais. Esses advogados assinarão as peças geradas.

---

## Como executar

### Teste local

O arquivo `teste_inbox.json` acompanha o projeto. Basta apontar o pipeline para ele:

**bash:**
```bash
export INBOX_MOCK_PATH=./teste_inbox.json
python -m src.main
```

**PowerShell:**
```powershell
$env:INBOX_MOCK_PATH = ".\teste_inbox.json"
python -m src.main
```

Saída esperada:
```
1 e-mail(s) pendente(s).
[+] teste_001 - 'Petição inicial - ...'
    docx -> peticao_YYYYMMDD_HHMMSS_teste_00.docx
    [VALIDACAO] OK

Concluido. Sucessos: 1 | Falhas: 0 | Violacoes: 0
```

O `.docx` aparece em `output/` e o envio fica enfileirado em `mcp_outbox.json`.

### Formatação direta a partir de um arquivo de texto

```bash
python -m src.formatar_docx peticao.txt output/peticao.docx
python -m src.formatar_docx - output/peticao.docx < texto.txt
```

### Validação de um `.docx` existente

```bash
python -m src.validar_docx output/peticao.docx
```

Retorna `OK` ou a lista de violações encontradas (margens, fontes, alinhamentos, OAB, etc.).

### Exit codes

| Código | Significado |
|---|---|
| 0 | Tudo OK |
| 1 | Falha em um ou mais itens |
| 2 | Configuração ausente (`EMAIL_ADVOGADO`) |
| 3 | Gerado, mas com violações de formatação |

---

## Estrutura do projeto

```
.
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   ├── workflows/
│   │   ├── ci.yml                     # Lint + compile em cada push/PR
│   │   └── processar_peticoes.yml     # Execução manual do pipeline
│   └── pull_request_template.md
├── docs/
│   ├── architecture.md                # Visão técnica detalhada
│   ├── decisions.md                   # Registro de decisões (ADR light)
│   ├── roadmap.md                     # Próximos passos
│   └── recruiter-notes.md             # Notas curtas para recrutadores/techs
├── prompts/
│   ├── prompt_peticao.md              # Regras jurídicas (23 seções) + advogados
│   └── prompt_formatacao_word.md      # Regras de formatação Word
├── src/
│   ├── __init__.py
│   ├── main.py                        # Orquestrador: lê inbox → formata → valida → enfileira
│   ├── gmail_reader.py                # Desserializa mcp_inbox.json
│   ├── gmail_sender.py                # Grava mcp_outbox.json
│   ├── formatar_docx.py               # Texto → .docx padrão forense
│   └── validar_docx.py                # Valida o .docx gerado
├── output/                            # .docx gerados (gitignored)
├── config.py                          # Loader de .env + paths
├── requirements.txt                   # python-docx
├── teste_inbox.json                   # Exemplo para testes locais
├── CHANGELOG.md
├── CONTRIBUTING.md
├── .env.example
├── .gitignore
├── LICENSE                            # MIT
└── README.md
```

---

## Arquitetura

Três camadas independentes, comunicando-se por JSON em disco:

1. **Ingestão** (`gmail_reader.py`): lê `mcp_inbox.json` (ou `INBOX_MOCK_PATH` para testes). Cada item é uma `Email` dataclass com `peticao_texto` já redigido.
2. **Processamento** (`formatar_docx.py` + `validar_docx.py`): o formatador transforma texto plano em `.docx` aplicando o padrão forense; o validador relê o arquivo e retorna violações determinísticas.
3. **Entrega** (`gmail_sender.py`): serializa a resposta (com o `.docx` em base64) em `mcp_outbox.json`. Um integrador externo consome essa fila para o envio real.

O orquestrador (`main.py`) costura os três estágios e produz um relatório no stdout. Para detalhes ver [`docs/architecture.md`](docs/architecture.md).

---

## Decisões técnicas

- **`python-docx` em vez de templating Word/Jinja** — controle granular sobre runs, parágrafos e estilos; essencial para negrito seletivo e recuos de parágrafo.
- **Filas JSON em vez de chamar Gmail direto** — o módulo Python fica testável offline e agnóstico ao canal de entrega.
- **Validador separado do formatador** — o formatador pode ter bugs; o validador é a rede de segurança independente. Dois processos reduzem acoplamento e permitem loops de autocorreção.
- **Loader `.env` caseiro, sem `python-dotenv`** — mantém o projeto com uma única dependência (`python-docx`).
- **Prompts em Markdown versionado** — mudança de regra jurídica = diff no repo, sem deploy.

Detalhes em [`docs/decisions.md`](docs/decisions.md).

---

## Desafios

- Traduzir regras tácitas de formatação forense ("negrito só em elementos autorizados") em verificações determinísticas sem falso-positivos.
- Lidar com heterogeneidade do texto de entrada (quebra de linha, acentos, parágrafos colados) e ainda produzir estrutura fiel ao padrão.
- Manter a API do `python-docx` sob controle — a biblioteca expõe muita complexidade XML abaixo da camada de objetos.

## Aprendizados

- Como funciona internamente um `.docx` (OOXML, `w:pPr`, `w:rPr`) e como regras visuais mapeiam para propriedades de parágrafo/run.
- Desenho de pipelines idempotentes com exit codes acionáveis por CI.
- Valor de separar geração e validação como processos distintos — espelha o conceito de "oráculo" em testes.

---

## Melhorias futuras

- Suporte a anexos embarcados (documentos do processo)
- Export em `.pdf` direto (mantendo o mesmo pipeline)
- Plugin para ingestão via API REST (FastAPI)
- Cobertura de testes automatizada (pytest + golden files)
- Métricas de qualidade (quantas peças passam em todas as validações na primeira tentativa)

Roadmap completo em [`docs/roadmap.md`](docs/roadmap.md).

---

## Como contribuir

Contribuições são muito bem-vindas! Veja [`CONTRIBUTING.md`](CONTRIBUTING.md) para o fluxo de branches, padrão de commits (Conventional Commits) e checklist de PR.

---

## Licença

Distribuído sob a licença [MIT](LICENSE). Use à vontade — atribuição é apreciada.

---

## Contato

**Kaká (1kookieh)**
GitHub: [@1kookieh](https://github.com/1kookieh)
Projeto: [github.com/1kookieh/sistema-de-peticoes](https://github.com/1kookieh/sistema-de-peticoes)

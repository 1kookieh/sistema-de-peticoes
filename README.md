# Sistema de Petições

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-ativo-brightgreen.svg)]()

Pipeline em Python que gera peças jurídicas em `.docx` no **padrão forense brasileiro** a partir de texto simples. O sistema formata, valida automaticamente e entrega o documento pronto para protocolo — sem dependência de APIs pagas, usando apenas `python-docx`.

> **Destaques técnicos:** pipeline autossuficiente (formata → valida → autocorrige), validador determinístico de regras ABNT/forenses, arquitetura modular orientada a filas (inbox/outbox JSON) e integração opcional com e-mail via assistentes MCP.

---

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

## Recursos

- **Formatação forense/ABNT automática** — `src/formatar_docx.py` aplica:
  A4, margens 3/3/2/2 cm, Times New Roman 12, justificado, 1,5 entre linhas, recuo 2,5 cm, 7 linhas em branco após o endereçamento, negrito restrito aos elementos autorizados, nome e OAB centralizados sem linha de assinatura.
- **Validador determinístico** — `src/validar_docx.py` relê o `.docx` gerado e verifica margens, fontes, alinhamentos, presença da OAB no fechamento e ausência de linhas de assinatura. Retorna lista de violações por item, permitindo loops de autocorreção.
- **Arquitetura orientada a filas** — `mcp_inbox.json` de entrada e `mcp_outbox.json` de saída desacoplam a produção do texto (humano ou agente externo) da formatação, permitindo integrar qualquer fonte de dados.
- **Prompts customizáveis** — `prompts/prompt_peticao.md` (regras jurídicas) e `prompts/prompt_formatacao_word.md` (regras de formatação) ficam versionados e são editáveis sem tocar no código.
- **Zero dependências pagas** — apenas `python-docx`. Sem chamadas a APIs de LLM.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.11+ |
| Geração de Word | `python-docx` |
| Validação | Módulo próprio sobre `python-docx` (regras determinísticas) |
| Configuração | `.env` (loader nativo, sem `python-dotenv`) |
| Entrega | Filas JSON locais (`mcp_inbox.json` / `mcp_outbox.json`) |

---

## Pré-requisitos

- **Python 3.11 ou superior**
- **Git**

---

## Instalação

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

## Uso

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

---

## Estrutura do projeto

```
.
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
├── .env.example
├── .gitignore
├── LICENSE                            # MIT
└── README.md
```

---

## Contrato do `mcp_inbox.json`

Cada item representa uma peça a ser formatada:

```json
[
  {
    "thread_id": "abc123",
    "message_id": "msg1",
    "remetente": "seu-email@exemplo.com",
    "assunto": "Petição inicial — caso Silva x Souza",
    "peticao_texto": "EXCELENTÍSSIMO SENHOR...\n\nI - DOS FATOS\n..."
  }
]
```

- `peticao_texto` contém o texto completo da peça.
- Linhas em branco separam blocos (endereçamento, título, seções, fechamento).
- Parágrafos do mesmo bloco são separados por quebra simples.

---

## Regras de formatação aplicadas

| Item | Regra |
|---|---|
| Papel | A4 |
| Margens | 3 / 3 / 2 / 2 cm (sup / esq / inf / dir) |
| Fonte | Times New Roman 12, preto |
| Alinhamento | Justificado (corpo); centralizado (endereçamento, título, nome e OAB) |
| Espaçamento | 1,5 entre linhas; 0 pt antes/depois |
| Recuo 1ª linha | 2,5 cm nos parágrafos corridos |
| Após endereçamento | 7 linhas em branco obrigatórias |
| Negrito | Endereçamento, título, seções (DOS FATOS, DO DIREITO, etc.), marcadores `a) b) c)`, nome e OAB |
| Fechamento | Nome do advogado e OAB em linhas separadas, centralizadas, sem linha de assinatura |

Regras completas em [`prompts/prompt_formatacao_word.md`](prompts/prompt_formatacao_word.md).

---

## Testes

Execução do pipeline ponta a ponta com o inbox de exemplo:

```bash
INBOX_MOCK_PATH=./teste_inbox.json python -m src.main
python -m src.validar_docx output/peticao_*.docx
```

Um sucesso produz exit code `0`. Exit codes:

| Código | Significado |
|---|---|
| 0 | Tudo OK |
| 1 | Falha em um ou mais itens |
| 2 | Configuração ausente (`EMAIL_ADVOGADO`) |
| 3 | Gerado, mas com violações de formatação |

---

## Roadmap

- [ ] Suporte a anexos embarcados (documentos do processo)
- [ ] Export em `.pdf` direto (mantendo o mesmo pipeline)
- [ ] Plugin para ingestão via API REST (FastAPI)
- [ ] Cobertura de testes automatizada (pytest)

---

## Licença

[MIT](LICENSE)

# Sistema de Petições

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-supervisionado-yellow.svg)]()
[![CI](https://github.com/1kookieh/sistema-de-peticoes/actions/workflows/ci.yml/badge.svg)](https://github.com/1kookieh/sistema-de-peticoes/actions/workflows/ci.yml)

Pipeline em Python para transformar texto de peças jurídicas em `.docx` com formatação forense padronizada, validação determinística e filas JSON locais. O sistema ajuda a reduzir retrabalho mecânico de Word, mas não substitui advogado, não valida mérito jurídico complexo e não deve ser usado para protocolo sem revisão humana.

**Stack principal:** Python 3.11+, FastAPI, Uvicorn, python-docx, Pytest, HTML, CSS, JavaScript, Tkinter e Docker.

## O Que Faz

- Formata texto em `.docx` com A4, margens 3/3/2/2 cm, Times New Roman 12, corpo justificado, espaçamento 1,5, recuo de 2,5 cm e 7 linhas após o endereçamento.
- Valida o `.docx` gerado quanto a regras formais: página, margens, fonte, endereçamento, OAB, local/data, assinatura gráfica e placeholders.
- Bloqueia o enfileiramento quando encontra violação formal ou entrada com dados de exemplo.
- Lê uma fila local `mcp_inbox.json` ou `INBOX_MOCK_PATH` e grava respostas em `mcp_outbox.json`.
- Mantém estado local em `mcp_status.json` para evitar reprocessamento acidental de itens já concluídos.
- Permite perfis formais por contexto, relatório JSON de conformidade e execução sem outbox.
- Expõe API REST local com FastAPI para setup, geração, download e consulta de relatórios.
- Inclui front-end local em HTML, CSS e JavaScript puro para upload de `.txt`, geração de `.docx`, download e histórico.
- Oferece interface desktop em Tkinter para uso local sem navegador.
- Gera relatórios JSON e HTML de conformidade formal para revisão humana.
- Inclui `Dockerfile` para executar a API/front-end em ambiente reprodutível.
- Possui política configurável de retenção para arquivos locais sensíveis.
- Inclui testes automatizados com `pytest`.

## Tecnologias Utilizadas

| Área | Tecnologia | Onde aparece |
|---|---|---|
| Linguagem principal | Python 3.11+ | `src/`, CLI, API, validações e geração `.docx` |
| Documentos Word | `python-docx` | `src/formatar_docx.py`, `src/validar_docx.py`, `src/reporting.py` |
| API REST | FastAPI | `src/api.py` |
| Servidor local | Uvicorn | execução de `uvicorn src.api:app --reload` |
| Front-end | HTML, CSS e JavaScript puro | `web/index.html`, `web/styles.css`, `web/app.js` |
| Interface desktop | Tkinter | `src/desktop.py` |
| Testes | Pytest e FastAPI TestClient | `tests/` |
| Container | Docker | `Dockerfile`, `.dockerignore` |

O front-end foi mantido sem React/Vite/Next.js de propósito: para este escopo, HTML/CSS/JS puro entrega upload, geração, download e histórico sem exigir Node.js, build ou dependências extras.

## Primeiro Uso

Prepare as pastas locais e verifique recursos essenciais:

```bash
python -m src --setup
```

O comando cria `output/` e `reports/` com `.gitkeep`, confere arquivos básicos do projeto e mostra próximos passos. Os documentos e relatórios reais continuam ignorados pelo Git.

Se preferir avaliar sem linha de comando, rode a API local e abra o front-end no navegador:

```bash
uvicorn src.api:app --reload
```

Depois acesse `http://127.0.0.1:8000`. A interface web usa HTML, CSS e JavaScript puro para evitar build obrigatório, dependências de Node e complexidade desnecessária para um projeto local.

## Demonstração Segura

Este repositório não deve expor peças reais, dados de clientes ou documentos sensíveis. Para avaliar o fluxo sem risco, use `examples/inbox_valid.json` ou `teste_inbox.json`, sempre com dados fictícios.

- Roteiro de demonstração: [docs/demo.md](docs/demo.md)
- API REST e interfaces locais: [docs/api.md](docs/api.md)
- Estudo de caso técnico: [docs/case-study.md](docs/case-study.md)
- Limitações jurídicas e LGPD: [docs/legal-limitations.md](docs/legal-limitations.md)
- Documento fictício já gerado: `examples/generated-docx/peticao_exemplo.docx`

## O Que Não Faz

- Não declara que uma peça está juridicamente pronta para protocolo.
- Não substitui conferência de advogado com OAB ativa e poderes nos autos.
- Não verifica automaticamente competência, rito, prazo, tese, jurisprudência atualizada ou regras locais de tribunal.
- Não consulta APIs pagas nem gera mérito jurídico definitivo.
- Não elimina a necessidade de revisar dados pessoais, documentos, cálculo, valor da causa e pedidos.

## Aviso Jurídico e LGPD

Peças jurídicas podem conter dados pessoais, dados sensíveis, informações médicas, dados previdenciários e elementos protegidos por sigilo profissional. Os arquivos abaixo são dados de runtime e devem ser tratados como sensíveis:

- `output/*.docx`
- `reports/*.json`
- `reports/*.html`
- `mcp_inbox.json`
- `mcp_outbox.json`
- `mcp_status.json`

Esses arquivos são ignorados pelo Git, mas continuam existindo localmente. Em ambiente real, use diretório protegido, controle de acesso, retenção curta, backups seguros e revisão humana obrigatória antes de envio ou protocolo.

## Instalação

```bash
git clone https://github.com/1kookieh/sistema-de-peticoes.git
cd sistema-de-peticoes
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

No Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Para desenvolvimento e testes:

```bash
pip install -r requirements-dev.txt
```

## Configuração

O projeto usa um arquivo `.env` local para configuração de execução. Esse arquivo não deve ser versionado, porque pode conter e-mails, caminhos e políticas internas de uso.

Configuração mínima:

```env
EMAIL_ADVOGADO=advogado-responsavel@example.com
```

Crie um `.env` local apenas na sua máquina quando necessário. Esse arquivo é ignorado pelo Git e não deve conter dados reais em exemplos públicos.

Configurações opcionais:

```env
REMETENTES_AUTORIZADOS=cliente1@example.com,cliente2@example.com
MAX_JSON_BYTES=2097152
GMAIL_LABEL_PROCESSADO=peticao-gerada
VALIDATION_PROFILE=judicial-inicial-jef
RETENTION_ENABLED=false
RETENTION_OUTPUT_DAYS=30
RETENTION_QUEUE_DAYS=7
RETENTION_STATUS_DAYS=30
```

`EMAIL_ADVOGADO` identifica o responsável pela revisão humana. `REMETENTES_AUTORIZADOS`, quando definido, filtra a inbox por e-mails exatos de remetentes permitidos.

## Perfis de Validação

Liste os perfis disponíveis:

```bash
python -m src --list-profiles
```

Perfis atuais:

| Perfil | Uso |
|---|---|
| `judicial-inicial-jef` | Petição inicial judicial no JEF ou Justiça Federal |
| `judicial-inicial-estadual` | Petição inicial judicial na Justiça Estadual |
| `administrativo-inss` | Requerimento, recurso ou manifestação administrativa |
| `extrajudicial-tabelionato` | Requerimento ou minuta extrajudicial |
| `forense-basico` | Validação formal mínima |

O perfil padrão vem de `VALIDATION_PROFILE`. Também é possível informar por CLI com `--profile`.

## Como Executar

### Fluxo de exemplo

```bash
export INBOX_MOCK_PATH=./examples/inbox_valid.json
python -m src.main
```

Também é possível usar a CLI dedicada:

```bash
python -m src --inbox ./examples/inbox_valid.json --profile judicial-inicial-jef
```

PowerShell:

```powershell
$env:INBOX_MOCK_PATH = ".\examples\inbox_valid.json"
python -m src.main
```

Saída esperada:

```text
1 e-mail(s) pendente(s).
[+] Processando thread teste_001
    docx -> peticao_YYYYMMDD_HHMMSS_xxxxxx_teste_001.docx
    [VALIDACAO] OK

Concluido. Enfileirados: 1 | Bloqueados: 0 | Falhas: 0 | Violacoes: 0 | Ignorados: 0 | Validos: 1
```

### Formatar um texto diretamente

```bash
python -m src.formatar_docx peticao.txt output/peticao.docx
python -m src.formatar_docx - output/peticao.docx < texto.txt
```

### Validar um `.docx`

```bash
python -m src.validar_docx output/peticao.docx
python -m src.validar_docx output/peticao.docx --profile judicial-inicial-jef
```

O validador retorna `OK` ou uma lista de violações formais. Essa validação não equivale a revisão jurídica de mérito.

### API REST e front-end local

```bash
uvicorn src.api:app --reload
```

Depois abra:

```text
http://127.0.0.1:8000
```

Endpoints principais:

| Método | Rota | Uso |
|---|---|---|
| `GET` | `/` | Abre o front-end local |
| `GET` | `/api/health` | Verifica se a API está ativa |
| `GET` | `/api/profiles` | Lista perfis de validação |
| `POST` | `/api/documents` | Gera e valida `.docx` a partir de texto |
| `GET` | `/api/documents/{arquivo}/download` | Baixa documento gerado |
| `GET` | `/api/reports` | Lista histórico local de relatórios |
| `GET` | `/api/reports/{arquivo}` | Abre relatório JSON ou HTML |

O front-end permite colar texto, carregar `.txt`, gerar o `.docx`, baixar o documento e abrir o relatório HTML. Ele é uma camada local de conveniência; a validação jurídica humana continua obrigatória.

Arquivos da interface web:

| Arquivo | Responsabilidade |
|---|---|
| `web/index.html` | Estrutura visual do formulário, resultado e painel de histórico |
| `web/styles.css` | Layout responsivo, identidade visual e estados de aviso |
| `web/app.js` | Carrega perfis, lê `.txt`, chama a API, exibe downloads e atualiza histórico |

O JavaScript escapa conteúdo retornado pela API antes de renderizar informações dinâmicas, reduzindo risco de injeção HTML mesmo em uso local.

### Interface desktop

```bash
python -m src.desktop
```

A interface desktop usa Tkinter, disponível na biblioteca padrão do Python, e aciona o mesmo pipeline da CLI/API. É útil para demonstração local ou uso supervisionado sem navegador.

### Docker

```bash
docker build -t sistema-peticoes .
docker run --rm -p 8000:8000 sistema-peticoes
```

Depois abra `http://127.0.0.1:8000`. Em uso real, monte volumes protegidos para `output/` e `reports/`, porque esses diretórios podem conter dados sensíveis.

Exemplo com volumes locais:

```bash
docker run --rm -p 8000:8000 \
  -v ./output:/app/output \
  -v ./reports:/app/reports \
  sistema-peticoes
```

## Contrato da Inbox

`mcp_inbox.json` deve ser uma lista JSON. Cada item precisa conter:

```json
{
  "thread_id": "thread_001",
  "message_id": "msg_001",
  "remetente": "cliente@example.com",
  "assunto": "Pedido de petição",
  "peticao_texto": "Texto final da peça..."
}
```

O pipeline rejeita JSON inválido, campos obrigatórios ausentes, campos vazios, `message_id` duplicado e arquivos acima de `MAX_JSON_BYTES`.

## Validações e Bloqueios

Antes de gerar/enfileirar, o sistema bloqueia entradas com:

- texto vazio;
- placeholders como `[DADO FALTANTE]`, `[CIDADE]`, `[UF]` ou `NOME DO REQUERENTE`;
- OAB em formato fictício como `OAB/UF 00.000`;
- CPF/NIT zerado;
- ausência de endereçamento, fechamento ou OAB reconhecida;
- petição inicial sem seções mínimas como `DOS FATOS`, `DO DIREITO`, `DOS PEDIDOS` e `DO VALOR DA CAUSA`.

Depois da geração, o `.docx` é reaberto e validado. Se houver violação, o documento não é enfileirado para envio.

## CLI Dedicada

```bash
python -m src --inbox ./examples/inbox_valid.json --strict --report reports/conformidade_report.json --no-outbox
```

Flags principais:

| Flag | Efeito |
|---|---|
| `--profile` | Seleciona o perfil formal de validação |
| `--strict` | Retorna falha quando nenhum documento novo válido é produzido |
| `--report` | Grava relatório JSON com resumo, itens e estrutura do `.docx` |
| `--no-outbox` | Gera e valida sem escrever `mcp_outbox.json` |
| `--apply-retention` | Remove arquivos que excedem a política de retenção |
| `--cleanup-only` | Executa apenas a política de retenção |

Relatórios podem conter identificadores de threads e caminhos de documentos. Trate `reports/`, `*_report.json` e `*.html` gerados em runtime como dados sensíveis.

## Relatórios e Histórico Local

O sistema pode produzir dois formatos de relatório:

| Formato | Saída | Uso recomendado |
|---|---|---|
| JSON | `reports/*.json` | Auditoria técnica, integração e testes automatizados |
| HTML | `reports/*.html` | Leitura humana rápida pelo front-end ou navegador |

O painel local em `GET /api/reports` lista relatórios existentes e itens do status local. Esse histórico é útil para demonstração e conferência operacional, mas não deve ser publicado quando houver dados reais.

## Retenção e Expurgo

A retenção fica desligada por padrão. Para ver candidatos sem apagar:

```bash
python -m src --cleanup-only
```

Para aplicar a política configurada:

```bash
python -m src --cleanup-only --apply-retention
```

Variáveis:

| Variável | Padrão | Efeito |
|---|---:|---|
| `RETENTION_OUTPUT_DAYS` | `30` | Remove `.docx` antigos em `output/` |
| `RETENTION_QUEUE_DAYS` | `7` | Remove inbox/outbox antigas |
| `RETENTION_STATUS_DAYS` | `30` | Remove `mcp_status.json` antigo |

## Exit Codes

| Código | Significado |
|---|---|
| 0 | Execução concluída sem falhas bloqueantes |
| 1 | Falha técnica ou erro de leitura/processamento |
| 2 | Configuração obrigatória ausente |
| 3 | Uma ou mais peças foram bloqueadas por violações formais |

## Testes

```bash
pip install -r requirements-dev.txt
python -m compileall config.py src tests
pytest -q
```

A suíte cobre `.env`, contrato JSON, formatador `.docx`, validador, entradas inválidas, acentos, assinatura indevida, bloqueio de outbox, API local, relatório HTML e setup de runtime.

Também há golden file estrutural em `tests/golden/`. Ele compara propriedades do documento, como A4, margens, fontes, quantidade de linhas após endereçamento e seções obrigatórias, sem depender de comparação binária do `.docx`.

## Fluxo Recomendado Para Uso Supervisionado

1. Redigir ou revisar o texto base fora do pipeline.
2. Garantir que não existam placeholders, dados fictícios ou lacunas críticas.
3. Rodar `python -m src.main` ou `python -m src.formatar_docx`.
4. Rodar `python -m src.validar_docx output/arquivo.docx`.
5. Abrir o `.docx` no Word/LibreOffice e conferir visualmente.
6. Revisar mérito jurídico, competência, rito, prazo, documentos, pedidos, valor da causa, assinatura e procuração.
7. Só protocolar após aprovação expressa do advogado responsável.

## Estrutura

```text
.
├── config.py
├── requirements.txt
├── requirements-dev.txt
├── teste_inbox.json
├── Dockerfile
├── examples/
│   ├── inbox_invalid.json
│   ├── inbox_valid.json
│   └── generated-docx/
│       └── peticao_exemplo.docx
├── prompts/
├── docs/
│   ├── api.md
│   ├── architecture.md
│   ├── demo.md
│   └── legal-limitations.md
├── src/
│   ├── api.py
│   ├── cli.py
│   ├── desktop.py
│   ├── domain.py
│   ├── formatar_docx.py
│   ├── gmail_reader.py
│   ├── gmail_sender.py
│   ├── main.py
│   ├── pipeline_state.py
│   ├── profiles.py
│   ├── reporting.py
│   ├── retention.py
│   ├── setup_runtime.py
│   └── validar_docx.py
├── tests/
├── web/
│   ├── app.js
│   ├── index.html
│   └── styles.css
└── .github/
```

## O que este projeto demonstra

- Capacidade de transformar um problema real de escritório jurídico em pipeline simples, testável e auditável.
- Separação clara entre geração mecânica, validação formal e revisão jurídica humana.
- Uso de contratos JSON, exit codes, CI, testes automatizados e documentação técnica para reduzir risco operacional.
- Atenção a LGPD, dados sensíveis, versionamento profissional e experiência de avaliação por recrutadores.

## Limitações Conhecidas

- O padrão forense brasileiro não é universal; tribunais, ritos, classes processuais e sistemas de protocolo podem exigir ajustes.
- A validação jurídica de mérito permanece humana.
- O parser de texto usa heurísticas, não um modelo semântico completo de todos os tipos de peça.
- `mcp_outbox.json` armazena anexo em base64 para compatibilidade com integradores externos; trate o arquivo como sensível.
- Veja também [docs/legal-limitations.md](docs/legal-limitations.md).

## Licença

Distribuído sob a licença [MIT](LICENSE).

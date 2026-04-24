# Sistema de Petições

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-supervisionado-yellow.svg)]()
[![CI](https://github.com/1kookieh/sistema-de-peticoes/actions/workflows/ci.yml/badge.svg)](https://github.com/1kookieh/sistema-de-peticoes/actions/workflows/ci.yml)

Pipeline em Python para transformar texto de peças jurídicas em `.docx` com formatação forense padronizada, validação determinística e filas JSON locais. O sistema ajuda a reduzir retrabalho mecânico de Word, mas não substitui advogado, não valida mérito jurídico complexo e não deve ser usado para protocolo sem revisão humana.

## O Que Faz

- Formata texto em `.docx` com A4, margens 3/3/2/2 cm, Times New Roman 12, corpo justificado, espaçamento 1,5, recuo de 2,5 cm e 7 linhas após o endereçamento.
- Valida o `.docx` gerado quanto a regras formais: página, margens, fonte, endereçamento, OAB, local/data, assinatura gráfica e placeholders.
- Bloqueia o enfileiramento quando encontra violação formal ou entrada com dados de exemplo.
- Lê uma fila local `mcp_inbox.json` ou `INBOX_MOCK_PATH` e grava respostas em `mcp_outbox.json`.
- Mantém estado local em `mcp_status.json` para evitar reprocessamento acidental de itens já concluídos.
- Permite perfis formais por contexto, relatório JSON de conformidade e execução sem outbox.
- Possui política configurável de retenção para arquivos locais sensíveis.
- Inclui testes automatizados com `pytest`.

## Demonstração Segura

Este repositório não deve expor peças reais, dados de clientes ou documentos sensíveis. Para avaliar o fluxo sem risco, use apenas `teste_inbox.json` e dados fictícios.

- Roteiro de demonstração: [docs/demo.md](docs/demo.md)
- Estudo de caso técnico: [docs/case-study.md](docs/case-study.md)

## O Que Não Faz

- Não declara que uma peça está juridicamente pronta para protocolo.
- Não substitui conferência de advogado com OAB ativa e poderes nos autos.
- Não verifica automaticamente competência, rito, prazo, tese, jurisprudência atualizada ou regras locais de tribunal.
- Não consulta APIs pagas nem gera mérito jurídico definitivo.
- Não elimina a necessidade de revisar dados pessoais, documentos, cálculo, valor da causa e pedidos.

## Aviso Jurídico e LGPD

Peças jurídicas podem conter dados pessoais, dados sensíveis, informações médicas, dados previdenciários e elementos protegidos por sigilo profissional. Os arquivos abaixo são dados de runtime e devem ser tratados como sensíveis:

- `output/*.docx`
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

Neste ambiente local, o `.env` já foi criado para facilitar o uso imediato. Em outro computador, crie manualmente um `.env` com as variáveis acima.

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
export INBOX_MOCK_PATH=./teste_inbox.json
python -m src.main
```

Também é possível usar a CLI dedicada:

```bash
python -m src --inbox ./teste_inbox.json --profile judicial-inicial-jef
```

PowerShell:

```powershell
$env:INBOX_MOCK_PATH = ".\teste_inbox.json"
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
python -m src --inbox ./teste_inbox.json --strict --report reports/conformidade_report.json --no-outbox
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

Relatórios podem conter identificadores de threads e caminhos de documentos. Trate `reports/` e `*_report.json` como dados sensíveis.

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

A suíte cobre `.env`, contrato JSON, formatador `.docx`, validador, entradas inválidas, acentos, assinatura indevida e bloqueio de outbox.

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
├── prompts/
├── docs/
├── src/
│   ├── formatar_docx.py
│   ├── gmail_reader.py
│   ├── gmail_sender.py
│   ├── main.py
│   ├── pipeline_state.py
│   ├── profiles.py
│   ├── reporting.py
│   ├── retention.py
│   ├── cli.py
│   └── validar_docx.py
├── tests/
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

## Licença

Distribuído sob a licença [MIT](LICENSE).

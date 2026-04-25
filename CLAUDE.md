# CLAUDE.md — Integração com o Modelo Claude

> Documento técnico que descreve **como o modelo Claude (Anthropic)** é integrado ao
> **Sistema de Petições**, quais prompts versionados orientam a geração jurídica,
> quais garantias de supervisão humana o projeto impõe e como reproduzir o fluxo
> ponta a ponta.

---

## Sumário

1. [Visão geral do projeto](#1-visão-geral-do-projeto)
2. [Arquitetura do sistema](#2-arquitetura-do-sistema)
3. [Configuração e setup](#3-configuração-e-setup)
4. [Uso do modelo Claude](#4-uso-do-modelo-claude)
5. [Estratégias de prompt engineering](#5-estratégias-de-prompt-engineering)
6. [Casos de uso](#6-casos-de-uso)
7. [Limitações e considerações éticas](#7-limitações-e-considerações-éticas)
8. [Melhorias futuras](#8-melhorias-futuras)
9. [Referências e recursos](#9-referências-e-recursos)

---

## 1. Visão geral do projeto

### Propósito

O **Sistema de Petições** automatiza a **preparação formal supervisionada** de
documentos jurídicos em `.docx`, no padrão forense brasileiro (A4, margens
3/3/2/2 cm, Times New Roman 12, espaçamento 1,5, recuo de 2,5 cm, 7 linhas
após o endereçamento). O projeto **não substitui advogado**: o modelo Claude
redige a minuta com base em prompts versionados, e um pipeline determinístico
em Python aplica formatação e validação formal antes que qualquer documento
chegue ao operador humano para revisão.

### Problema que resolve

Escritórios pequenos e profissionais autônomos gastam horas em tarefas
mecânicas: replicar layout de petição, conferir OAB, garantir 7 linhas após
o endereçamento, evitar placeholders esquecidos no `.docx`, formatar alíneas,
manter consistência entre peças. O sistema **automatiza essa camada formal**
e transforma o tempo livre em revisão jurídica de mérito — onde o advogado
agrega valor real.

### Público-alvo

| Perfil | Como usa |
|---|---|
| **Advogado(a) atuante** | Cola texto da peça (ou envia PDF/foto), recebe `.docx` formatado e relatório de violações para revisar antes do protocolo. |
| **Estagiário(a) jurídico(a)** | Gera minuta inicial supervisionada para o titular ajustar. |
| **Operador técnico de escritório** | Roda CLI/API local, mantém retenção, audita relatórios JSON/HTML. |
| **Recrutador / avaliador técnico** | Inspeciona arquitetura, prompts versionados e separação entre LLM e validação determinística. |

### O que **não** é

- Não é um chatbot jurídico. Não responde perguntas a clientes finais.
- Não envia peças automaticamente para tribunais ou cartórios.
- Não decide mérito, prazo, competência, tese aplicável, jurisprudência ou cálculo.
- Não usa APIs pagas no core: Claude entra via orquestrador externo do usuário.

---

## 2. Arquitetura do sistema

### Modelo de integração com o Claude

O sistema adota **integração desacoplada por filas locais em JSON**. Em vez de
acoplar o pipeline Python diretamente à API da Anthropic, ele consome um
contrato simples (`mcp_inbox.json`) que pode ser populado por **qualquer
orquestrador** capaz de redigir a peça com Claude (CLI da Anthropic,
Claude Desktop com MCP Gmail, integração customizada via SDK).

```text
                    ┌─────────────────────────────────────────────┐
                    │  Orquestrador externo (Claude + MCP)        │
                    │  - lê e-mail/instrução do cliente            │
                    │  - aplica prompts/prompt_peticao.md          │
                    │  - aplica prompts/prompt_formatacao_word.md  │
                    │  - escreve peticao_texto em mcp_inbox.json   │
                    └────────────────┬────────────────────────────┘
                                     │
                                     ▼
                          ┌──────────────────────┐
                          │   mcp_inbox.json     │  ← contrato JSON estável
                          └──────────┬───────────┘
                                     │
                ┌────────────────────┼────────────────────┐
                ▼                    ▼                    ▼
        src/cli.py            src/api.py          src/desktop.py
        (linha de comando)    (FastAPI + web)     (Tkinter local)
                │                    │                    │
                └────────────────────┼────────────────────┘
                                     ▼
                          ┌─────────────────────┐
                          │  src/main.py         │  ← orquestrador interno
                          │  processar_email()   │
                          └──────────┬──────────┘
                                     │
   ┌─────────────────────┬───────────┴────────────┬─────────────────────┐
   ▼                     ▼                        ▼                     ▼
piece_types        validar_texto          formatar_docx         validar (.docx)
.infer_…           _protocolavel          renderizar()          regras formais
(detector          (pré-validação         (python-docx)         (re-abre o
 determin.)         formal do texto)                             arquivo)
                                                                        │
                                                                        ▼
                                                              ┌──────────────────┐
                                                              │ output/*.docx     │
                                                              │ reports/*.json    │
                                                              │ reports/*.html    │
                                                              │ mcp_status.json   │
                                                              │ mcp_outbox.json   │
                                                              └──────────────────┘
```

### Componentes principais

| Camada | Arquivo | Papel |
|---|---|---|
| **Prompts versionados** | `prompts/prompt_peticao.md` | Guia jurídico mestre com hierarquia de regras, catálogo de peças, restrições éticas e estrutura forense. |
| | `prompts/prompt_formatacao_word.md` | Padrão de formatação Word/DOCX (A4, margens, fontes, alíneas, fechamento). |
| **Contrato com a LLM** | `mcp_inbox.json` | Lista JSON com `thread_id`, `message_id`, `remetente`, `assunto`, `peticao_texto`. |
| **Inferência determinística** | `src/piece_types.py::infer_piece_type_id` | Detecta o tipo de peça pelo cabeçalho e palavras-chave — independente da LLM, auditável. |
| **Perfis formais** | `src/profiles.py` | `judicial-inicial-jef` (padrão PJE/Projudi), `administrativo-inss`, `instrumento-mandato`, etc. |
| **Geração** | `src/formatar_docx.py` | Aplica regras do `prompt_formatacao_word.md` em `.docx` real via `python-docx`. |
| **Validação formal** | `src/validar_docx.py` | Reabre o `.docx` e verifica margens, fonte, OAB, recuos, placeholders. |
| **Orquestração** | `src/main.py`, `src/cli.py`, `src/api.py`, `src/desktop.py` | CLI, API REST local com FastAPI e desktop em Tkinter. |
| **Auditoria** | `src/reporting.py` | Relatórios JSON e HTML por execução. |
| **Estado** | `src/pipeline_state.py` | `mcp_status.json` evita reprocessamento acidental de `message_id` já concluído. |

### Por que filas JSON em vez de SDK direto?

1. **Trocabilidade do modelo.** Hoje o orquestrador roda Claude. Amanhã pode rodar outro LLM, ou um humano. O contrato JSON não muda.
2. **Auditabilidade.** Cada item da fila é inspecionável antes da geração; a validação determinística não depende de chamada de rede.
3. **Custo zero no core.** Quem rodar `pytest`, CI ou o pipeline localmente não consome créditos da Anthropic — a LLM atua só na entrada.
4. **Compliance.** Dados sensíveis não são copiados para serviços externos pelo pipeline interno (a fronteira fica no orquestrador, sob controle do operador).

---

## 3. Configuração e setup

### Requisitos

- **Python 3.11+**
- **CMake-livre.** Toda a pilha do core é Python puro + `python-docx`, `pypdf`, `Pillow`, `pytesseract`, `fastapi`, `uvicorn`.
- **Tesseract OCR** instalado no sistema (opcional — só para uploads de imagem).
- **Acesso ao modelo Claude** via um dos orquestradores suportados (ver §3.4).

### Instalação

```bash
git clone https://github.com/1kookieh/sistema-de-peticoes.git
cd sistema-de-peticoes
python -m venv .venv
source .venv/bin/activate            # PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r requirements-dev.txt   # opcional: para rodar pytest
```

### Configuração local

```bash
cp .env.example .env
```

Variáveis usadas pelo pipeline (todas opcionais para o fluxo web/API com
detecção automática):

```env
EMAIL_ADVOGADO=advogado-responsavel@example.com
API_TOKEN=                            # se vazio, API local fica sem auth
VALIDATION_PROFILE=judicial-inicial-jef
REMETENTES_AUTORIZADOS=               # CSV de e-mails permitidos no inbox
MAX_JSON_BYTES=2097152
RETENTION_ENABLED=false
RETENTION_OUTPUT_DAYS=30
RETENTION_REPORTS_DAYS=30
RETENTION_QUEUE_DAYS=7
RETENTION_STATUS_DAYS=30
```

> ⚠️ **Nunca versione `.env` com dados reais.** O arquivo é ignorado pelo Git;
> mantenha-o local e protegido.

### Conexão com Claude (orquestrador externo)

O Sistema de Petições não embute credenciais da Anthropic. O orquestrador
externo decide como autenticar:

| Cenário | Como conectar |
|---|---|
| **Claude Desktop + MCP Gmail** | O usuário roda Claude Desktop com servidor MCP do Gmail, cola os prompts em `prompts/`, e instrui o Claude a gravar `mcp_inbox.json`. |
| **Anthropic SDK Python** | Script externo lê e-mail, chama `anthropic.Anthropic().messages.create(...)` com os prompts, escreve o texto em `mcp_inbox.json`. |
| **Claude Code / CLI** | Operador roda em loop manual: cola a instrução do cliente, recebe o `peticao_texto` e despeja no JSON. |
| **Mock para testes** | Aponte `INBOX_MOCK_PATH` para um JSON pré-gravado em `examples/`. |

### Como rodar

```bash
# CLI (lote a partir de um JSON de exemplo)
python -m src --inbox ./examples/inbox_valid.json --profile judicial-inicial-jef --no-outbox

# API + front-end local (recomendado para demonstração)
uvicorn src.api:app --host 127.0.0.1 --port 8000 --reload
# Abrir: http://127.0.0.1:8000

# Interface desktop em Tkinter
python -m src.desktop

# Testes
pytest -q
```

---

## 4. Uso do modelo Claude

### Modelos recomendados

| Modelo | Quando usar |
|---|---|
| `claude-opus-4-5` ou superior | Peças complexas (recursos, mandado de segurança, sucessório com testamento). |
| `claude-sonnet-4-5` | Peças repetitivas e bem definidas (auxílio-doença, pensão por morte, declaração de hipossuficiência). Ótimo custo/qualidade. |
| `claude-haiku-4-5` | Reformatação rápida de textos já redigidos. **Não recomendado** para redação inicial de peça complexa. |

### Parâmetros sugeridos

```python
from anthropic import Anthropic

client = Anthropic()  # lê ANTHROPIC_API_KEY do ambiente

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=8192,
    temperature=0.2,        # baixa: queremos consistência formal, não criatividade
    system=open("prompts/prompt_peticao.md").read()
           + "\n\n---\n\n"
           + open("prompts/prompt_formatacao_word.md").read(),
    messages=[
        {
            "role": "user",
            "content": (
                "Cliente: João da Silva, 62 anos, trabalhador rural.\n"
                "Pedido: aposentadoria por idade rural.\n"
                "DER: 12/03/2026. Indeferida por falta de início de prova material.\n"
                "Documentos disponíveis: declaração do sindicato rural, "
                "notas fiscais de venda em feira (2018-2024), CCIR.\n\n"
                "Redija a petição inicial completa para JEF, perfil "
                "judicial-inicial-jef, valor da causa estimado em R$ 18.000,00."
            ),
        }
    ],
)

peticao_texto = response.content[0].text
```

### Boas práticas operacionais

1. **Sempre injete os dois prompts em `system`**, nessa ordem: jurídico primeiro, formatação depois. A hierarquia de regras está explícita no `prompt_peticao.md` §2.
2. **Não use streaming na geração final.** Você precisa do texto completo antes de gravar em `mcp_inbox.json`.
3. **Use `temperature ≤ 0.3`.** Texto jurídico não é criativo — é técnico, repetível e auditável.
4. **`max_tokens` generoso.** Peças iniciais previdenciárias longas podem chegar a ~5–7k tokens.
5. **Use prompt caching** para o `system` (que é estável). Custo cai dramaticamente em uso recorrente:
   ```python
   system=[
       {"type": "text", "text": prompt_juridico, "cache_control": {"type": "ephemeral"}},
       {"type": "text", "text": prompt_formatacao, "cache_control": {"type": "ephemeral"}},
   ]
   ```
6. **Valide antes de enfileirar.** Mesmo com Claude perfeito, rode `validar_texto_protocolavel(texto, profile_id)` antes de gravar `mcp_inbox.json` para detectar placeholders ou ausência de OAB.

---

## 5. Estratégias de prompt engineering

### 5.1 Hierarquia de regras (regra mestra)

O `prompt_peticao.md` define **explicitamente** uma hierarquia de prioridade
para resolver conflitos. Esse padrão é fundamental quando o operador refina
instruções por turno:

```markdown
Seção 2 — HIERARQUIA DE REGRAS

1. Limites profissionais e revisão humana obrigatória.
2. Restrições éticas (não inventar fatos, OAB, jurisprudência).
3. Formatação Word/DOCX (prompts/prompt_formatacao_word.md).
4. Estrutura padrão da peça (cabeçalho, fatos, direito, pedidos).
5. Instruções específicas do operador no turno.
```

> Quando o operador pedir algo que conflite com o item 1 ou 2, o assistente
> **recusa** e sinaliza a pendência, em vez de obedecer cegamente.

### 5.2 Few-shot por tipo de peça

O `prompt_peticao.md` traz exemplos curtos de cada tipo (auxílio-doença,
aposentadoria rural, BPC, recurso inominado, procuração ad judicia, etc.),
sempre com **dados claramente fictícios** marcados como `[PREENCHER: ...]`
para evitar contaminação. Isso reduz alucinação de números reais.

### 5.3 Chain-of-thought controlado

Para peças complexas (mandado de segurança, recurso especial), o prompt
orienta o modelo a **raciocinar primeiro internamente** sobre cabimento e
admissibilidade antes de redigir, mas **a saída final só contém a peça** —
sem exposição do raciocínio para o cliente. Isso evita poluir o `.docx`
final com meta-comentários.

```markdown
Antes de redigir, valide internamente:
- Há ato coator individualizado e autoridade competente?
- O prazo decadencial de 120 dias está respeitado?
- Há prova pré-constituída (não cabe dilação probatória)?

Se algum item falhar, NÃO redija a peça. Liste a pendência ao operador
no formato:
  PENDÊNCIA: <descrição objetiva>
```

### 5.4 Restrição negativa explícita

O prompt usa **regras negativas** de forma agressiva, porque LLMs tendem
a "ajudar demais":

```markdown
PROIBIDO:
- Inventar número de OAB.
- Inventar valores monetários.
- Citar jurisprudência sem que o operador tenha fornecido referência.
- Marcar a peça como "pronta para protocolo".
- Fechar com linha de assinatura (traços/underscores).
- Inserir comentários, marcações de IA, anotações ao usuário final.
```

### 5.5 Output schema implícito

A saída precisa ser **texto puro estruturável** que `formatar_docx.py`
reconhece por regex (`HEADER_RE`, `TITLE_RE`, `SECTION_NAMES`, `ALINEA_RE`,
`OAB_RE`). O prompt pede exatamente isso, sem JSON ou Markdown:

```markdown
A saída deve ser texto puro, em parágrafos separados por linha em branco.
Sem Markdown, sem JSON, sem títulos com #. As seções DOS FATOS, DO DIREITO,
DOS PEDIDOS, DO VALOR DA CAUSA aparecem em CAIXA ALTA, sozinhas em uma linha.
```

### 5.6 Detecção determinística como rede de segurança

Mesmo que o Claude declare ter redigido um "auxílio-doença", a função
`infer_piece_type_id(texto)` reanalisa o texto produzido e confirma o tipo
baseado em palavras-chave. Discordâncias viram alerta no relatório, não
silêncio.

---

## 6. Casos de uso

### 6.1 Geração de petição inicial previdenciária

**Entrada (instrução ao orquestrador):**

```text
Cliente: Maria Aparecida (fictícia), trabalhadora rural, 56 anos.
Pedido: aposentadoria por idade rural.
Documentos: CCIR, declaração do sindicato (2010-2024), notas fiscais
de venda em feira do produtor (2015-2024).
DER administrativa: 03/02/2026. Indeferida.
Vara: Subseção Judiciária de Goiânia/GO.
```

**Saída do Claude (trecho):**

```text
EXCELENTÍSSIMO SENHOR DOUTOR JUIZ FEDERAL DA SUBSEÇÃO JUDICIÁRIA DE GOIÂNIA/GO

(7 linhas em branco)

AÇÃO PREVIDENCIÁRIA DE CONCESSÃO DE APOSENTADORIA POR IDADE RURAL

MARIA APARECIDA [PREENCHER: qualificação completa], representada por
seu procurador que esta subscreve, vem respeitosamente perante Vossa
Excelência propor a presente

AÇÃO DE CONCESSÃO DE APOSENTADORIA POR IDADE RURAL

em face do INSTITUTO NACIONAL DO SEGURO SOCIAL (INSS), pelos fatos e
fundamentos a seguir expostos.

DOS FATOS

A autora exerce atividade rural em regime de economia familiar desde
[PREENCHER: ano inicial], na propriedade [PREENCHER: nome/localização],
conforme comprovam a Declaração de Aptidão ao Pronaf (DAP), a declaração
do Sindicato dos Trabalhadores Rurais (...).

DO DIREITO

(...)

DOS PEDIDOS

(...)

DO VALOR DA CAUSA

Dá-se à causa o valor de R$ [PREENCHER: estimativa = 12 RMI mensais].

Termos em que, pede deferimento.

Goiânia/GO, [PREENCHER: data por extenso].

[NOME COMPLETO DO ADVOGADO RESPONSÁVEL]
OAB/GO 00.000
```

**Pipeline interno:**

1. `infer_piece_type_id(texto)` → detecta `aposentadoria-idade-rural`.
2. Perfil resolvido → `judicial-inicial-jef`.
3. `validar_texto_protocolavel` → bloqueia se o texto vier sem `[PREENCHER]` substituído pelo operador real.
4. `renderizar` → gera o `.docx` com formatação forense.
5. `validar` → confirma A4, margens, 7 linhas após cabeçalho, OAB.
6. Relatório JSON/HTML salvo em `reports/`.

### 6.2 Procuração ad judicia

**Entrada:** "Procuração ad judicia para João Silva (CPF fictício),
poderes gerais para o foro em geral, cláusula ad judicia et extra
não desejada."

**Detecção automática:**

```python
>>> infer_piece_type_id("PROCURAÇÃO AD JUDICIA\n\nOutorgante: João...")
'procuracao-ad-judicia'
>>> get_piece_type('procuracao-ad-judicia').profile_id
'instrumento-mandato'
```

O perfil `instrumento-mandato` **não exige** OAB no fechamento (é
o outorgado que assina, não o outorgante), nem 7 linhas após cabeçalho
(`min_blank_lines_after_header=1`). A validação se adapta.

### 6.3 Reformatação de peça já redigida (entrada via OCR)

Operador fotografa uma peça antiga em papel. O front-end aceita a imagem,
extrai o texto via Tesseract e roda o pipeline:

```bash
curl -X POST http://127.0.0.1:8000/api/documents/upload \
  -F "files=@peticao_antiga.jpg"
```

Resposta:

```json
{
  "status": "ok_no_outbox",
  "piece_type": {"id": "auxilio-incapacidade-temporaria", "nome": "Petição Inicial — Auxílio por Incapacidade Temporária", "grupo": "Benefícios por incapacidade"},
  "piece_type_inferred": true,
  "profile": {"id": "judicial-inicial-jef", "label": "Inicial JEF / Justiça Federal"},
  "profile_inferred": true,
  "problems": [],
  "download_url": "/api/documents/peticao_20260424_103015_xyz.docx/download",
  "report_html_url": "/api/reports/api_20260424_103015_xyz.html"
}
```

### 6.4 Lote de petições idênticas com dados diferentes

Cenário: escritório recebe 50 e-mails pedindo recurso inominado contra
sentenças similares. O orquestrador externo:

1. Lê os 50 e-mails (MCP Gmail).
2. Para cada thread, monta `peticao_texto` com Claude (cache do `system` zera o custo extra).
3. Escreve as 50 entradas em `mcp_inbox.json`.
4. Operador roda `python -m src --strict --report reports/lote.json`.
5. Pipeline gera 50 `.docx` em `output/`, marca cada `message_id` em `mcp_status.json` e devolve relatório consolidado.

---

## 7. Limitações e considerações éticas

### Limitações técnicas

- **Não há streaming** entre Claude e o pipeline: o texto inteiro precisa
  estar pronto antes da geração do `.docx`.
- **Detecção determinística é heurística.** Falha em peças exóticas ou em
  textos sem cabeçalho. Quando a inferência falha, o sistema cai no perfil
  padrão `judicial-inicial-jef`, o que pode ser inadequado para a peça —
  exige conferência humana.
- **Validação formal ≠ validação jurídica.** O sistema confere margens, fonte
  e OAB; **não** confere mérito, prazo, competência, tese.
- **OCR depende do Tesseract.** Imagens de baixa qualidade ou peças
  manuscritas podem produzir texto ilegível, contaminando a peça.

### Considerações éticas

| Risco | Mitigação |
|---|---|
| **Alucinação de jurisprudência ou números de processo** | `prompt_peticao.md` proíbe explicitamente; revisão humana obrigatória; pré-validação bloqueia placeholders. |
| **Vazamento de dados sensíveis (LGPD)** | Pipeline 100% local; `output/`, `reports/`, `mcp_*.json` no `.gitignore`; política de retenção configurável; `API_TOKEN` opcional para a API. |
| **Falsa sensação de "peça pronta"** | Aviso explícito no README, no front-end, em `docs/legal-limitations.md`; nenhum endpoint declara peça "protocolável". |
| **Uso por leigos sem advogado** | O sistema **não é um chatbot público**; roda local sob supervisão; cada peça gerada exige nome e OAB de advogado responsável no fechamento. |
| **Bias do modelo em redação jurídica** | Temperature baixa, restrições negativas explícitas, exemplos few-shot diversificados, e o operador humano é o último filtro. |

### Conformidade com responsabilidade profissional

- **OAB:** Toda peça gerada precisa do nome e do número de OAB do advogado
  responsável no fechamento. O `prompt_peticao.md` enumera os advogados
  do escritório (placeholder no template) e o validador rejeita peças sem
  OAB no perfil judicial.
- **Sigilo profissional:** Recomenda-se rodar o orquestrador externo em
  ambiente local ou em rede privada do escritório. **Nunca** colar dados
  reais de cliente em interfaces públicas de LLMs.
- **Revisão humana obrigatória:** Documentada em `docs/legal-limitations.md`
  e repetida em todo ponto de contato (CLI, API, desktop, README).

---

## 8. Melhorias futuras

### Alta prioridade

- **Cliente Anthropic embutido (opcional).** Adicionar `src/llm_client.py`
  com integração direta via SDK, ativada por flag `--llm-anthropic`, mantendo
  o contrato JSON como fonte de verdade.
- **Prompt caching automático.** Detectar mudanças nos prompts em disco e
  invalidar cache; expor métrica `llm_cache_hit_rate` no relatório.
- **Logging estruturado JSON.** Substituir `print` por `logging` com
  formatter JSON para integrar com observabilidade externa.
- **Validação cruzada peça↔perfil.** Se o operador escolher peça incompatível
  com o perfil, alertar antes da geração em vez de falhar no validador.

### Média prioridade

- **Avaliação automática de qualidade.** Pipeline de eval com peças-âncora
  conhecidas (golden set) que reroda Claude periodicamente e compara
  estrutura/seções com o esperado.
- **Multi-modelo.** Fallback automático para Sonnet quando Opus está
  indisponível ou orçamento estourou.
- **Tool use.** Em vez de o orquestrador escrever `peticao_texto` puro, o
  Claude poderia chamar tools (`gerar_peca(tipo, dados)`) e o pipeline
  processaria a chamada. Reduz alucinação estrutural.
- **RAG em precedentes.** Indexar acórdãos públicos e dar contexto ao
  Claude para fundamentação — sempre marcado como "verificar antes de citar".

### Baixa prioridade

- **Painel de métricas** com taxa de bloqueio por perfil, tempo médio de
  geração, distribuição de tipos de peça.
- **Modo dual-LLM** (Claude + outro modelo) para revisão cruzada.
- **Editor inline no front-end** para o advogado revisar/ajustar antes
  de salvar `.docx`.

---

## 9. Referências e recursos

### Anthropic / Claude

- **Documentação oficial:** https://docs.anthropic.com
- **API Reference:** https://docs.anthropic.com/en/api
- **Prompt Engineering Guide:** https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview
- **Prompt Caching:** https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching
- **Tool use:** https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview
- **Model Context Protocol (MCP):** https://modelcontextprotocol.io

### Projeto

- **Repositório:** https://github.com/1kookieh/sistema-de-peticoes
- **Arquitetura detalhada:** [`docs/architecture.md`](docs/architecture.md)
- **Limitações jurídicas e LGPD:** [`docs/legal-limitations.md`](docs/legal-limitations.md)
- **Contrato da API REST:** [`docs/api.md`](docs/api.md)
- **Prompt jurídico mestre:** [`prompts/prompt_peticao.md`](prompts/prompt_peticao.md)
- **Padrão de formatação Word:** [`prompts/prompt_formatacao_word.md`](prompts/prompt_formatacao_word.md)
- **Detector determinístico:** [`src/piece_types.py`](src/piece_types.py) (função `infer_piece_type_id`)
- **Perfis formais:** [`src/profiles.py`](src/profiles.py)

### Bibliotecas-chave

| Biblioteca | Uso |
|---|---|
| [`python-docx`](https://python-docx.readthedocs.io) | Renderização e validação de `.docx`. |
| [`fastapi`](https://fastapi.tiangolo.com) | API REST local. |
| [`uvicorn`](https://www.uvicorn.org) | Servidor ASGI. |
| [`pypdf`](https://pypdf.readthedocs.io) | Extração de texto de PDF. |
| [`pillow`](https://pillow.readthedocs.io) | Pré-processamento de imagem para OCR. |
| [`pytesseract`](https://github.com/madmaze/pytesseract) | Wrapper Python para Tesseract OCR. |
| [`pytest`](https://docs.pytest.org) | Suíte de testes determinísticos. |

### Padrões e legislação aplicáveis

- **LGPD** (Lei nº 13.709/2018) — tratamento de dados pessoais.
- **Estatuto da OAB** (Lei nº 8.906/1994) — responsabilidade profissional.
- **CPC/2015** — estrutura de petições e recursos.
- **Lei nº 9.099/1995 / Lei nº 10.259/2001** — Juizados Especiais Federais (JEF).
- **EC 103/2019** — reforma da previdência (regras de transição).

---

> **Documento mantido em conjunto com `docs/architecture.md` e
> `docs/legal-limitations.md`. Quando alterar este arquivo, verifique se
> os outros dois continuam consistentes.**

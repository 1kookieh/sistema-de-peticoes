# Arquitetura

O `Sistema de Petições` é um pipeline local para preparação formal supervisionada de documentos jurídicos em `.docx`. A arquitetura prioriza simplicidade, validação determinística e separação entre geração mecânica e revisão jurídica humana.

## Princípios

1. **Uso supervisionado.** O sistema nunca declara uma peça juridicamente pronta sem revisão de advogado.
2. **Validação antes e depois da geração.** A entrada textual é bloqueada quando contém lacunas formais; o `.docx` gerado é reaberto e validado.
3. **Filas locais explícitas.** Integrações externas conversam por JSON em disco.
4. **Dados sensíveis por padrão.** Inbox, outbox, status e `.docx` gerados não devem ser versionados nem expostos como artifacts.
5. **Sem dependências pagas.** O core usa `python-docx`; a API usa FastAPI; testes usam `pytest`.
6. **Perfis explícitos.** Variações por rito ou destino ficam em perfis de validação, não em promessas genéricas.

## Componentes

A organização real do `src/` segue cinco camadas, cada uma com responsabilidade explícita.

### `config.py` (raiz)

Carrega `.env` via `pydantic-settings`, expõe caminhos globais (`OUTPUT_DIR`, `REPORTS_DIR`, `FRONTEND_DIR`, `PROMPTS_DIR`) e configurações como `EMAIL_ADVOGADO`, `API_TOKEN`, `API_ALLOWED_ORIGINS`, `MAX_DOCX_BYTES`, `RATE_LIMIT_*` e a política de retenção. O parser de `.env` foi isolado em funções utilitárias para testes unitários.

### Camada `core/` — domínio puro

- `src/core/domain.py`: tipos compartilhados (`ProcessResult`, `PipelineSummary`, `SetupCheck`).
- `src/core/profiles.py`: define perfis formais (`judicial-inicial-jef`, `judicial-inicial-estadual`, `administrativo-inss`, `extrajudicial-tabelionato`, `instrumento-mandato`, `forense-basico`). Cada perfil declara cabeçalhos aceitos, seções obrigatórias e exigências formais (OAB, local/data, valor da causa, mínimo de linhas após endereçamento).
- `src/core/piece_types.py`: catálogo de tipos de peça alinhado ao prompt jurídico. Cada tipo sugere um perfil formal e registra pontos de revisão humana.
- `src/core/piece_inference.py`: detector determinístico declarativo. Aplica regras em ordem (`INSTRUMENT_RULES` → `ADMIN_RULES` → `TITLE_RULES`) sobre primeira linha, candidatos a título e corpo do texto. Cada regra é uma `DetectionRule` auditável.
- `src/core/prompts.py`: carrega `prompt_peticao.md` e `prompt_formatacao_word.md`, calcula SHA-256 e expõe `PromptSpec` para auditoria. **Não chama LLM** — apenas garante que os prompts versionados existem e registra o hash no relatório.
- `src/core/validation/docx.py`: implementa `validar()` (validação estrutural do binário gerado) e `validar_texto_protocolavel()` (pré-validação textual). Bloqueia placeholders, dados fictícios, OAB em formato inválido, ausência de seções mínimas e fechamento forense.
- `src/core/validation/text.py`: re-exporta `validar_texto_protocolavel` para conveniência.

### Camada `adapters/` — entrada e saída

- `src/adapters/inbox/gmail_reader.py`: lê `mcp_inbox.json` ou `INBOX_MOCK_PATH`. Valida que a entrada é uma lista JSON, exige campos obrigatórios e rejeita duplicidade de `message_id`. Aplica filtro opcional de remetentes autorizados.
- `src/adapters/outbox/gmail_sender.py`: grava `mcp_outbox.json` com anexo `.docx` em base64. Valida destinatário, extensão, localização do anexo em `output/`, tamanho máximo e escreve de forma atômica.
- `src/adapters/files/file_extractors.py`: extrai texto de uploads `.txt`, `.md`, `.docx`, `.pdf` e imagens (OCR via Tesseract). Bloqueia formatos não suportados, limita tamanho por arquivo e total da requisição. **Exige UTF-8** em arquivos de texto (sem fallback silencioso para Latin-1/CP1252).

### Camada `infra/` — infraestrutura local

- `src/infra/docx_render.py`: renderiza texto plano em `.docx` aplicando A4, margens 3/3/2/2 cm, Times 12, 1,5 entre linhas, recuo 2,5 cm, 7 linhas após endereçamento e formatação determinística de títulos, seções, alíneas e assinatura.
- `src/infra/pipeline_state.py`: mantém `mcp_status.json` com status por `message_id`. Itens concluídos com sucesso são ignorados em execuções futuras.
- `src/infra/file_lock.py`: lock cooperativo para escrita atômica de filas locais.
- `src/infra/logging.py`: configura logger (modo texto para CLI, modo JSON para API).

### Camada `interfaces/` — pontos de entrada

- `src/interfaces/api.py`: API REST local com FastAPI. Endpoints versionados em `/api/v1/*`, security headers, CSP, rate limit local, `_safe_file()` para bloquear path traversal, e `Depends(require_api_token)` quando `API_TOKEN` está configurado. `piece_type_id` e `profile_id` são opcionais — `"auto"` ou ausência disparam inferência. Resposta inclui `piece_type_inferred` e `profile_inferred`.
- `src/interfaces/cli.py`: `python -m src` com `--setup`, `--profile`, `--list-profiles`, `--inbox`, `--strict`, `--report`, `--no-outbox`, `--apply-retention` e `--cleanup-only`.
- `src/interfaces/desktop.py`: interface Tkinter para uso local sem navegador. Reaproveita o mesmo pipeline.

### Camada `orchestration/` — fluxos

- `src/orchestration/pipeline.py`: orquestrador supervisionado. Aplica pré-validação textual, renderização, validação binária e (opcionalmente) outbox. Itens inválidos não são enfileirados.
- `src/orchestration/reporting.py`: gera relatórios JSON e HTML de conformidade. Registra perfil, violações, hash dos prompts, página, margens, fontes e seções encontradas.
- `src/orchestration/history.py`: lê relatórios JSON e estado local para o painel de histórico. Ignora JSON corrompido em vez de quebrar o painel inteiro.
- `src/orchestration/setup.py`: cria `output/` e `reports/` com `.gitkeep` e verifica recursos essenciais.
- `src/orchestration/retention.py`: aplica política configurável de retenção para `output/`, inbox, outbox, status e relatórios. Modo dry-run por padrão; só apaga com `--apply-retention`.

### `web/`

Front-end local em HTML, CSS e JavaScript ES Modules, sem build. Estrutura:

- `web/index.html`: layout LexDoc com stepper, drag-drop, configurações avançadas e checklist.
- `web/app.js`: bootstrap e registro do service worker.
- `web/api.js`: chamadas HTTP para `/api/v1`.
- `web/state/store.js`: estado global, tema, limites e token.
- `web/render.js`: templates HTML com `escapeHTML`.
- `web/ui.js`: DOM, eventos, drag-drop, stepper, validação visual.
- `web/sw.js`: service worker que cacheia apenas assets estáticos (nunca `/api/v1`).

### Pipeline supervisionado

`src/orchestration/pipeline.py` orquestra o fluxo:

```text
inbox JSON
  -> validação de contrato
  -> pré-validação formal do texto
  -> geração .docx
  -> validação .docx
  -> outbox somente se válido e solicitado
  -> relatório opcional
  -> status por item
```

Fluxo API/web:

```text
front-end local
  -> POST /api/v1/documents (peça/perfil podem vir vazios)
  -> infer_piece_type_id(texto) quando piece_type_id é vazio
  -> resolução de perfil: peça detectada -> perfil sugerido
                          sem peça        -> judicial-inicial-jef (PJE/Projudi)
  -> processar_email(no_outbox=True)
  -> output/*.docx
  -> reports/*.json + reports/*.html
  -> download local + painel de histórico
```

## Fluxo De Falhas

- Falha de configuração: exit code `2`.
- Falha técnica de leitura/processamento: exit code `1`.
- Violação formal em uma ou mais peças: exit code `3`.
- Itens inválidos não são enfileirados.
- Falha em um item não derruba o lote inteiro; o status fica registrado por `message_id`.
- `--strict` falha quando nenhum documento novo válido é produzido.

## Segurança E LGPD

Os arquivos `output/*.docx`, `reports/*.json`, `reports/*.html`, `mcp_inbox.json`, `mcp_outbox.json` e `mcp_status.json` são runtime local e podem conter dados pessoais ou sensíveis. Eles ficam no `.gitignore`, mas isso não substitui controle de acesso, retenção curta e revisão operacional.

O repositório mantém apenas CI técnico em GitHub Actions. O processamento operacional de peças não roda por workflow manual para evitar exposição acidental de dados jurídicos, anexos `.docx` ou relatórios sensíveis em ambiente de terceiros.

## Testabilidade

A suíte em `tests/` cobre:

- parser `.env`;
- contrato da inbox;
- geração e validação de `.docx`;
- bloqueio de placeholders;
- assinatura indevida;
- bloqueio de outbox;
- exit code de configuração ausente.
- golden file estrutural do `.docx`;
- CLI com relatório e `--no-outbox`;
- retenção em dry-run e modo aplicado;
- API local, painel de histórico e relatório HTML;
- detector automático de peça (`infer_piece_type_id`) com cenários parametrizados cobrindo procurações, recursos, cumprimento, sucessório, administrativos e benefícios.


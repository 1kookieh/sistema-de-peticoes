# Arquitetura

O `Sistema de PetiÃ§Ãµes` Ã© um pipeline local para preparaÃ§Ã£o formal supervisionada de documentos jurÃ­dicos em `.docx`. A arquitetura prioriza simplicidade, validaÃ§Ã£o determinÃ­stica e separaÃ§Ã£o entre geraÃ§Ã£o mecÃ¢nica e revisÃ£o jurÃ­dica humana.

## PrincÃ­pios

1. **Uso supervisionado.** O sistema nunca declara uma peÃ§a juridicamente pronta sem revisÃ£o de advogado.
2. **ValidaÃ§Ã£o antes e depois da geraÃ§Ã£o.** A entrada textual Ã© bloqueada quando contÃ©m lacunas formais; o `.docx` gerado Ã© reaberto e validado.
3. **Filas locais explÃ­citas.** IntegraÃ§Ãµes externas conversam por JSON em disco.
4. **Dados sensÃ­veis por padrÃ£o.** Inbox, outbox, status e `.docx` gerados nÃ£o devem ser versionados nem expostos como artifacts.
5. **Sem dependÃªncias pagas.** O core usa `python-docx`; a API usa FastAPI; testes usam `pytest`.
6. **Perfis explÃ­citos.** VariaÃ§Ãµes por rito ou destino ficam em perfis de validaÃ§Ã£o, nÃ£o em promessas genÃ©ricas.

## Componentes

### `config.py`

Carrega `.env` simples, expÃµe caminhos globais e configuraÃ§Ãµes como `EMAIL_ADVOGADO`, `REMETENTES_AUTORIZADOS` e `MAX_JSON_BYTES`. O parser foi isolado para testes unitÃ¡rios.

### `src/gmail_reader.py`

LÃª `mcp_inbox.json` ou `INBOX_MOCK_PATH`. Valida que a entrada Ã© uma lista JSON, exige campos obrigatÃ³rios, rejeita duplicidade de `message_id` e aplica filtro opcional de remetentes autorizados.

### `src/formatar_docx.py`

Converte texto plano em `.docx`, aplicando A4, margens, fonte, alinhamentos, recuos, 7 linhas apÃ³s endereÃ§amento e formataÃ§Ã£o bÃ¡sica de seÃ§Ãµes, alÃ­neas e assinatura.

### `src/validar_docx.py`

Executa validaÃ§Ãµes formais, separadas do formatador. TambÃ©m expÃµe `validar_texto_protocolavel()`, usada antes da geraÃ§Ã£o para bloquear placeholders, dados fictÃ­cios, OAB invÃ¡lida e ausÃªncia de elementos mÃ­nimos.

### `src/profiles.py`

Define perfis formais como `judicial-inicial-jef`, `administrativo-inss`, `extrajudicial-tabelionato` e `instrumento-mandato`. Cada perfil declara cabeÃ§alhos aceitos, seÃ§Ãµes obrigatÃ³rias e exigÃªncias formais como OAB, local/data e valor da causa.

### `src/piece_types.py`

Centraliza o catÃ¡logo de tipos de peÃ§a exibido no front-end, alinhado Ã  seÃ§Ã£o de peÃ§as contempladas do prompt jurÃ­dico. Cada tipo sugere um perfil formal e registra pontos que exigem revisÃ£o humana, incluindo procuraÃ§Ãµes, substabelecimentos e declaraÃ§Ãµes.

TambÃ©m expÃµe `infer_piece_type_id(texto)`, um detector determinÃ­stico baseado em (1) primeira linha (cabeÃ§alho) e (2) palavras-chave do corpo. Quando o usuÃ¡rio nÃ£o escolhe a peÃ§a, a API delega para essa funÃ§Ã£o; o resultado Ã© auditÃ¡vel (cada decisÃ£o Ã© uma regra explÃ­cita) e cai em `peticao-simples` para cabeÃ§alhos judiciais sem palavra-chave reconhecida, ou `None` para texto irrelevante.

### `src/file_extractors.py`

Extrai texto de uploads `.txt`, `.md`, `.docx`, `.pdf` e imagens. Imagens sÃ£o fonte para OCR via Tesseract e nÃ£o sÃ£o anexadas ao `.docx` final. O mÃ³dulo bloqueia formatos nÃ£o suportados, limita tamanho do arquivo e falha quando nÃ£o hÃ¡ texto extraÃ­vel.

### `src/gmail_sender.py`

Grava `mcp_outbox.json` com anexo `.docx` em base64. O mÃ³dulo valida destinatÃ¡rio, extensÃ£o, localizaÃ§Ã£o do anexo em `output/`, tamanho mÃ¡ximo e salva a fila de forma atÃ´mica.

### `src/pipeline_state.py`

MantÃ©m `mcp_status.json` com status por `message_id`. Itens concluÃ­dos com sucesso sÃ£o ignorados em execuÃ§Ãµes futuras para reduzir risco de envio duplicado.

### `src/orchestration/reporting.py`

Extrai estrutura do `.docx` e gera relatÃ³rios JSON e HTML de conformidade formal. O relatÃ³rio registra perfil, violaÃ§Ãµes, pÃ¡gina, margens, fontes, quantidade de parÃ¡grafos e seÃ§Ãµes mÃ­nimas encontradas.

### `src/interfaces/api.py`

ExpÃµe uma API REST local com FastAPI para setup, listagem de perfis, listagem de tipos de peÃ§a, geraÃ§Ã£o por texto/upload, download de `.docx` e consulta de relatÃ³rios. A API usa `--no-outbox` por padrÃ£o no fluxo web para evitar envio automÃ¡tico ou falsa sensaÃ§Ã£o de protocolo.

`piece_type_id` e `profile_id` sÃ£o opcionais: ausentes ou `"auto"` disparam inferÃªncia automÃ¡tica (peÃ§a pelo texto; perfil pela peÃ§a detectada, com fallback `judicial-inicial-jef`). A resposta carrega `piece_type_inferred` e `profile_inferred` para o front-end mostrar o que foi escolhido automaticamente.

`/api/v1/profiles` retorna `{items, default}` em vez de lista crua: cada item traz `label` em PT-BR, `is_default`, exigÃªncias formais (`require_oab`, `require_local_data`, `require_value_cause`) e a lista `required_sections`.

### `web/`

Front-end local em HTML, CSS e JavaScript puro. Essa escolha evita build com Node, reduz superfÃ­cie de manutenÃ§Ã£o e mantÃ©m o projeto fÃ¡cil de demonstrar em ambiente limpo.

### `src/orchestration/history.py`

LÃª relatÃ³rios JSON e estado local para alimentar o painel de histÃ³rico. O mÃ³dulo ignora JSON corrompido em vez de quebrar o painel inteiro.

### `src/interfaces/desktop.py`

Interface desktop com Tkinter para colar/carregar texto e gerar `.docx` usando o mesmo pipeline supervisionado. NÃ£o adiciona dependÃªncia externa de GUI.

### `src/retention.py`

Aplica polÃ­tica configurÃ¡vel de retenÃ§Ã£o para `output/`, inbox, outbox, status e arquivos temporÃ¡rios. Por seguranÃ§a, a CLI pode listar candidatos em dry-run ou apagar somente com `--apply-retention`.

### `src/interfaces/cli.py`

Fornece `python -m src` com `--setup`, `--profile`, `--strict`, `--report`, `--no-outbox`, `--cleanup-only` e `--apply-retention`.

### `src/core/domain.py`

Centraliza tipos compartilhados do domÃ­nio, como resultado por item, resumo do pipeline e verificaÃ§Ãµes de setup. Isso reduz acoplamento entre CLI, orquestrador e relatÃ³rios.

### `src/orchestration/setup.py`

Cria `output/` e `reports/` com `.gitkeep` e verifica recursos essenciais para o primeiro uso local.

### `src/orchestration/pipeline.py`

Orquestra o fluxo:

```text
inbox JSON
  -> validaÃ§Ã£o de contrato
  -> prÃ©-validaÃ§Ã£o formal do texto
  -> geraÃ§Ã£o .docx
  -> validaÃ§Ã£o .docx
  -> outbox somente se vÃ¡lido e solicitado
  -> relatÃ³rio opcional
  -> status por item
```

Fluxo API/web:

```text
front-end local
  -> POST /api/v1/documents (peÃ§a/perfil podem vir vazios)
  -> infer_piece_type_id(texto) quando piece_type_id Ã© vazio
  -> resoluÃ§Ã£o de perfil: peÃ§a detectada -> perfil sugerido
                          sem peÃ§a        -> judicial-inicial-jef (PJE/Projudi)
  -> processar_email(no_outbox=True)
  -> output/*.docx
  -> reports/*.json + reports/*.html
  -> download local + painel de histÃ³rico
```

## Fluxo De Falhas

- Falha de configuraÃ§Ã£o: exit code `2`.
- Falha tÃ©cnica de leitura/processamento: exit code `1`.
- ViolaÃ§Ã£o formal em uma ou mais peÃ§as: exit code `3`.
- Itens invÃ¡lidos nÃ£o sÃ£o enfileirados.
- Falha em um item nÃ£o derruba o lote inteiro; o status fica registrado por `message_id`.
- `--strict` falha quando nenhum documento novo vÃ¡lido Ã© produzido.

## SeguranÃ§a E LGPD

Os arquivos `output/*.docx`, `reports/*.json`, `reports/*.html`, `mcp_inbox.json`, `mcp_outbox.json` e `mcp_status.json` sÃ£o runtime local e podem conter dados pessoais ou sensÃ­veis. Eles ficam no `.gitignore`, mas isso nÃ£o substitui controle de acesso, retenÃ§Ã£o curta e revisÃ£o operacional.

O repositÃ³rio mantÃ©m apenas CI tÃ©cnico em GitHub Actions. O processamento operacional de peÃ§as nÃ£o roda por workflow manual para evitar exposiÃ§Ã£o acidental de dados jurÃ­dicos, anexos `.docx` ou relatÃ³rios sensÃ­veis em ambiente de terceiros.

## Testabilidade

A suÃ­te em `tests/` cobre:

- parser `.env`;
- contrato da inbox;
- geraÃ§Ã£o e validaÃ§Ã£o de `.docx`;
- bloqueio de placeholders;
- assinatura indevida;
- bloqueio de outbox;
- exit code de configuraÃ§Ã£o ausente.
- golden file estrutural do `.docx`;
- CLI com relatÃ³rio e `--no-outbox`;
- retenÃ§Ã£o em dry-run e modo aplicado;
- API local, painel de histÃ³rico e relatÃ³rio HTML;
- detector automÃ¡tico de peÃ§a (`infer_piece_type_id`) com cenÃ¡rios parametrizados cobrindo procuraÃ§Ãµes, recursos, cumprimento, sucessÃ³rio, administrativos e benefÃ­cios.


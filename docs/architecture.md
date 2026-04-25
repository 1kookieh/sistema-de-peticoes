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

### `config.py`

Carrega `.env` simples, expõe caminhos globais e configurações como `EMAIL_ADVOGADO`, `REMETENTES_AUTORIZADOS` e `MAX_JSON_BYTES`. O parser foi isolado para testes unitários.

### `src/gmail_reader.py`

Lê `mcp_inbox.json` ou `INBOX_MOCK_PATH`. Valida que a entrada é uma lista JSON, exige campos obrigatórios, rejeita duplicidade de `message_id` e aplica filtro opcional de remetentes autorizados.

### `src/formatar_docx.py`

Converte texto plano em `.docx`, aplicando A4, margens, fonte, alinhamentos, recuos, 7 linhas após endereçamento e formatação básica de seções, alíneas e assinatura.

### `src/validar_docx.py`

Executa validações formais, separadas do formatador. Também expõe `validar_texto_protocolavel()`, usada antes da geração para bloquear placeholders, dados fictícios, OAB inválida e ausência de elementos mínimos.

### `src/profiles.py`

Define perfis formais como `judicial-inicial-jef`, `administrativo-inss`, `extrajudicial-tabelionato` e `instrumento-mandato`. Cada perfil declara cabeçalhos aceitos, seções obrigatórias e exigências formais como OAB, local/data e valor da causa.

### `src/piece_types.py`

Centraliza o catálogo de tipos de peça exibido no front-end, alinhado à seção de peças contempladas do prompt jurídico. Cada tipo sugere um perfil formal e registra pontos que exigem revisão humana, incluindo procurações, substabelecimentos e declarações.

Também expõe `infer_piece_type_id(texto)`, um detector determinístico baseado em (1) primeira linha (cabeçalho) e (2) palavras-chave do corpo. Quando o usuário não escolhe a peça, a API delega para essa função; o resultado é auditável (cada decisão é uma regra explícita) e cai em `peticao-simples` para cabeçalhos judiciais sem palavra-chave reconhecida, ou `None` para texto irrelevante.

### `src/file_extractors.py`

Extrai texto de uploads `.txt`, `.md`, `.docx`, `.pdf` e imagens. Imagens são fonte para OCR via Tesseract e não são anexadas ao `.docx` final. O módulo bloqueia formatos não suportados, limita tamanho do arquivo e falha quando não há texto extraível.

### `src/gmail_sender.py`

Grava `mcp_outbox.json` com anexo `.docx` em base64. O módulo valida destinatário, extensão, localização do anexo em `output/`, tamanho máximo e salva a fila de forma atômica.

### `src/pipeline_state.py`

Mantém `mcp_status.json` com status por `message_id`. Itens concluídos com sucesso são ignorados em execuções futuras para reduzir risco de envio duplicado.

### `src/reporting.py`

Extrai estrutura do `.docx` e gera relatórios JSON e HTML de conformidade formal. O relatório registra perfil, violações, página, margens, fontes, quantidade de parágrafos e seções mínimas encontradas.

### `src/api.py`

Expõe uma API REST local com FastAPI para setup, listagem de perfis, listagem de tipos de peça, geração por texto/upload, download de `.docx` e consulta de relatórios. A API usa `--no-outbox` por padrão no fluxo web para evitar envio automático ou falsa sensação de protocolo.

`piece_type_id` e `profile_id` são opcionais: ausentes ou `"auto"` disparam inferência automática (peça pelo texto; perfil pela peça detectada, com fallback `judicial-inicial-jef`). A resposta carrega `piece_type_inferred` e `profile_inferred` para o front-end mostrar o que foi escolhido automaticamente.

`/api/profiles` retorna `{items, default}` em vez de lista crua: cada item traz `label` em PT-BR, `is_default`, exigências formais (`require_oab`, `require_local_data`, `require_value_cause`) e a lista `required_sections`.

### `web/`

Front-end local em HTML, CSS e JavaScript puro. Essa escolha evita build com Node, reduz superfície de manutenção e mantém o projeto fácil de demonstrar em ambiente limpo.

### `src/history.py`

Lê relatórios JSON e estado local para alimentar o painel de histórico. O módulo ignora JSON corrompido em vez de quebrar o painel inteiro.

### `src/desktop.py`

Interface desktop com Tkinter para colar/carregar texto e gerar `.docx` usando o mesmo pipeline supervisionado. Não adiciona dependência externa de GUI.

### `src/retention.py`

Aplica política configurável de retenção para `output/`, inbox, outbox, status e arquivos temporários. Por segurança, a CLI pode listar candidatos em dry-run ou apagar somente com `--apply-retention`.

### `src/cli.py`

Fornece `python -m src` com `--setup`, `--profile`, `--strict`, `--report`, `--no-outbox`, `--cleanup-only` e `--apply-retention`.

### `src/domain.py`

Centraliza tipos compartilhados do domínio, como resultado por item, resumo do pipeline e verificações de setup. Isso reduz acoplamento entre CLI, orquestrador e relatórios.

### `src/setup_runtime.py`

Cria `output/` e `reports/` com `.gitkeep` e verifica recursos essenciais para o primeiro uso local.

### `src/main.py`

Orquestra o fluxo:

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
  -> POST /api/documents (peça/perfil podem vir vazios)
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

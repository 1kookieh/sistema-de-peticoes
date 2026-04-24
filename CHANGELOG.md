# Changelog

Todas as mudanças notáveis deste projeto são documentadas aqui.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e o projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Unreleased]

### Adicionado
- Suíte inicial de testes automatizados com `pytest`.
- `requirements-dev.txt` para dependências de desenvolvimento.
- Pré-validação formal do texto antes da geração do `.docx`.
- Estado local `mcp_status.json` para reduzir reprocessamento acidental por `message_id`.
- Validação de contrato da inbox JSON, incluindo campos obrigatórios, tamanho máximo e `message_id` duplicado.
- Validações adicionais de `.docx`: A4 explícito, OAB formatada, local/data, recuo e placeholders.
- Perfis de validação formal por contexto (`judicial-inicial-jef`, `administrativo-inss`, etc.).
- CLI dedicada via `python -m src` com `--strict`, `--report`, `--no-outbox` e retenção.
- Relatório JSON de conformidade formal com estrutura do `.docx`.
- Golden file estrutural para regressão de documentos `.docx`.
- Política configurável de retenção/expurgo para runtime local.

### Alterado
- O pipeline agora bloqueia a outbox quando encontra qualquer violação formal.
- O CI roda `compileall` e `pytest`.
- A documentação foi reescrita para deixar claro que o uso é jurídico supervisionado.
- O workflow manual de processamento foi removido para manter o repositório público focado em CI e evitar execução operacional com dados jurídicos em GitHub Actions.
- A configuração local passou a usar `.env` ignorado pelo Git, sem manter `.env.example` no repositório.

### Segurança
- Escrita atômica da outbox.
- Validação de anexo `.docx` dentro de `output/`.
- Avisos de LGPD e sigilo profissional no README e arquitetura.

## [1.0.0] - 2026-04-24

### Adicionado
- Pipeline completo `formatar → validar → enfileirar` em `src/main.py`.
- Formatador `src/formatar_docx.py` aplicando padrão forense brasileiro (A4, margens 3/3/2/2 cm, Times New Roman 12, 1,5 de espaçamento, recuo 2,5 cm, 7 linhas após o endereçamento, negrito restrito a elementos autorizados, nome e OAB centralizados sem linha de assinatura).
- Validador determinístico `src/validar_docx.py` que relê o `.docx` e retorna violações de margens, fonte, alinhamentos, 7 linhas e OAB no fechamento.
- Ingestão e entrega via filas JSON (`mcp_inbox.json` / `mcp_outbox.json`) em `gmail_reader.py` e `gmail_sender.py`.
- Loader `.env` sem dependência externa em `config.py`.
- Prompts versionados em `prompts/` com regras jurídicas e de formatação.
- `teste_inbox.json` como fixture de teste local.
- Exit codes semânticos em `main.py` (0 OK, 1 falha, 2 config ausente, 3 gerado com violações).
- Documentação `docs/` com `architecture.md`, `decisions.md`, `roadmap.md` e `recruiter-notes.md`.
- `CHANGELOG.md` e `CONTRIBUTING.md` em pt-BR.
- Templates de issue e pull request em `.github/`.
- Workflow de CI (`.github/workflows/ci.yml`) com instalação de dependências e `py_compile` dos módulos.
- Licença MIT.

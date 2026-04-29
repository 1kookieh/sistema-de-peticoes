# Changelog

Todas as mudanças relevantes deste projeto são documentadas aqui.

## [Unreleased]

### Added

- Camada `src/infra/llm/` para geração opcional com LLM.
- Provider `mock` para testes e desenvolvimento.
- Provider `openai` via HTTP, ativado somente com `OPENAI_API_KEY`.
- Provider `anthropic` via Anthropic Messages API, ativado somente com `ANTHROPIC_API_KEY`.
- Provider `ollama` para IA local via `OLLAMA_BASE_URL`, sem chave externa.
- Allowlist `LLM_CLIENT_ALLOWED_PROVIDERS` para escolha segura de provider/modelo pela interface/API sem permitir `none`.
- Schemas Pydantic para resposta estruturada da IA.
- Metadados `llm` em respostas da API e relatórios.
- Mascaramento de CPF, CNPJ, NIT, NB, RG, CEP, telefone e e-mail antes de chamadas a providers externos.
- Consentimento explícito por requisição para providers externos de IA.
- Paths MCP centralizados em `config.py`.
- CI com `ruff`, `mypy` gradual, `pip-audit`, `bandit` e cobertura de testes.
- `CODEOWNERS` e Dependabot para manutenção do repositório.
- Controles `LLM_*` em `.env.example`.
- Botões separados na interface web: `Gerar DOCX` e `Validar texto`.
- Documentação específica de uso, prompts e segurança.
- `AGENTS.md` com instruções específicas para agentes de IA no projeto.

### Changed

- Fluxo principal refatorado para AI-first: criação passa por LLM configurado no backend.
- Interface web simplificada para `Criar documento com IA`, sem seletor de provider, histórico recente ou validação/triagem como ação principal.
- API passou a tratar `llm.enabled/provider/model` como campos legados e usar `LLM_REQUIRED`/`LLM_PROVIDER` do backend.
- CLI passou a usar IA por padrão, com `--mock` para desenvolvimento/testes e sem opção principal de triagem.
- README reestruturado para refletir o fluxo real com e sem IA.
- Documentação de API e arquitetura atualizada para `/api/v1` e camada LLM.
- Documentação de Docker atualizada para refletir `API_REQUIRE_TOKEN=1` por padrão.
- README e docs de uso/API reforçam uso de `X-API-Token` em container e redaction como proteção parcial, não anonimização.
- Template de Pull Request atualizado para comandos reais de validação.
- Guias de segurança, contribuição e agentes reforçam mock provider, consentimento e riscos de IA externa.
- Prompts passaram por sanitização para remover dados sensíveis identificados.
- Modo `minuta` permite gerar DOCX com alertas formais não críticos.
- Provider `mock` passou a sinalizar revisão pendente e não entregar modo `final`.

### Security

- Chaves de IA documentadas apenas como placeholders.
- Prompt completo não é salvo por padrão em relatórios.
- Fallback para mock permanece desativado por padrão.
- Chamadas externas de IA agora exigem consentimento explícito e passam por redaction prévia.
- Dependências vulneráveis (`pypdf`, `python-multipart`, `pillow`) atualizadas para versões corrigidas.

## [1.0.0] - 2026-04-24

### Added

- Pipeline local de geração e validação DOCX.
- API local com FastAPI.
- Interface web local.
- CLI via `python -m src`.
- Interface desktop Tkinter.
- Relatórios JSON/HTML.
- Dockerfile.
- Testes automatizados.
- Prompts versionados.
- Perfis formais e detector de tipo de peça.
- Documentação inicial, templates GitHub e licença MIT.

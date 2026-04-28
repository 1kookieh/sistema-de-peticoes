# Changelog

Todas as mudanças relevantes deste projeto são documentadas aqui.

## [Unreleased]

### Added

- Camada `src/infra/llm/` para geração opcional com LLM.
- Provider `mock` para testes e desenvolvimento.
- Provider `openai` via HTTP, ativado somente com `OPENAI_API_KEY`.
- Schemas Pydantic para resposta estruturada da IA.
- Metadados `llm` em respostas da API e relatórios.
- Controles `LLM_*` em `.env.example`.
- Botões separados na interface web: `Gerar DOCX` e `Validar texto`.
- Documentação específica de uso, prompts e segurança.

### Changed

- README reestruturado para refletir o fluxo real com e sem IA.
- Documentação de API e arquitetura atualizada para `/api/v1` e camada LLM.
- Prompts passaram por sanitização para remover dados sensíveis identificados.
- Modo `minuta` permite gerar DOCX com alertas formais não críticos.

### Security

- Chaves de IA documentadas apenas como placeholders.
- Prompt completo não é salvo por padrão em relatórios.
- Fallback para mock permanece desativado por padrão.

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

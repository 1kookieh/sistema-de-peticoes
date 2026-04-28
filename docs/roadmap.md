# Roadmap

Este roadmap lista melhorias técnicas planejadas. Ele não promete prazo nem substitui revisão jurídica humana.

## Concluído

- Pipeline local de geração e validação DOCX.
- API FastAPI em `/api/v1`.
- Interface web local.
- CLI e interface desktop.
- Dockerfile.
- Relatórios JSON/HTML.
- Retenção configurável.
- Detector automático de tipos de peça.
- Modos `minuta`, `final` e `triagem`.
- Integração LLM opcional com `mock` e `openai`.
- Prompts versionados com hash de auditoria.
- Testes automatizados para fluxo crítico.

## Próximas Melhorias

- Melhorar mensagens de validação por seção/parágrafo.
- Ampliar validações específicas por tipo de peça.
- Adicionar paginação e busca mais completa em relatórios.
- Refinar preview visual antes do download.
- Adicionar screenshots/GIFs reais no README.
- Melhorar suporte a múltiplos advogados no fechamento.

## Médio Prazo

- Providers adicionais: Anthropic, Gemini, OpenRouter e Ollama.
- Exportação PDF opcional via ferramenta local.
- Templates por classe processual.
- Configuração avançada de perfis por tribunal/escritório.
- Mascaramento configurável de dados pessoais em relatórios.

## Fora do Escopo Atual

- Substituir advogado responsável.
- Garantir tese jurídica correta.
- Garantir aceitação por todos os tribunais.
- Processar dados reais em GitHub Actions.
- Expor a API publicamente sem camada adicional de segurança.

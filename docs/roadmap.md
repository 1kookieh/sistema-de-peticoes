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
- Modos `minuta` e `final` no fluxo principal.
- Integração AI-first com Groq como provider externo único.
- Provider `mock` reservado para testes automatizados.
- Paginação básica em `/api/v1/pieces` e `/api/v1/reports`.
- Prompts versionados com hash de auditoria.
- Testes automatizados para fluxo crítico.
- Smoke HTTP cobrindo chat, criação de documento, dashboard e peças.

## Próximas Melhorias

- Melhorar mensagens de validação por seção/parágrafo.
- Ampliar validações específicas por tipo de peça.
- Adicionar filtros e busca mais completa em peças e relatórios.
- Refinar preview visual antes do download.
- Adicionar screenshots/GIFs reais no README.
- Melhorar suporte a múltiplos advogados no fechamento.

## Médio Prazo

- Migrar estado local JSON para SQLite ou outro armazenamento transacional.
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

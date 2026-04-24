# Notas para recrutadores / tech leads

Resumo de 2 minutos para quem está avaliando o projeto.

## O que é

Pipeline Python (3.11+) que transforma texto plano em peças jurídicas `.docx` no padrão forense brasileiro, com um validador determinístico que confere o documento depois de gerado.

## Por que é interessante

- **Domínio específico resolvido de verdade.** Não é um CRUD genérico — o sistema codifica regras reais de formatação jurídica (margens, fontes, 7 linhas após endereçamento, negrito restrito a elementos autorizados).
- **Separação formatação × validação.** O validador funciona como oráculo independente do gerador. Isso é uma boa prática de software test‑driven aplicada ao domínio de documentos.
- **Arquitetura orientada a filas JSON.** O núcleo Python é agnóstico ao canal de entrega — ingestão e envio são contratos em disco. Facilita testes, integrações e troca de canal sem mexer no core.
- **Dependências mínimas.** Uma biblioteca de runtime (`python-docx`) e um loader `.env` caseiro. Sem vendor lock‑in.
- **Exit codes semânticos.** Pensado para rodar em CI/CD: `0` OK, `1` falha, `2` config ausente, `3` gerado com violações.

## Como avaliar em 5 minutos

1. Abra `src/main.py` — 99 linhas, orquestrador limpo.
2. Veja o contraste entre `src/formatar_docx.py` (gera) e `src/validar_docx.py` (verifica).
3. Leia `docs/decisions.md` para entender trade-offs explícitos.
4. Rode `INBOX_MOCK_PATH=./teste_inbox.json python -m src.main` — gera um `.docx` em `output/` e valida.

## Skills demonstradas

- Python moderno (`dataclass`, `Path`, type hints, `from __future__ import annotations`).
- Manipulação de OOXML via `python-docx`.
- Desenho de pipelines determinísticos com exit codes acionáveis.
- Modelagem por contratos (JSON) em vez de SDKs.
- Documentação técnica em pt-BR clara e navegável.

## Stack em uma linha

Python 3.11 · `python-docx` · GitHub Actions · Conventional Commits · MIT.

## Contato

GitHub: [@1kookieh](https://github.com/1kookieh)

# Notas para recrutadores / tech leads

Resumo de 2 minutos para quem está avaliando o projeto.

## O que é

Pipeline Python (3.11+) que transforma texto plano em peças jurídicas `.docx` com padrão formal forense, validação determinística e bloqueios para uso jurídico supervisionado.

## Por que é interessante

- **Domínio específico com risco tratado.** Não é um CRUD genérico — o sistema codifica regras reais de formatação jurídica e deixa explícito que revisão humana continua obrigatória.
- **Separação formatação × validação.** O validador funciona como oráculo independente do gerador. Isso é uma boa prática de software test‑driven aplicada ao domínio de documentos.
- **Arquitetura orientada a filas JSON.** O núcleo Python é agnóstico ao canal de entrega — ingestão e envio são contratos em disco. Facilita testes, integrações e troca de canal sem mexer no core.
- **Dependências mínimas.** Uma biblioteca de runtime (`python-docx`), `pytest` só para desenvolvimento e um loader `.env` simples. Sem vendor lock-in.
- **Exit codes semânticos.** Pensado para rodar em CI/CD: `0` OK, `1` falha técnica, `2` config ausente, `3` peça bloqueada por violação formal.

## Como avaliar em 5 minutos

1. Abra `src/main.py` — orquestra validação, geração, bloqueio e status por item.
2. Veja o contraste entre `src/formatar_docx.py` (gera) e `src/validar_docx.py` (verifica).
3. Leia `docs/decisions.md` para entender trade-offs explícitos.
4. Rode `pytest -q`.
5. Rode `python -m src --inbox ./examples/inbox_valid.json --no-outbox --report reports/demo_report.json` depois de configurar `EMAIL_ADVOGADO`.
6. Consulte `docs/git-history.md` para ver uma sugestão de histórico profissional com Conventional Commits.

## Skills demonstradas

- Python moderno (`dataclass`, `Path`, type hints, `from __future__ import annotations`).
- Manipulação de OOXML via `python-docx`.
- Desenho de pipelines determinísticos com exit codes acionáveis.
- Modelagem por contratos (JSON) em vez de SDKs.
- Testes automatizados com fixtures de `.docx`.
- Cuidado explícito com LGPD e falsa prontidão jurídica.
- Documentação técnica em pt-BR clara e navegável.

## Stack em uma linha

Python 3.11+ · `python-docx` · `pytest` · GitHub Actions · Conventional Commits · MIT.

## Contato

GitHub: [@1kookieh](https://github.com/1kookieh)

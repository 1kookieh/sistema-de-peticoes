# Historico Git sugerido

Este arquivo descreve uma sequencia profissional de commits para apresentar o projeto com clareza em entrevistas, revisoes tecnicas e portfolio.

## Sequencia recomendada

- `chore: initialize project structure`
- `feat: add docx formatting pipeline`
- `feat: add deterministic docx validation`
- `feat: add json inbox and outbox pipeline`
- `fix: block invalid legal documents from outbox`
- `feat: add validation profiles and compliance reports`
- `test: add automated pipeline coverage`
- `docs: improve legal, architecture and recruiter documentation`
- `chore: configure ci and github templates`
- `chore: prepare release v1.0.0`

## Comandos uteis

```bash
git add .
git commit -m "docs: improve project documentation"
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin main
git push origin v1.0.0
```

## Boas praticas

- Prefira commits pequenos, coesos e revisaveis.
- Use Conventional Commits: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`.
- Nao versione `.env`, arquivos `.docx`, filas locais, relatorios reais ou qualquer dado de cliente.
- Antes de criar uma tag, rode `python -m compileall config.py src tests`, `pytest -q` e um fluxo de exemplo.

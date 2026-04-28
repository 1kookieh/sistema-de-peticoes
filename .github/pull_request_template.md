## Descrição

Explique o que muda e por quê. Relacione a issue, se houver (`Closes #123`).

## Tipo de mudança

- [ ] `feat` — nova funcionalidade
- [ ] `fix` — correção de bug
- [ ] `docs` — documentação
- [ ] `refactor` — reorganização sem mudança de comportamento
- [ ] `chore` — infra, CI, dependências
- [ ] `test` — testes

## Checklist

- [ ] O título segue [Conventional Commits](https://www.conventionalcommits.org/pt-br/).
- [ ] Rodei `python -m compileall config.py src tests`.
- [ ] Rodei `pytest -q`.
- [ ] Rodei `ruff check .` quando alterei Python.
- [ ] Rodei `mypy config.py src/infra/llm` quando alterei configuração ou LLM.
- [ ] Rodei `pip-audit -r requirements.txt --strict` quando alterei dependências.
- [ ] Rodei `bandit -q -r src` quando alterei backend, segurança ou LLM.
- [ ] Rodei `node --check web/ui.js` e/ou `node --check web/render.js` quando alterei front-end.
- [ ] Se alterei regra de formatação, também atualizei `src/core/validation/docx.py`, `src/infra/docx_render.py` e o prompt correspondente quando necessário.
- [ ] Atualizei o `CHANGELOG.md` (seção `Unreleased`) quando a mudança é visível ao usuário.
- [ ] Atualizei a documentação em `docs/` quando necessário.
- [ ] Não adicionei `.env`, `output/`, `reports/`, caches, chaves de API ou dados reais.

## Teste manual

Descreva o que você executou e qual foi a saída.

```
...
```

## Observações

Qualquer ponto que precise de atenção especial do revisor.

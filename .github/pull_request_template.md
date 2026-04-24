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
- [ ] Rodei `python -m py_compile src/*.py config.py` sem erros.
- [ ] Rodei o pipeline de ponta a ponta com `teste_inbox.json` e conferi a saída.
- [ ] Se alterei regra de formatação, também atualizei `validar_docx.py` e o prompt correspondente.
- [ ] Atualizei o `CHANGELOG.md` (seção `Unreleased`) quando a mudança é visível ao usuário.
- [ ] Atualizei a documentação em `docs/` quando necessário.

## Teste manual

Descreva o que você executou e qual foi a saída.

```
...
```

## Observações

Qualquer ponto que precise de atenção especial do revisor.

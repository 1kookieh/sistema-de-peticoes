# Contribuindo com o Sistema de Petições

Obrigado pelo interesse em contribuir! Este documento descreve o fluxo esperado.

## Como reportar bugs

Abra uma [issue](https://github.com/1kookieh/sistema-de-peticoes/issues/new?template=bug_report.md) usando o template de bug. Quanto mais contexto (trecho do `.docx`, saída do validador, versão do Python), mais rápido conseguimos reproduzir.

## Como sugerir melhorias

Use o template de [feature request](https://github.com/1kookieh/sistema-de-peticoes/issues/new?template=feature_request.md). Descreva o problema que resolve, não apenas a solução.

## Fluxo de desenvolvimento

1. **Fork** do repositório e clone local.
2. Crie uma branch a partir de `main` com nome descritivo:
   ```bash
   git checkout -b feat/pdf-export
   ```
3. Faça commits pequenos e focados seguindo [Conventional Commits](https://www.conventionalcommits.org/pt-br/):
   - `feat:` nova funcionalidade
   - `fix:` correção de bug
   - `docs:` documentação
   - `chore:` infra, build, dependências
   - `refactor:` mudança interna sem alterar comportamento
   - `test:` testes
4. Rode localmente antes de abrir PR:
   ```bash
   python -m py_compile src/*.py config.py
   INBOX_MOCK_PATH=./teste_inbox.json python -m src.main
   ```
5. Abra o PR preenchendo o template. Vincule a issue quando houver.

## Padrões de código

- **Python 3.11+** (usamos sintaxe de tipos moderna e `match` quando agregar valor).
- **Type hints** em toda função pública.
- **Docstrings** curtas em pt-BR em módulos, classes e funções públicas.
- **Imports** organizados: stdlib → terceiros → locais.
- **Sem dependências novas** sem discussão prévia na issue — mantemos a superfície mínima.

## Regras específicas de domínio

- **Não adicione regras de formatação silenciosamente.** Toda nova regra precisa:
  1. Estar documentada em `prompts/prompt_formatacao_word.md` (fonte humana).
  2. Ter verificação correspondente em `src/validar_docx.py` (fonte executável).
- **Nada de APIs pagas no core.** Integrações com LLMs ou serviços externos devem ficar em módulos ou projetos separados, consumindo as filas JSON.

## Revisão

Reviews focam em: clareza do código, aderência ao padrão forense, impacto nas regras de validação e qualidade da documentação. Testes automatizados ainda estão no [roadmap](docs/roadmap.md) — até lá, descreva o teste manual feito no PR.

## Conduta

Seja gentil. Problemas são com o código, não com as pessoas.

# Contribuindo

Obrigado por considerar contribuir com o `Sistema de Petições`.

Este projeto lida com documentos jurídicos e potenciais dados sensíveis. Toda contribuição deve preservar segurança, revisão humana e clareza técnica.

## Como Preparar o Ambiente

```bash
git clone https://github.com/1kookieh/sistema-de-peticoes.git
cd sistema-de-peticoes
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Linux/macOS:

```bash
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

## Antes de Abrir PR

Rode:

```bash
python -m compileall config.py src tests
pytest -q
ruff check .
mypy config.py src/infra/llm
pip-audit -r requirements.txt --strict
bandit -q -r src
```

O `mypy` é gradual neste momento: valide `config.py` e `src/infra/llm`, que são o escopo configurado no CI.

Se alterar interface web, também valide sintaxe dos módulos JavaScript alterados:

```bash
node --check web/ui.js
node --check web/render.js
```

## Padrão de Branch e Commit

Use nomes descritivos:

```bash
git checkout -b feat/llm-provider
git checkout -b fix/docx-validation
git checkout -b docs/readme-usage
```

Commits recomendados:

- `feat:` nova funcionalidade;
- `fix:` correção de bug;
- `docs:` documentação;
- `test:` testes;
- `refactor:` mudança interna sem alterar comportamento;
- `chore:` manutenção.

## Regras de Código

- Preserve a arquitetura em camadas.
- Não coloque chamadas de LLM diretamente nas rotas.
- Não remova validações sem teste e justificativa.
- Não adicione dependência nova sem necessidade clara.
- Atualize documentação quando mudar contrato, comando ou fluxo.
- Adicione testes para mudanças em API, pipeline, DOCX, prompts ou validação.

## Regras para Prompts

- Use apenas dados fictícios.
- Não inclua nomes reais, CPF, RG, OAB, NB, DER ou documentos reais.
- Separe instruções jurídicas de instruções de formatação.
- Não peça para a IA inventar fatos ou jurisprudência.
- Ao alterar prompts, rode os testes.

## Segurança e LGPD

Não commitar:

- `.env`;
- chaves de API;
- DOCX real;
- relatórios reais;
- inbox/outbox/status com dados reais;
- prints com dados sensíveis.

Leia [SECURITY.md](SECURITY.md) e [docs/legal-limitations.md](docs/legal-limitations.md).

## Pull Requests

Ao abrir PR:

1. Explique o problema resolvido.
2. Liste arquivos principais alterados.
3. Informe testes executados.
4. Destaque riscos ou limitações.
5. Informe se a mudança afeta IA/LLM, prompts, DOCX, API ou segurança.

## Conduta

Seja objetivo e respeitoso. Reviews devem focar no código, documentação, segurança e confiabilidade do sistema.

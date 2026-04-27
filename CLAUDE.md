# CLAUDE.md — Integração Supervisionada com Claude

Este arquivo orienta o uso do Claude ou de agentes Claude com o **Sistema de Petições**. O projeto gera e valida documentos jurídicos `.docx` em ambiente local, usando prompts versionados e validações determinísticas. O Claude pode apoiar a preparação da minuta, mas a revisão humana por advogado continua obrigatória.

## Princípios obrigatórios

- Não inventar fatos, documentos, datas, números de benefício, OAB, valores ou jurisprudência.
- Não afirmar que uma peça está pronta para protocolo.
- Não substituir análise jurídica de mérito.
- Sinalizar lacunas, inconsistências e pontos que exigem revisão humana.
- Preservar dados sensíveis e evitar expor conteúdo de peças, relatórios e filas locais.
- Usar os prompts versionados do repositório como fonte principal de orientação.

## Prompts oficiais

| Arquivo | Função |
|---|---|
| `prompts/prompt_peticao.md` | Orienta a estrutura jurídica, limites, catálogo de peças, tom e cautelas de geração. |
| `prompts/prompt_formatacao_word.md` | Orienta o padrão formal esperado para Word/DOCX. |

O pipeline Python carrega e audita esses dois prompts. O relatório registra `prompt_usage` com nome, caminho e hash SHA-256.

## Fluxo recomendado com Claude

```text
Entrada do usuário ou arquivo
  -> Claude prepara minuta conforme prompt_peticao.md
  -> Sistema detecta tipo de peça e perfil formal
  -> Sistema valida texto antes de renderizar
  -> Sistema aplica prompt_formatacao_word.md como contrato de formatação
  -> Sistema gera DOCX com python-docx
  -> Sistema valida DOCX e gera relatório
  -> Advogado revisa antes de qualquer uso real
```

## Como rodar o projeto

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m src --setup
uvicorn src.interfaces.api:app --host 127.0.0.1 --port 8000 --reload
```

Acesse `http://127.0.0.1:8000`.

## Comandos de validação

```bash
python -m compileall config.py src tests
pytest -q
python -m src --inbox examples/inbox_valid.json --profile judicial-inicial-jef --strict --no-outbox --report reports/demo_report.json
```

## Arquitetura atual

```text
src/
  core/            domínio, tipos de peça, perfis, prompts e validações
  adapters/        leitura de inbox, escrita de outbox e extração de arquivos
  infra/           DOCX, locks, logging e estado local
  interfaces/      API, CLI e desktop
  orchestration/   pipeline, relatórios, retenção e setup
```

## Regras para agentes Claude

Antes de alterar código:

1. Ler `README.md`, `CLAUDE.md` e o arquivo afetado.
2. Rodar ou consultar `git status`.
3. Entender se a mudança afeta geração, validação, API, front-end, prompts ou documentação.
4. Fazer alterações pequenas e verificáveis.

Depois de alterar código:

1. Rodar `python -m compileall config.py src tests`.
2. Rodar `pytest -q`.
3. Se mexer na interface, abrir `http://127.0.0.1:8000` e verificar console/fluxo básico.
4. Informar limitações e pendências humanas.

## Segurança e dados sensíveis

Nunca versionar:

- `.env`
- `output/*.docx`
- `reports/*.json`
- `reports/*.html`
- `mcp_inbox.json`
- `mcp_outbox.json`
- `mcp_status.json`
- documentos reais de clientes

Use apenas fixtures fictícias em `examples/` e `tests/`.

## Limites jurídicos

O sistema pode validar forma, estrutura e riscos evidentes. Ele não decide:

- competência;
- prazo;
- tese jurídica correta;
- cálculo final;
- suficiência de prova;
- estratégia processual;
- viabilidade de protocolo.

Esses pontos exigem advogado responsável.

## Boas práticas de prompt engineering

Ao usar Claude para gerar uma minuta:

- delimite o tipo de peça, partes, fatos, documentos e objetivo;
- destaque lacunas explicitamente;
- peça saída em texto limpo, sem Markdown excessivo, quando o destino for DOCX;
- evite inventar citações ou jurisprudência;
- peça checklist de revisão separado da peça;
- peça que dúvidas sejam marcadas como `[REVISAR]`.

## Checklist final para agentes

- [ ] Não inventei dados.
- [ ] Preservei revisão humana obrigatória.
- [ ] Não expus secrets nem arquivos sensíveis.
- [ ] Mantive `/api/v1` como contrato da API.
- [ ] Mantive prompts versionados como fonte de orientação.
- [ ] Rodei compile/testes ou expliquei por que não rodei.
- [ ] Atualizei documentação quando o comportamento mudou.

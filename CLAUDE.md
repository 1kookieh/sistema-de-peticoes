# CLAUDE.md — Integração Supervisionada com Claude

Este arquivo orienta o uso do Claude ou de agentes Claude com o **Sistema de Petições**. O projeto **cria, valida e renderiza** documentos jurídicos `.docx` em ambiente local. O fluxo principal é AI-first: `LLM_REQUIRED=true` e o provider vem da configuração/allowlist do backend (`mock` para desenvolvimento/testes, `ollama` para IA local e `openai`/`anthropic` para uso externo controlado).

Quando IA estiver ativada, `prompt_peticao.md` e `prompt_formatacao_word.md` compõem o prompt final, a resposta deve ser JSON estruturado e o DOCX é renderizado a partir dessa estrutura validada. A revisão humana por advogado responsável continua obrigatória antes de qualquer protocolo.

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

O pipeline Python carrega e audita esses dois prompts. O relatório registra `prompt_usage` com nome, caminho e hash SHA-256. Em modo IA, o relatório também registra `llm` com provedor, modelo, hash do prompt final e flags de mock/fallback, sem salvar o prompt completo por padrão.

## Redaction e consentimento de IA externa

Providers externos, como `openai` e `anthropic`, exigem consentimento explícito por requisição (`llm.consent_external_provider=true`, campo de upload `llm_consent_external_provider=true` ou flag CLI `--llm-consent-external`). Sem isso, o pipeline retorna `llm_error` e não chama a API externa. `ollama` é tratado como provider local e não exige chave externa.

Antes de chamar um provider externo, o backend aplica mascaramento textual em padrões como CPF, CNPJ, NIT, NB, RG, CEP, telefone e e-mail. Isso reduz exposição acidental, mas não remove nomes próprios nem todos os fatos sensíveis. Agentes não devem afirmar anonimização completa.

## Fluxo recomendado com Claude

```text
Entrada do usuário ou arquivo
  -> provider LLM configurado no backend gera JSON estruturado usando os prompts versionados
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
ruff check .
mypy config.py src/infra/llm
pip-audit -r requirements.txt --strict
bandit -q -r src
python -m src --inbox examples/inbox_valid.json --profile judicial-inicial-jef --strict --no-outbox --report reports/demo_report.json
```

O `mypy` ainda é gradual; o escopo validado no CI é `config.py` e `src/infra/llm`.

## Docker e token da API

O `Dockerfile` define `API_REQUIRE_TOKEN=1`. Ao rodar em container, defina `API_TOKEN` e use o mesmo valor no header `X-API-Token` para rotas sensíveis. Não rode container sem token fora de `127.0.0.1` ou demonstração local isolada.

## Arquitetura atual

```text
src/
  core/            domínio, tipos de peça, perfis, prompts e validações
  adapters/        leitura de inbox, escrita de outbox e extração de arquivos
  infra/           DOCX, LLM, locks, logging e estado local
  interfaces/      API, CLI e desktop
  orchestration/   pipeline, relatórios, retenção e setup
```

## Diretrizes comportamentais para agentes

Estas diretrizes reduzem erros comuns de agentes LLM. Elas priorizam cautela sobre velocidade; para tarefas triviais, use julgamento.

### 1. Pense antes de codar

Nao assuma, nao esconda confusao e explicite tradeoffs antes de implementar:

- Declare suposicoes explicitamente. Se estiver incerto, pergunte.
- Se houver multiplas interpretacoes, apresente-as em vez de escolher silenciosamente.
- Se existir uma abordagem mais simples, diga. Conteste quando fizer sentido.
- Se algo estiver confuso, pare, nomeie a duvida e pergunte.

### 2. Simplicidade primeiro

Use o minimo de codigo que resolve o problema. Nada especulativo.

- Nao adicione funcionalidades alem do pedido.
- Nao crie abstracoes para codigo de uso unico.
- Nao adicione flexibilidade ou configurabilidade que nao foi solicitada.
- Nao escreva tratamento de erro para cenarios impossiveis.
- Se uma mudanca ficar muito maior do que precisa, simplifique antes de continuar.

Pergunte: um engenheiro senior acharia isto overengineering? Se sim, reduza.

### 3. Mudancas cirurgicas

Toque somente no necessario e limpe apenas a sujeira criada pela propria mudanca.

- Nao melhore codigo, comentarios ou formatacao adjacente sem relacao com o pedido.
- Nao refatore codigo nao relacionado.
- Siga o estilo existente, mesmo que voce fizesse diferente.
- Se notar codigo morto nao relacionado, mencione em vez de apagar.
- Remova imports, variaveis, funcoes e arquivos que suas proprias mudancas tornaram inutilizados.

Cada linha alterada deve apontar diretamente para o pedido do usuario.

### 4. Execucao orientada por objetivo

Transforme tarefas em metas verificaveis e itere ate validar.

- "Adicionar validacao" significa criar ou ajustar testes para entradas invalidas e faze-los passar.
- "Corrigir bug" significa reproduzir com teste ou checagem direcionada e depois validar a correcao.
- "Refatorar X" significa preservar comportamento e rodar os testes relevantes antes de finalizar.

Para tarefas em varias etapas, declare um plano curto com verificacao:

```text
1. [Etapa] -> verificar: [checagem]
2. [Etapa] -> verificar: [checagem]
3. [Etapa] -> verificar: [checagem]
```

Estas diretrizes estao funcionando quando os diffs ficam menores, reescritas sao menos frequentes e perguntas de esclarecimento acontecem antes de erros de implementacao.

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

Em testes e desenvolvimento, prefira `LLM_PROVIDER=mock`. Não envie dados reais para providers externos. Redaction é parcial e não deve ser descrita como anonimização completa.

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

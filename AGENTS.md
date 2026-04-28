# AGENTS.md

Instrucoes para Codex e outros agentes de IA trabalhando neste repositorio.

## Project Overview

Este projeto e um sistema local de geracao, validacao, renderizacao e auditoria de documentos juridicos `.docx`.

O pipeline recebe texto pronto ou texto extraido de arquivos, detecta tipo de peca/perfil formal, opcionalmente chama LLM configurado, valida riscos formais, renderiza DOCX com `python-docx` e grava relatorios JSON/HTML. O fluxo padrao usa `LLM_PROVIDER=none` e nao envia dados para servicos externos.

Modulos principais:

- `src/core/`: dominio puro, perfis, tipos de peca, inferencia, prompts e validacoes.
- `src/adapters/`: leitura de inbox, escrita de outbox e extracao de arquivos.
- `src/infra/`: renderizacao DOCX, providers LLM, locks, logging e estado local.
- `src/interfaces/`: API FastAPI, CLI e interface desktop Tkinter.
- `src/orchestration/`: pipeline, relatorios, retencao e setup.
- `web/`: front-end local em HTML/CSS/JavaScript ESM.

## Tech Stack

- Backend/API: Python 3.11+, FastAPI, Pydantic Settings, Uvicorn.
- Documentos/IA: `python-docx`, `pypdf`, `pillow`, `pytesseract`, Jinja2, provider LLM HTTP.
- Frontend: HTML, CSS, JavaScript ES Modules, Service Worker.
- Desktop: Tkinter.
- Testes: pytest, httpx, FastAPI TestClient, golden files estruturais.
- DevOps: Dockerfile e GitHub Actions em `.github/workflows/ci.yml`.

Nao adicione tecnologias, frameworks ou dependencias sem necessidade clara e sem atualizar testes/documentacao relacionados.

## Repository Structure

```text
.
+-- src/
|   +-- core/
|   +-- adapters/
|   +-- infra/
|   +-- interfaces/
|   +-- orchestration/
+-- web/
+-- tests/
+-- docs/
+-- prompts/
+-- templates/
+-- examples/
+-- README.md
+-- CLAUDE.md
+-- CONTRIBUTING.md
+-- requirements.txt
+-- requirements-dev.txt
+-- Dockerfile
```

Pastas de runtime como `output/`, `reports/` e arquivos `mcp_*.json` podem conter dados sensiveis. Nao trate esses arquivos como fixtures publicas.

## Setup Instructions

Use os comandos reais do projeto:

```bash
python -m venv .venv
pip install -r requirements.txt
python -m src --setup
```

No Windows PowerShell, a ativacao documentada e:

```powershell
.\.venv\Scripts\Activate.ps1
```

Para desenvolvimento com testes:

```bash
pip install -r requirements-dev.txt
```

Use `.env.example` como modelo para `.env`. Nunca copie ou exponha valores de `.env` real.

## Development Commands

```bash
# API + web local
uvicorn src.interfaces.api:app --host 127.0.0.1 --port 8000 --reload

# CLI em lote
python -m src --inbox examples/inbox_valid.json --profile judicial-inicial-jef --strict --no-outbox --report reports/demo_report.json

# Validar um DOCX gerado
python -m src.core.validation.docx output/nome-do-arquivo.docx --profile judicial-inicial-jef

# Interface desktop
python -m src.interfaces.desktop

# Docker
docker build -t sistema-peticoes .
docker run --rm -p 8000:8000 -e API_TOKEN=troque-este-token sistema-peticoes
```

O Dockerfile define `API_REQUIRE_TOKEN=1` por padrao. Para demonstracao local sem token, defina explicitamente `-e API_REQUIRE_TOKEN=false`; nao use esse modo em rede.

Comandos de qualidade confirmados:

```bash
ruff check .
mypy config.py src/infra/llm
pip-audit -r requirements.txt --strict
bandit -q -r src
```

`mypy` ainda e gradual: o CI valida `config.py` e `src/infra/llm`, nao todo `src/`.

## Testing Instructions

Comandos confirmados:

```bash
python -m compileall config.py src tests
pytest -q
```

Para alteracoes focadas, rode tambem o teste especifico relacionado. Exemplos:

```bash
pytest tests/test_api_desktop_reporting.py -q
pytest tests/test_main_pipeline.py -q
pytest tests/test_docx_validation.py -q
```

Se alterar front-end, valide sintaxe JS quando Node estiver disponivel:

```bash
node --check web/ui.js
node --check web/render.js
```

Se nao puder rodar algum comando, diga claramente no resumo final. Nao afirme que testes passaram se nao foram executados.

## Code Style and Conventions

- Python usa type hints, funcoes pequenas quando possivel e imports na ordem stdlib, terceiros, locais.
- Mantenha docstrings curtas em pt-BR quando adicionar modulos/funcoes publicas.
- Preserve a arquitetura em camadas; nao mova regras de dominio para `interfaces/` nem detalhes de API para `core/`.
- API publica usa `/api/v1/*`. Nao recrie rotas antigas `/api/*`.
- Front-end usa JavaScript ESM modular (`web/api.js`, `web/ui.js`, `web/render.js`, `web/state/store.js`).
- Commits documentados no `CONTRIBUTING.md` seguem Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`).
- Ao fazer commit quando solicitado, use o autor Git configurado do usuario e nao adicione `Co-authored-by` do Codex.

Siga o estilo dos arquivos proximos antes de introduzir nova convencao.

## Architecture Notes

Fluxo principal:

```text
entrada do usuario/arquivo
-> extracao de texto ou OCR
-> inferencia de tipo de peca e perfil
-> opcional: LLM provider gera JSON estruturado validado
-> validacao textual
-> renderizacao DOCX
-> validacao estrutural do DOCX
-> relatorio JSON/HTML e historico local
```

`prompts/prompt_peticao.md` e `prompts/prompt_formatacao_word.md` sao contratos versionados e auditados por hash no relatorio. No modo LLM, esses prompts compoem o prompt final; o prompt completo nao deve ser salvo por padrao.

Ao alterar geracao/validacao:

- Atualize testes em `tests/`.
- Preserve revisao humana obrigatoria.
- Nao afirme que a peca esta pronta para protocolo.
- Nao permita comentarios internos, placeholders ou marcas de IA no modo final.

## Environment Variables

Variaveis confirmadas em `.env.example` e `config.py`:

- `EMAIL_ADVOGADO`: remetente/advogado responsavel em fluxos de CLI/outbox.
- `API_TOKEN`: protege rotas sensiveis quando preenchido.
- `API_REQUIRE_TOKEN`: exige token configurado quando verdadeiro; no Docker fica `1` por padrao.
- `API_ALLOWED_ORIGINS`: origens permitidas para chamadas mutadoras.
- `REMETENTES_AUTORIZADOS`: lista de remetentes aceitos.
- `MAX_JSON_BYTES`: limite de JSON de entrada.
- `GMAIL_LABEL_PROCESSADO`: label usada no fluxo de email/mock.
- `VALIDATION_PROFILE`: perfil formal padrao.
- `RETENTION_ENABLED` e `RETENTION_*_DAYS`: politica de retencao de runtime.
- `LLM_MODE`, `LLM_PROVIDER`, `LLM_MODEL`: selecionam modo/provedor/modelo de IA.
- `LLM_TEMPERATURE`, `LLM_MAX_OUTPUT_TOKENS`, `LLM_TIMEOUT_SECONDS`, `LLM_RETRY_ATTEMPTS`: parametros do provider.
- `LLM_REQUIRE_STRUCTURED_OUTPUT`, `LLM_FALLBACK_ENABLED`, `LLM_LOG_PROMPT`: controles de seguranca/auditoria.
- `OPENAI_API_KEY`: chave para provider `openai`; nunca versionar.
- `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `OPENROUTER_API_KEY`, `OLLAMA_BASE_URL`: reservados para providers futuros/opcionais.

Nunca leia, copie ou versione `.env` real. Use apenas placeholders de `.env.example`.

## API and Backend Guidelines

- Rotas ficam em `src/interfaces/api.py`.
- Orquestracao do fluxo fica em `src/orchestration/pipeline.py`.
- Validacoes de texto/DOCX ficam em `src/core/validation/`.
- Tipos de peca e inferencia ficam em `src/core/piece_types.py` e `src/core/piece_inference.py`.
- Renderizacao DOCX fica em `src/infra/docx_render.py`.
- Integracao LLM fica em `src/infra/llm/`; nao coloque chamadas de IA diretamente nas rotas.

Regras:

- Valide toda entrada de usuario.
- Preserve `_safe_file`/protecoes contra path traversal em downloads e relatorios.
- Preserve CORS, Origin check, rate limit e `API_TOKEN`.
- Nao exponha conteudo sensivel em logs, relatorios publicos ou fixtures.
- Nao faca fallback silencioso para mock quando o usuario pediu provider real; fallback so com `LLM_FALLBACK_ENABLED=true`.
- Se mudar contrato de API, atualize front-end, testes e `docs/api.md`.

## Frontend Guidelines

- HTML principal: `web/index.html`.
- Estilos: `web/styles.css`.
- Bootstrap: `web/app.js`.
- Chamadas HTTP: `web/api.js`.
- Estado: `web/state/store.js`.
- Renderizacao: `web/render.js`.
- Eventos/DOM: `web/ui.js`.
- Service Worker: `web/sw.js`.

Ao alterar UI:

- Preserve acessibilidade basica: labels, foco visivel, `aria-live` para mensagens e nomes claros de botoes.
- Mantenha responsividade e linguagem clara para usuario juridico.
- Nao cacheie documentos, uploads, relatorios ou respostas sensiveis no Service Worker.
- Teste visualmente em `http://127.0.0.1:8000` quando possivel.

## Security Guidelines

- Nunca commite `.env`, tokens, senhas, documentos reais, relatorios reais ou dados de clientes.
- Trate `output/`, `reports/`, `mcp_inbox.json`, `mcp_outbox.json` e `mcp_status.json` como runtime sensivel.
- Use apenas dados ficticios em `examples/` e `tests/`.
- Nao reduza validacoes para "fazer passar" sem justificativa tecnica.
- Nao exponha CPF, NIT, endereco, e-mail ou conteudo juridico real em logs, screenshots, fixtures ou README.
- Revise novas dependencias com cautela; mantenha a superficie minima.
- Nao execute acoes destrutivas como limpar runtime real, apagar relatorios ou resetar estado sem pedido explicito.

## Agent Workflow

Antes de alterar:

1. Rode `git status --short`.
2. Leia `README.md`, este `AGENTS.md` e os arquivos afetados.
3. Verifique se ha alteracoes pendentes do usuario e nao as sobrescreva.
4. Entenda se a mudanca afeta API, pipeline, DOCX, prompts, front-end ou docs.

Durante a alteracao:

- Faca mudancas pequenas e coesas.
- Nao refatore arquitetura sem pedido explicito.
- Nao altere arquivos fora do escopo.
- Nao adicione dependencia sem necessidade real.
- Atualize testes quando mudar comportamento.
- Atualize docs quando mudar contrato, comando ou fluxo de uso.

Antes de finalizar:

- Rode `python -m compileall config.py src tests`.
- Rode `pytest -q` ou testes focados quando fizer sentido.
- Se mexer no front, rode `node --check` nos arquivos JS alterados quando Node estiver disponivel.
- Se mexer em seguranca, dependencias ou LLM, rode tambem `ruff`, `mypy` gradual, `pip-audit` e `bandit` quando disponiveis.
- Revise `git diff`.
- Informe validacoes executadas e limitacoes.

## Review and Quality Checklist

- [ ] A alteracao respeita o escopo solicitado.
- [ ] O codigo segue o padrao dos arquivos proximos.
- [ ] O contrato `/api/v1` foi preservado ou documentado.
- [ ] Validacoes juridicas/formais nao foram removidas sem justificativa.
- [ ] Modo final nao permite placeholders, comentarios internos ou marcas de IA.
- [ ] Testes relevantes foram executados ou a impossibilidade foi explicada.
- [ ] Nenhum segredo ou dado sensivel foi exposto.
- [ ] Documentacao foi atualizada quando necessario.
- [ ] O diff foi revisado antes da resposta final.
- [ ] Riscos e pendencias foram informados com clareza.

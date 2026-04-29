# Guia de Uso

Este guia descreve o fluxo atual do sistema: criacao de minutas juridicas DOCX com IA obrigatoria no pipeline principal.

## 1. Iniciar API e Web

```bash
uvicorn src.interfaces.api:app --host 127.0.0.1 --port 8000 --reload
```

Abra:

```text
http://127.0.0.1:8000
```

## 2. Criar DOCX pela Interface Web

1. Escolha o tipo de documento ou deixe `Detectar automaticamente`.
2. Escolha o perfil formal ou deixe automatico.
3. Escolha o provider liberado pelo backend: `mock`, `ollama`, `openai` ou `anthropic`.
4. Cole o relato do caso ou envie arquivo.
5. Se escolher provider externo (`openai` ou `anthropic`), marque o consentimento.
6. Clique em `Criar documento com IA`.
7. Baixe o DOCX no card de resultado e revise manualmente.

Nao ha mais botao principal de triagem/validacao separada. As validacoes continuam internas ao fluxo de criacao.

## 3. Configuracao de IA

O backend continua sendo a fonte da verdade para IA. A interface so mostra providers permitidos pela allowlist:

```env
LLM_REQUIRED=true
LLM_ALLOW_MOCK=true
LLM_ALLOW_CLIENT_PROVIDER=true
LLM_CLIENT_ALLOWED_PROVIDERS=mock,ollama,openai,anthropic
LLM_PROVIDER=mock
LLM_MODEL=
```

Use `mock` em desenvolvimento e testes. Ele nao representa IA real e nao deve ser usado como prova de qualidade juridica.

## 4. Usar Ollama Local

Use `ollama` quando quiser IA local sem chave de API externa. Instale o Ollama, baixe um modelo e mantenha o servico ativo:

```env
LLM_PROVIDER=ollama
LLM_MODEL=llama3.1:8b
OLLAMA_BASE_URL=http://localhost:11434
```

## 5. Usar OpenAI

No `.env` local/controlado:

```env
LLM_REQUIRED=true
LLM_ALLOW_MOCK=false
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sua-chave-local
LLM_FALLBACK_ENABLED=false
```

## 6. Usar Anthropic / Claude

No `.env` local/controlado:

```env
LLM_REQUIRED=true
LLM_ALLOW_MOCK=false
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-haiku-latest
ANTHROPIC_API_KEY=sua-chave-local
LLM_FALLBACK_ENABLED=false
```

Cuidados para providers externos:

- nao use chave real em arquivos versionados;
- nao envie dados reais sem base legal/autorizacao;
- a interface e a API exigem consentimento explicito antes de enviar dados para provider externo;
- redaction e parcial e nao garante anonimizacao completa;
- revise a minuta antes de qualquer uso profissional.

## 7. Usar CLI

Ajuda:

```bash
python -m src --help
```

Processar exemplo com mock e sem outbox:

```bash
python -m src --inbox examples/inbox_valid.json --no-outbox --mock --report reports/demo_report.json
```

Processar com Ollama local:

```bash
python -m src --inbox examples/inbox_valid.json --no-outbox --llm-provider ollama --llm-model llama3.1:8b
```

Processar com Anthropic exige `ANTHROPIC_API_KEY` no `.env` e consentimento:

```bash
python -m src --inbox examples/inbox_valid.json --no-outbox --llm-provider anthropic --llm-consent-external
```

## 8. Validar DOCX Gerado

```bash
python -m src.core.validation.docx output/nome-do-arquivo.docx --profile judicial-inicial-jef
```

Essa validacao e auxiliar; a experiencia principal e criacao do documento.

## 9. Rodar Testes

```bash
python -m compileall config.py src tests
pytest -q
```

# Guia de Uso

Este guia descreve o fluxo atual: criacao de minutas juridicas DOCX com IA obrigatoria. Groq e o provider externo unico; `mock` e reservado para testes.

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
3. Cole o relato do caso ou envie arquivo.
4. Marque o consentimento de envio ao Groq.
5. Clique em `Criar documento com IA`.
6. Baixe o DOCX no card de resultado e revise manualmente.

Nao ha mais botao principal de triagem/validacao separada. As validacoes continuam internas ao fluxo de criacao.

## 3. Configuracao de IA

O backend e a fonte da verdade para IA. A interface mostra somente o provider Groq fixo:

```env
LLM_REQUIRED=true
LLM_ALLOW_MOCK=true
LLM_ALLOW_CLIENT_PROVIDER=false
LLM_CLIENT_ALLOWED_PROVIDERS=groq
LLM_MODE=groq
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile
GROQ_API_KEY=sua-chave-local
```

Use `mock` apenas em testes automatizados. Ele nao representa IA real.

## 4. Usar Groq

Crie a chave em `https://console.groq.com/keys` e configure no `.env` local:

```env
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile
GROQ_API_KEY=gsk_...
```

Cuidados:

- nao use chave real em arquivos versionados;
- nao envie dados reais sem base legal/autorizacao;
- interface e API exigem consentimento explicito antes de enviar dados ao Groq;
- redaction e parcial e nao garante anonimizacao completa;
- revise a minuta antes de qualquer uso profissional.

## 5. Usar CLI

Ajuda:

```bash
python -m src --help
```

Processar exemplo com mock e sem outbox:

```bash
python -m src --inbox examples/inbox_valid.json --no-outbox --mock --report reports/demo_report.json
```

Processar com Groq exige `GROQ_API_KEY` no `.env` e consentimento:

```bash
python -m src --inbox examples/inbox_valid.json --no-outbox --llm-consent-external
```

## 6. Validar DOCX Gerado

```bash
python -m src.core.validation.docx output/nome-do-arquivo.docx --profile judicial-inicial-jef
```

Essa validacao e auxiliar; a experiencia principal e criacao do documento.

## 7. Rodar Testes

```bash
python -m compileall config.py src tests
pytest -q
```

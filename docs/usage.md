# Guia de Uso

Este guia mostra os fluxos principais para usar o sistema localmente.

## 1. Iniciar API e Web

```bash
uvicorn src.interfaces.api:app --host 127.0.0.1 --port 8000 --reload
```

Abra:

```text
http://127.0.0.1:8000
```

## 2. Gerar DOCX pela Interface Web

1. Em `Peça desejada`, escolha uma peça ou deixe `Detectar automaticamente`.
2. Em `Perfil formal`, escolha um perfil ou deixe automático.
3. Em `Configurações avançadas`, escolha:
   - `Minuta revisável`;
   - ou `Final protocolável`.
4. Cole o texto do caso ou envie arquivo.
5. Clique em `Gerar DOCX`.
6. Baixe o arquivo pelo card de resultado.

Use `Validar texto` quando quiser apenas checar pendências sem criar DOCX.

## 3. Usar Sem IA

No `.env`:

```env
LLM_PROVIDER=none
```

Esse modo usa o texto informado pelo usuário e não chama provedor externo.

## 4. Usar IA Mock

No `.env`:

```env
LLM_PROVIDER=mock
```

Ou pela API:

```json
{
  "text": "texto do caso",
  "output_mode": "minuta",
  "llm": {
    "enabled": true,
    "provider": "mock"
  }
}
```

O mock serve para validar o fluxo técnico. Ele não representa IA real.

## 5. Usar OpenAI

No `.env`:

```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sua-chave-local
LLM_FALLBACK_ENABLED=false
```

Depois reinicie o servidor.

Cuidados:

- Não use chave real em arquivos versionados.
- Não envie dados reais sem autorização.
- Revise a peça antes de qualquer uso profissional.

## 6. Usar CLI

Ajuda:

```bash
python -m src --help
```

Processar exemplo sem outbox:

```bash
python -m src --inbox examples/inbox_valid.json --no-outbox --report reports/demo_report.json
```

Com IA mock:

```bash
python -m src --inbox examples/inbox_valid.json --no-outbox --llm --llm-provider mock --output-mode minuta
```

## 7. Validar DOCX Gerado

```bash
python -m src.core.validation.docx output/nome-do-arquivo.docx --profile judicial-inicial-jef
```

## 8. Rodar Testes

```bash
python -m compileall config.py src tests
pytest -q
```

No Windows, se `python` global não estiver no PATH:

```powershell
.\.venv\Scripts\python.exe -m compileall config.py src tests
.\.venv\Scripts\python.exe -m pytest -q
```

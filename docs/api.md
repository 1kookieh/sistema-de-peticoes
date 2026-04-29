# API REST

A API local usa FastAPI e expõe rotas versionadas em `/api/v1`. O endpoint principal cria documentos jurídicos com IA configurada no backend.

## Iniciar Servidor

```bash
uvicorn src.interfaces.api:app --host 127.0.0.1 --port 8000 --reload
```

URLs úteis:

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/api/v1/health
```

## Autenticação Local

Se `API_TOKEN` estiver preenchido, rotas sensíveis exigem:

```http
X-API-Token: valor-do-token
```

O `Dockerfile` usa `API_REQUIRE_TOKEN=1` por padrão. Ao rodar em container, defina `API_TOKEN` e envie o header em rotas sensíveis:

```bash
curl http://127.0.0.1:8000/api/v1/health
curl -H "X-API-Token: troque-este-token" http://127.0.0.1:8000/api/v1/reports
```

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Serve a interface web local |
| `GET` | `/api/v1/health` | Healthcheck |
| `POST` | `/api/v1/setup` | Cria/verifica pastas locais |
| `GET` | `/api/v1/profiles` | Lista perfis formais |
| `GET` | `/api/v1/piece-types` | Lista tipos de documento |
| `GET` | `/api/v1/limits` | Retorna limites e configuração pública da IA |
| `POST` | `/api/v1/documents` | Cria DOCX com IA a partir de texto |
| `POST` | `/api/v1/documents/upload` | Extrai texto de arquivos e cria DOCX com IA |
| `GET` | `/api/v1/documents/{filename}/download` | Baixa DOCX gerado |
| `GET` | `/api/v1/reports` | Lista relatórios locais, mantido para API/operador |
| `GET` | `/api/v1/reports/{filename}` | Abre relatório JSON ou HTML |

## Criar Documento por Texto

```bash
curl -X POST http://127.0.0.1:8000/api/v1/documents \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"Relato do caso para teste.\",\"output_mode\":\"minuta\"}"
```

Payload principal:

```json
{
  "text": "relato do caso",
  "profile_id": "auto",
  "piece_type_id": "auto",
  "output_mode": "minuta",
  "consent_external_provider": false,
  "llm": {
    "provider": "mock",
    "model": null,
    "consent_external_provider": false
  }
}
```

Campos:

- `text`: dados do caso ou conteúdo base.
- `piece_type_id`: ID de `/piece-types` ou `auto`.
- `profile_id`: ID de `/profiles` ou `auto`.
- `output_mode`: `minuta` ou `final`.
- `consent_external_provider`: obrigatório quando o provider escolhido for externo, como `openai` ou `anthropic`.
- `llm.provider`: opcional; aceito somente se estiver em `LLM_CLIENT_ALLOWED_PROVIDERS`. Use `mock`, `ollama`, `openai` ou `anthropic`.
- `llm.model`: opcional; se vazio, o backend usa `LLM_MODEL` ou o padrão do provider.
- `llm.enabled`: legado; não desativa IA quando `LLM_REQUIRED=true`.

`triagem` foi desativado no endpoint principal e retorna `422`.

## Upload

```bash
curl -X POST http://127.0.0.1:8000/api/v1/documents/upload \
  -F "files=@relato.pdf" \
  -F "output_mode=minuta" \
  -F "llm_provider=mock" \
  -F "llm_consent_external_provider=false"
```

Arquivos suportados:

- `.txt` e `.md` em UTF-8;
- `.docx`;
- `.pdf`;
- imagens suportadas pelo OCR configurado.

## IA / LLM

A criação é AI-first:

- `LLM_REQUIRED=true` faz todo documento passar pela camada LLM.
- `LLM_PROVIDER=mock` é usado em testes/desenvolvimento.
- `LLM_PROVIDER=openai` usa provider externo e exige `OPENAI_API_KEY`.
- `LLM_PROVIDER=anthropic` usa Anthropic/Claude e exige `ANTHROPIC_API_KEY`.
- `LLM_PROVIDER=ollama` usa IA local via `OLLAMA_BASE_URL` e não exige chave externa.
- Se `LLM_ALLOW_CLIENT_PROVIDER=true`, o cliente pode escolher apenas providers da allowlist `LLM_CLIENT_ALLOWED_PROVIDERS`.
- Provider, modelo, temperatura e timeout vêm do backend.

Antes do envio a providers externos, o backend aplica redaction parcial para reduzir exposição de CPF, CNPJ, NIT, NB, RG, CEP, telefone e e-mail quando detectados. Isso não garante anonimização completa.

Quando a escolha de provider estiver habilitada para o cliente, a API ainda valida tudo pelo backend e rejeita providers fora da allowlist; `none` não é caminho válido de criação.

## Resposta

Exemplo resumido:

```json
{
  "status": "ok_no_outbox",
  "problems": [],
  "document": "peticao_20260429_123456_api.docx",
  "download_url": "/api/v1/documents/peticao_20260429_123456_api.docx/download",
  "report_json_url": "/api/v1/reports/api_20260429_123456.json",
  "report_html_url": "/api/v1/reports/api_20260429_123456.html",
  "piece_type_inferred": true,
  "profile_inferred": true,
  "llm": {
    "used": true,
    "provider": "mock",
    "mock_used": true
  }
}
```

O prompt completo e chaves de API não são retornados.

## Erros Comuns

| Situação | Resposta esperada |
|---|---|
| Perfil inexistente | `422` |
| Arquivo não suportado | `422` |
| Texto sem UTF-8 válido | `422` |
| `output_mode=triagem` | `422` |
| Origem HTTP não autorizada | `403` |
| Token ausente/inválido | `401` |
| Rate limit local excedido | `429` |
| Provider real sem chave | Status `llm_error` no payload |
| Provider externo sem consentimento | Status `llm_error` no payload |

## Segurança Operacional

- A API foi desenhada para uso local.
- Não exponha em rede pública sem autenticação, TLS e política de retenção.
- O service worker não cacheia `/api/v1`, uploads, relatórios ou DOCX.
- Use dados fictícios em testes e demonstrações públicas.
- Use providers externos somente com autorização, consentimento explícito e revisão humana.

# API REST e Interfaces Locais

A API local usa FastAPI e expõe apenas rotas versionadas em `/api/v1`. As rotas antigas `/api/...` não são mantidas.

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

Se `API_REQUIRE_TOKEN=true` e `API_TOKEN` estiver vazio, a API retorna erro de configuração.

O `Dockerfile` usa `API_REQUIRE_TOKEN=1` por padrão. Ao rodar em container, defina `API_TOKEN` e envie o header em rotas sensíveis:

```bash
curl http://127.0.0.1:8000/api/v1/health
curl -H "X-API-Token: troque-este-token" http://127.0.0.1:8000/api/v1/reports
```

Os exemplos abaixo omitem o header apenas para o modo local padrão sem token.

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Serve a interface web local |
| `GET` | `/api/v1/health` | Healthcheck |
| `POST` | `/api/v1/setup` | Cria/verifica pastas locais |
| `GET` | `/api/v1/profiles` | Lista perfis formais |
| `GET` | `/api/v1/piece-types` | Lista tipos de peça |
| `GET` | `/api/v1/limits` | Retorna limites de texto, upload, DOCX e defaults LLM |
| `POST` | `/api/v1/documents` | Gera/valida DOCX a partir de texto |
| `POST` | `/api/v1/documents/upload` | Extrai texto de arquivos e gera/valida DOCX |
| `GET` | `/api/v1/documents/{filename}/download` | Baixa DOCX gerado |
| `GET` | `/api/v1/reports` | Lista relatórios e status locais |
| `GET` | `/api/v1/reports/{filename}` | Abre relatório JSON ou HTML |

## Geração por Texto

```bash
curl -X POST http://127.0.0.1:8000/api/v1/documents \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"Relato do caso para teste.\",\"output_mode\":\"minuta\"}"
```

Payload principal:

```json
{
  "text": "texto do caso ou da peça",
  "profile_id": "auto",
  "piece_type_id": "auto",
  "output_mode": "minuta",
  "remetente": "demo@example.com",
  "assunto": "Geração local",
  "llm": {
    "enabled": false,
    "provider": "none",
    "model": null,
    "consent_external_provider": false
  }
}
```

Campos opcionais:

- `piece_type_id`: use um ID da rota `/piece-types` ou `auto`.
- `profile_id`: use um ID da rota `/profiles` ou `auto`.
- `output_mode`: `minuta`, `final` ou `triagem`.
- `llm`: configura IA por requisição.
- `llm.consent_external_provider`: obrigatório quando o provider escolhido envia dados para fora do ambiente local, como `openai`.

## Modos de Saída

| Modo | Gera DOCX | Comportamento |
|---|---:|---|
| `minuta` | Sim | Aceita alertas formais não críticos e registra pendências |
| `final` | Sim, se válido | Bloqueia placeholders, marcas internas e pendências críticas |
| `triagem` | Não | Retorna diagnóstico sem renderizar documento |

## Upload

Arquivo único:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/documents/upload \
  -F "file=@peticao.docx" \
  -F "output_mode=minuta"
```

Múltiplos arquivos:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/documents/upload \
  -F "files=@relato.pdf" \
  -F "files=@observacoes.txt" \
  -F "profile_id=judicial-inicial-jef"
```

Arquivos suportados:

- `.txt` e `.md` em UTF-8;
- `.docx`;
- `.pdf`;
- imagens suportadas pelo OCR configurado.

Limites atuais são expostos por:

```text
GET /api/v1/limits
```

## IA / LLM

O padrão é `none`, sem envio externo.

Providers disponíveis:

| Provider | Uso | Chave |
|---|---|---|
| `none` | Modo local sem IA | Não |
| `mock` | Testes e desenvolvimento | Não |
| `openai` | API externa OpenAI | Sim, `OPENAI_API_KEY` |

Providers externos exigem consentimento explícito por requisição. Sem esse campo, a API não chama o provedor e retorna `llm_error` de forma controlada.

Exemplo com OpenAI:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/documents \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"Relato do caso para teste.\",\"output_mode\":\"minuta\",\"llm\":{\"enabled\":true,\"provider\":\"openai\",\"model\":\"gpt-4o-mini\",\"consent_external_provider\":true}}"
```

No upload, use o campo de formulário:

```bash
-F "llm_consent_external_provider=true"
```

Antes do envio a providers externos, o backend aplica mascaramento textual para reduzir exposição de CPF, CNPJ, NIT, NB, RG, CEP, telefone e e-mail quando esses padrões são detectados. O mascaramento não substitui revisão humana nem autorização adequada para tratamento de dados.

Exemplo com mock:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/documents \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"Relato do caso para teste.\",\"output_mode\":\"minuta\",\"llm\":{\"enabled\":true,\"provider\":\"mock\"}}"
```

Exemplo com upload e mock:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/documents/upload \
  -F "files=@relato.pdf" \
  -F "output_mode=minuta" \
  -F "llm_enabled=true" \
  -F "llm_provider=mock"
```

Metadados retornados em `llm`:

- `enabled`;
- `mode`;
- `provider`;
- `model`;
- `used`;
- `mock_used`;
- `fallback_used`;
- `prompt_files`;
- `prompt_hash`;
- `response_valid`;
- `tokens_input`;
- `tokens_output`;
- `latency_ms`;
- `error`;
- `redaction_applied`;
- `redaction_counts`;
- `consent_external_provider`.

O prompt completo e chaves de API não são retornados.

## Resposta

Exemplo resumido:

```json
{
  "status": "ok_no_outbox",
  "problems": [],
  "document": "peticao_20260428_123456_api.docx",
  "download_url": "/api/v1/documents/peticao_20260428_123456_api.docx/download",
  "report_json_url": "/api/v1/reports/api_20260428_123456.json",
  "report_html_url": "/api/v1/reports/api_20260428_123456.html",
  "piece_type_inferred": true,
  "profile_inferred": true,
  "llm": {
    "used": false,
    "provider": "none"
  }
}
```

## Erros Comuns

| Situação | Resposta esperada |
|---|---|
| Perfil inexistente | `422` |
| Arquivo não suportado | `422` |
| Texto sem UTF-8 válido | `422` |
| Origem HTTP não autorizada | `403` |
| Token ausente/inválido | `401` |
| Rate limit local excedido | `429` |
| Provider real sem chave | Status `llm_error` no payload |
| Provider externo sem consentimento | Status `llm_error` no payload |

## Segurança Operacional

- A API foi desenhada para uso local.
- Não exponha em rede pública sem autenticação, TLS e política de retenção.
- O service worker não cacheia `/api/v1`, uploads, relatórios ou DOCX.
- Imagens são usadas para OCR e não são anexadas automaticamente ao `.docx`.
- Use dados fictícios em demonstrações públicas.
- Use providers externos somente com autorização, consentimento explícito na requisição e revisão humana.

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
    "model": null
  }
}
```

Campos opcionais:

- `piece_type_id`: use um ID da rota `/piece-types` ou `auto`.
- `profile_id`: use um ID da rota `/profiles` ou `auto`.
- `output_mode`: `minuta`, `final` ou `triagem`.
- `llm`: configura IA por requisição.

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
- `error`.

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

## Segurança Operacional

- A API foi desenhada para uso local.
- Não exponha em rede pública sem autenticação, TLS e política de retenção.
- O service worker não cacheia `/api/v1`, uploads, relatórios ou DOCX.
- Imagens são usadas para OCR e não são anexadas automaticamente ao `.docx`.
- Use dados fictícios em demonstrações públicas.

# API REST e interfaces locais

Este projeto possui três formas de uso local sobre o mesmo pipeline supervisionado: CLI, API/front-end web e interface desktop. Nenhuma delas substitui revisão jurídica humana.

## Escolha de front-end

A interface web usa HTML, CSS e JavaScript puro em `web/`, agora modularizado em:

- `web/api.js`: chamadas HTTP para `/api/v1`;
- `web/state/store.js`: estado global, tema, limites e token;
- `web/render.js`: templates e escaping;
- `web/ui.js`: DOM, eventos, validação visual e acessibilidade;
- `web/app.js`: bootstrap e registro do service worker.

Essa escolha evita Node.js, bundler ou build, reduz dependências e mantém o projeto fácil de demonstrar em ambiente limpo.

## Executar API local

```bash
uvicorn src.interfaces.api:app --host 127.0.0.1 --port 8000 --reload
```

Abra `http://127.0.0.1:8000`.

## Endpoints

As rotas antigas `/api/...` foram removidas. A API pública local usa somente `/api/v1/...`.

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Entrega o front-end local |
| `GET` | `/api/v1/health` | Healthcheck simples |
| `POST` | `/api/v1/setup` | Cria `output/` e `reports/` e valida recursos essenciais |
| `GET` | `/api/v1/profiles` | Retorna `{items, default}` com perfis formais |
| `GET` | `/api/v1/piece-types` | Lista tipos de peça agrupados conforme o prompt jurídico |
| `GET` | `/api/v1/limits` | Expõe limites de texto, upload e DOCX |
| `POST` | `/api/v1/documents` | Gera `.docx`, valida e grava relatórios JSON/HTML |
| `POST` | `/api/v1/documents/upload` | Extrai texto de `.txt`, `.md`, `.docx`, `.pdf` ou imagem e gera `.docx` |
| `GET` | `/api/v1/documents/{filename}/download` | Baixa documento gerado |
| `GET` | `/api/v1/reports` | Lista histórico local de relatórios e status |
| `GET` | `/api/v1/reports/{filename}` | Abre relatório JSON ou HTML |

## Detecção automática de peça e perfil

`piece_type_id` e `profile_id` são opcionais em `/api/v1/documents` e `/api/v1/documents/upload`.

- `piece_type_id` ausente, vazio ou `"auto"` faz o sistema inferir a peça por regras determinísticas em `src/core/piece_inference.py`.
- `profile_id` ausente, vazio ou `"auto"` usa o perfil sugerido pela peça detectada.
- Sem peça reconhecida, o fallback é `judicial-inicial-jef`.

A resposta inclui `piece_type_inferred`, `profile_inferred` e `profile { id, label, descricao }` para auditoria.

## Exemplos

Sem informar peça nem perfil:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/documents \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"PROCURAÇÃO AD JUDICIA...\\n\\nOutorgante fictício para teste.\"}"
```

Com peça e perfil explícitos:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/documents \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"[PREENCHER: texto fictício completo da peça]\",\"profile_id\":\"judicial-inicial-jef\",\"piece_type_id\":\"auxilio-incapacidade-temporaria\"}"
```

Upload de arquivo:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/documents/upload \
  -F "file=@peticao.docx"
```

Upload de múltiplos arquivos, incluindo imagem para OCR:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/documents/upload \
  -F "files=@relato.pdf" \
  -F "files=@print.png" \
  -F "profile_id=judicial-inicial-jef"
```

## Segurança operacional

- A API foi pensada para uso local.
- Não exponha em rede pública sem autenticação, TLS, logs controlados e política de retenção.
- Defina `API_TOKEN` no `.env` para exigir o cabeçalho `X-API-Token` nas rotas sensíveis.
- `output/`, `reports/`, inbox, outbox e status podem conter dados pessoais ou sensíveis.
- O front usa `no_outbox=True`, ou seja, gera e valida sem envio automático.
- O service worker cacheia somente assets estáticos; não cacheia `/api/v1`, uploads, relatórios ou DOCX.
- Imagens são usadas para OCR e não são anexadas ao `.docx` gerado.

## Docker

```bash
docker build -t sistema-peticoes .
docker run --rm -p 8000:8000 sistema-peticoes
```

Para uso com dados reais, monte volumes locais protegidos:

```bash
docker run --rm -p 8000:8000 \
  -v ./output:/app/output \
  -v ./reports:/app/reports \
  sistema-peticoes
```

# API REST e interfaces locais

Este projeto possui três formas de uso local sobre o mesmo pipeline supervisionado: CLI, API/front-end web e interface desktop. Nenhuma delas substitui revisão jurídica humana.

## Escolha de front-end

A interface web usa HTML, CSS e JavaScript puro em `web/`. Essa foi a opção escolhida porque:

- não exige Node.js, bundler ou build;
- facilita demonstração para recrutadores e avaliadores técnicos;
- reduz dependências e superfície de manutenção;
- é suficiente para upload de `.txt`, geração, download e histórico local.

Frameworks como React, Vue ou Next.js podem ser úteis no futuro se o painel crescer, mas seriam complexidade desnecessária nesta versão.

## Executar API local

```bash
uvicorn src.api:app --reload
```

Abra `http://127.0.0.1:8000`.

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Entrega o front-end local |
| `GET` | `/api/health` | Healthcheck simples |
| `POST` | `/api/setup` | Cria `output/` e `reports/` e valida recursos essenciais |
| `GET` | `/api/profiles` | Retorna `{items, default}` com perfis formais (label, descrição, exigências e flags) |
| `GET` | `/api/piece-types` | Lista tipos de peça agrupados conforme o prompt jurídico |
| `POST` | `/api/documents` | Gera `.docx`, valida e grava relatórios JSON/HTML |
| `POST` | `/api/documents/upload` | Extrai texto de `.txt`, `.md`, `.docx`, `.pdf` ou imagem e gera `.docx` |
| `GET` | `/api/documents/{filename}/download` | Baixa documento gerado |
| `GET` | `/api/reports` | Lista histórico local de relatórios e status |
| `GET` | `/api/reports/{filename}` | Abre relatório JSON ou HTML |

## Detecção automática de peça e perfil

`piece_type_id` e `profile_id` são opcionais em `/api/documents` e `/api/documents/upload`. Comportamento padrão:

- `piece_type_id` ausente, vazio ou `"auto"` → o sistema tenta inferir a peça a partir do texto, usando regras determinísticas em `src/piece_types.py::infer_piece_type_id`. Se nada for reconhecido, segue sem rótulo de peça.
- `profile_id` ausente, vazio ou `"auto"` → o sistema usa o perfil sugerido pela peça detectada. Sem peça reconhecida, cai em `judicial-inicial-jef` (PJE / Projudi).

A resposta inclui `piece_type_inferred: bool`, `profile_inferred: bool` e o objeto `profile { id, label, descricao }` para auditoria do que foi escolhido automaticamente.

## Exemplo de requisição

Sem informar nada (sistema detecta tudo):

```bash
curl -X POST http://127.0.0.1:8000/api/documents \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"PROCURAÇÃO AD JUDICIA...\\n\\nOutorgante fictício para teste.\"}"
```

Com peça e perfil explícitos:

```bash
curl -X POST http://127.0.0.1:8000/api/documents \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"[PREENCHER: texto fictício completo da peça]\",\"profile_id\":\"judicial-inicial-jef\",\"piece_type_id\":\"auxilio-incapacidade-temporaria\"}"
```

Upload de arquivo:

```bash
curl -X POST http://127.0.0.1:8000/api/documents/upload \
  -F "file=@peticao.docx"
```

Upload de múltiplos arquivos, incluindo imagem para OCR (com perfil explícito):

```bash
curl -X POST http://127.0.0.1:8000/api/documents/upload \
  -F "files=@relato.pdf" \
  -F "files=@print.png" \
  -F "profile_id=judicial-inicial-jef"
```

## Segurança operacional

- A API foi pensada para uso local.
- Não exponha em rede pública sem autenticação, TLS, logs controlados e política de retenção.
- Defina `API_TOKEN` no `.env` para exigir o cabeçalho `X-API-Token` nas rotas sensíveis.
- `output/`, `reports/`, inbox, outbox e status podem conter dados pessoais ou sensíveis.
- O fluxo web usa `no_outbox=True`, ou seja, gera e valida sem enfileirar envio automático.
- O payload textual da API tem limite de tamanho para reduzir risco de abuso local.
- Uploads são limitados a `.txt`, `.md`, `.docx`, `.pdf`, `.png`, `.jpg`, `.jpeg` e `.webp`.
- Imagens são usadas para OCR e não são anexadas ao `.docx` gerado.
- OCR de imagem exige Tesseract instalado no sistema operacional; sem isso, a API bloqueia com erro claro.

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

Use essa opção apenas em ambiente controlado.

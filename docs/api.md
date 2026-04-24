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
| `GET` | `/api/profiles` | Lista perfis formais disponíveis |
| `POST` | `/api/documents` | Gera `.docx`, valida e grava relatórios JSON/HTML |
| `GET` | `/api/documents/{filename}/download` | Baixa documento gerado |
| `GET` | `/api/reports` | Lista histórico local de relatórios e status |
| `GET` | `/api/reports/{filename}` | Abre relatório JSON ou HTML |

## Exemplo de requisição

```bash
curl -X POST http://127.0.0.1:8000/api/documents \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"[PREENCHER: texto fictício completo da peça]\",\"profile_id\":\"judicial-inicial-jef\"}"
```

## Segurança operacional

- A API foi pensada para uso local.
- Não exponha em rede pública sem autenticação, TLS, logs controlados e política de retenção.
- `output/`, `reports/`, inbox, outbox e status podem conter dados pessoais ou sensíveis.
- O fluxo web usa `no_outbox=True`, ou seja, gera e valida sem enfileirar envio automático.

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

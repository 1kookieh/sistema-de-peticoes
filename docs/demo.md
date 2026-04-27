# Demonstração segura

Este documento mostra como demonstrar o `sistema-de-peticoes` sem usar dados reais, documentos de clientes ou peças jurídicas sensíveis.

## Pré-requisitos

- Python 3.11+.
- Dependências instaladas com `pip install -r requirements-dev.txt`.
- Arquivo `.env` local configurado somente com valores fictícios.
- Entrada fictícia em `examples/inbox_valid.json`.
- Documento fictício de referência em `examples/generated-docx/peticao_exemplo.docx`.

## Fluxo recomendado por CLI

```powershell
python -m src --inbox .\examples\inbox_valid.json --profile judicial-inicial-jef --strict --no-outbox --report reports\conformidade_report.json
```

Para validar o documento gerado:

```powershell
python -m src.core.validation.docx output\arquivo.docx --profile judicial-inicial-jef
```

## Demonstração pela interface web

```powershell
uvicorn src.interfaces.api:app --host 127.0.0.1 --port 8000 --reload
```

Abra `http://127.0.0.1:8000`, cole o texto fictício de `examples/inbox_valid.json` ou carregue um arquivo fictício. O front-end mostra links para download do `.docx`, relatório JSON e relatório HTML local.

## Demonstração pela interface desktop

```powershell
python -m src.interfaces.desktop
```

Use apenas textos fictícios. A interface desktop gera o `.docx` em `output/` e relatórios em `reports/`, com o mesmo aviso de revisão humana obrigatória.

## O que demonstrar

- API somente em `/api/v1`.
- Leitura de uma inbox JSON local.
- Detecção automática de peça e perfil.
- Upload de texto, `.docx`, `.pdf` e imagem para OCR.
- Geração de `.docx`.
- Validação formal do documento gerado.
- Bloqueio de documentos com violações.
- Relatório JSON de conformidade formal.
- Relatório HTML local para revisão.
- Download pelo front-end local.
- Tema claro/escuro e service worker cacheando apenas assets estáticos.

## Cuidados

- Não use nomes reais, CPF, NIT, número de processo ou dados médicos.
- Não publique `output/`, `reports/`, `mcp_inbox.json`, `mcp_outbox.json` ou `mcp_status.json`.
- Não publique relatórios HTML gerados em `reports/`.
- Não apresente a saída como peça juridicamente pronta para protocolo.
- Sempre explique que o projeto exige revisão humana por advogado.

## Screenshot ou GIF

[PREENCHER: adicionar GIF ou screenshot usando apenas dados fictícios, sem informações pessoais ou sensíveis]

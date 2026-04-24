# Demonstração segura

Este documento mostra como demonstrar o `sistema-de-peticoes` sem usar dados reais, documentos de clientes ou peças jurídicas sensíveis.

## Pré-requisitos

- Python 3.11+.
- Dependências instaladas com `pip install -r requirements-dev.txt`.
- Arquivo `.env` local configurado.
- Entrada fictícia em `examples/inbox_valid.json`.
- Documento fictício de referência em `examples/generated-docx/peticao_exemplo.docx`.

## Fluxo recomendado

```powershell
$env:INBOX_MOCK_PATH = ".\examples\inbox_valid.json"
python -m src.main
```

Para gerar relatório sem escrever outbox:

```powershell
python -m src --inbox .\examples\inbox_valid.json --profile judicial-inicial-jef --strict --no-outbox --report reports\conformidade_report.json
```

Para validar o documento gerado:

```powershell
python -m src.validar_docx output\arquivo.docx --profile judicial-inicial-jef
```

## Demonstração pela interface web

```powershell
uvicorn src.api:app --reload
```

Abra `http://127.0.0.1:8000`, cole o texto fictício de `examples/inbox_valid.json` ou carregue um `.txt` fictício. O front-end mostra links para download do `.docx` e para o relatório HTML local.

## Demonstração pela interface desktop

```powershell
python -m src.desktop
```

Use apenas textos fictícios. A interface desktop gera o `.docx` em `output/` e relatórios em `reports/`, com o mesmo aviso de revisão humana obrigatória.

## O que demonstrar

- Leitura de uma inbox JSON local.
- Validação de contrato da entrada.
- Geração de `.docx`.
- Validação formal do documento gerado.
- Bloqueio de documentos com violações.
- Relatório JSON de conformidade formal.
- Relatório HTML local para revisão.
- Download pelo front-end local.
- Separação entre validação formal e revisão jurídica humana.

## Cuidados

- Não use nomes reais, CPF, NIT, número de processo ou dados médicos.
- Não publique `output/`, `reports/`, `mcp_inbox.json`, `mcp_outbox.json` ou `mcp_status.json`.
- Não publique relatórios HTML gerados em `reports/`.
- Não apresente a saída como peça juridicamente pronta para protocolo.
- Sempre explique que o projeto exige revisão humana por advogado.

## Screenshot ou GIF

[PREENCHER: adicionar GIF ou screenshot usando apenas dados fictícios, sem informações pessoais ou sensíveis]

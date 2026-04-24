# Demonstração segura

Este documento mostra como demonstrar o `sistema-de-peticoes` sem usar dados reais, documentos de clientes ou peças jurídicas sensíveis.

## Pré-requisitos

- Python 3.11+.
- Dependências instaladas com `pip install -r requirements-dev.txt`.
- Arquivo `.env` local configurado.
- Entrada fictícia em `teste_inbox.json`.

## Fluxo recomendado

```powershell
$env:INBOX_MOCK_PATH = ".\teste_inbox.json"
python -m src.main
```

Para gerar relatório sem escrever outbox:

```powershell
python -m src --inbox .\teste_inbox.json --profile judicial-inicial-jef --strict --no-outbox --report reports\conformidade_report.json
```

Para validar o documento gerado:

```powershell
python -m src.validar_docx output\arquivo.docx --profile judicial-inicial-jef
```

## O que demonstrar

- Leitura de uma inbox JSON local.
- Validação de contrato da entrada.
- Geração de `.docx`.
- Validação formal do documento gerado.
- Bloqueio de documentos com violações.
- Relatório JSON de conformidade formal.
- Separação entre validação formal e revisão jurídica humana.

## Cuidados

- Não use nomes reais, CPF, NIT, número de processo ou dados médicos.
- Não publique `output/`, `reports/`, `mcp_inbox.json`, `mcp_outbox.json` ou `mcp_status.json`.
- Não apresente a saída como peça juridicamente pronta para protocolo.
- Sempre explique que o projeto exige revisão humana por advogado.

## Screenshot ou GIF

[PREENCHER: adicionar GIF ou screenshot usando apenas dados fictícios, sem informações pessoais ou sensíveis]

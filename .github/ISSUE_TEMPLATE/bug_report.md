---
name: Relatar bug
about: Reporte um comportamento inesperado do pipeline
title: "[BUG] "
labels: bug
assignees: ''
---

## Descrição

Explique, em uma ou duas frases, o que está errado.

## Como reproduzir

1. Conteúdo do `mcp_inbox.json` (ou trecho relevante):
   ```json
   ...
   ```
2. Comando executado:
   ```bash
   ...
   ```
3. O que aconteceu:

## Comportamento esperado

O que deveria acontecer.

## Saída relevante

- Saída do `python -m src.main`:
  ```
  ...
  ```
- Saída do `python -m src.validar_docx <arquivo>`:
  ```
  ...
  ```
- Se possível, anexe o `.docx` gerado (ou um trecho dele).

## Ambiente

- SO: (Windows 11 / Ubuntu 22.04 / macOS 14 / ...)
- Versão do Python: `python --version`
- `python-docx`: `pip show python-docx | grep Version`

## Contexto adicional

Qualquer detalhe extra (logs, screenshots, hipóteses).

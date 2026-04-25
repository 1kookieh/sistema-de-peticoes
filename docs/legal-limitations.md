# Limitações jurídicas, LGPD e uso supervisionado

Este projeto automatiza preparação formal de documentos `.docx`, mas não substitui revisão jurídica humana.

## Limites do sistema

- Não decide mérito jurídico.
- Não confirma competência, rito, prazo, prescrição, decadência, tese aplicável ou jurisprudência atualizada.
- Não garante aceitação por tribunal, cartório, sistema de protocolo ou órgão administrativo.
- Não valida procuração, poderes nos autos, documentos médicos, cálculos, valor da causa ou autenticidade documental.
- Não deve ser usado para protocolo sem aprovação expressa de advogado responsável.
- **A detecção automática de tipo de peça é heurística**: serve para reduzir fricção operacional, não substitui escolha consciente do operador. O advogado responsável deve conferir se o perfil de validação aplicado é o adequado para a peça e o destino, especialmente quando o sistema cair no fallback `judicial-inicial-jef`.

## Revisão humana obrigatória

Antes de qualquer uso real, um advogado deve conferir:

- endereçamento, competência e classe processual;
- qualificação das partes;
- fatos, fundamentos, pedidos e valor da causa;
- assinatura, OAB, procuração e poderes;
- documentos anexos;
- regras locais do tribunal, rito ou sistema de protocolo;
- dados pessoais e dados sensíveis.

## Dados sensíveis

Considere sensíveis por padrão:

- `output/*.docx`;
- `reports/*.json`;
- `reports/*.html`;
- `mcp_inbox.json`;
- `mcp_outbox.json`;
- `mcp_status.json`;
- arquivos temporários e logs operacionais.

Esses arquivos não devem ser versionados, enviados para issues públicas ou compartilhados sem anonimização.

## Retenção e expurgo

Use retenção curta quando houver dados reais. A CLI oferece dry-run e expurgo explícito:

```bash
python -m src --cleanup-only
python -m src --cleanup-only --apply-retention
```

O operador continua responsável por backups, controle de acesso e política interna de armazenamento.
Quando a API for usada em rede interna, configure `API_TOKEN` e trate o token como segredo operacional.

## Demonstrações

Demonstrações devem usar apenas dados fictícios, como os arquivos em `examples/`.

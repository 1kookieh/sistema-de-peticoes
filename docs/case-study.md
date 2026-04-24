# Case study técnico

## Contexto

O `sistema-de-peticoes` nasceu como um pipeline local para reduzir retrabalho mecânico na preparação formal de documentos `.docx`, sem substituir a revisão jurídica humana.

O problema tratado não é decidir mérito jurídico. O foco é organizar um fluxo técnico previsível: receber texto, validar entrada, gerar documento, validar formatação e registrar status.

## Problema

Peças jurídicas podem conter lacunas, placeholders, dados fictícios, erros formais e informações sensíveis. Um pipeline automatizado precisa evitar duas falhas principais:

- gerar uma saída corrompida ou formalmente inválida;
- transmitir falsa sensação de que o documento está pronto para protocolo.

## Solução implementada

O projeto usa Python e `python-docx` para gerar `.docx`, com uma etapa de validação antes e depois da geração.

Fluxo:

```text
inbox JSON
  -> validação de contrato
  -> validação formal do texto
  -> geração do .docx
  -> validação formal do .docx
  -> outbox ou bloqueio
  -> status por item
  -> relatório opcional
```

## Decisões técnicas

- Separar formatador e validador para reduzir risco de o mesmo módulo gerar e aprovar o próprio erro.
- Usar filas JSON locais para manter integração simples e testável.
- Tratar `output/`, `reports/`, inbox, outbox e status como dados sensíveis.
- Usar perfis de validação para não assumir que existe um único padrão forense universal.
- Bloquear outbox quando houver violação formal relevante.

## O que o projeto demonstra

- Arquitetura de pipeline em Python.
- Manipulação de documentos `.docx`.
- Validação determinística.
- Separação de responsabilidades.
- Tratamento de dados sensíveis.
- Documentação técnica para usuários e avaliadores.
- Testes automatizados e golden file estrutural.

## Limitações assumidas

- O sistema não valida mérito jurídico.
- O sistema não substitui advogado.
- O padrão formal pode variar por tribunal, rito, classe processual e sistema de protocolo.
- O relatório JSON é evidência de validação formal, não garantia de aceitação.
- Demonstrações devem usar apenas dados fictícios.

## Próximas melhorias realistas

- Ampliar perfis por tribunal e tipo de peça.
- Melhorar mensagens de violação por seção ou parágrafo.
- Adicionar demonstração visual com dados fictícios.
- Criar exemplos adicionais de inbox inválida e documento bloqueado.

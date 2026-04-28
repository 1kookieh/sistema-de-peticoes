# Case Study Técnico

## Contexto

O `sistema-de-peticoes` nasceu para reduzir retrabalho mecânico na preparação formal de documentos jurídicos em `.docx`, mantendo revisão humana obrigatória.

O projeto não tenta decidir mérito jurídico. O foco é organizar um fluxo técnico previsível: receber dados, gerar ou formatar texto, validar, renderizar DOCX e registrar auditoria.

## Problema

Peças jurídicas podem conter:

- lacunas;
- placeholders;
- dados fictícios;
- erros formais;
- informações sensíveis;
- comentários internos indevidos.

Um pipeline automatizado precisa evitar duas falhas principais:

- gerar documento formalmente inválido;
- transmitir falsa sensação de que a peça está pronta para protocolo.

## Solução Implementada

O projeto usa Python, FastAPI, `python-docx` e uma camada opcional de LLM.

Fluxo resumido:

```text
entrada local
  -> extração de texto
  -> inferência de peça/perfil
  -> opcional: LLM estruturado
  -> validação textual
  -> geração DOCX
  -> validação estrutural
  -> relatório
```

## Decisões Técnicas

- Separar renderização e validação.
- Usar perfis formais por contexto.
- Manter API local e versionada.
- Isolar LLM em `src/infra/llm/`.
- Usar mock para testes sem envio externo.
- Manter prompts versionados.
- Não salvar prompt completo por padrão.
- Bloquear modo final quando houver marcadores internos ou dados críticos ausentes.

## O Que o Projeto Demonstra

- Arquitetura Python em camadas.
- API FastAPI.
- Front-end sem build.
- Manipulação de DOCX.
- Integração LLM testável.
- Validação determinística.
- Testes automatizados.
- Documentação de segurança e LGPD.

## Limitações Assumidas

- Não substitui advogado.
- Não valida mérito jurídico.
- Não pesquisa jurisprudência em tempo real.
- Não garante aceitação por tribunal ou órgão administrativo.
- Providers além de OpenAI ainda são roadmap.

## Evolução Natural

- Mais providers LLM.
- Mais validações jurídicas específicas.
- Preview visual do documento.
- Exportação PDF local opcional.
- Mascaramento configurável em relatórios.

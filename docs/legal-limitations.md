# Limitações Jurídicas, LGPD e Uso Supervisionado

O sistema automatiza etapas técnicas de geração, formatação e validação de documentos `.docx`. Ele não substitui advogado e não decide mérito jurídico.

## O Que o Sistema Faz

- Ajuda a estruturar e renderizar peças em DOCX.
- Aplica validações formais e textuais.
- Registra alertas em relatórios.
- Permite uso opcional de IA/LLM configurável.
- Mantém o fluxo padrão local, sem envio externo.

## O Que o Sistema Não Faz

- Não confirma competência, rito, prazo, prescrição ou decadência.
- Não garante tese jurídica correta.
- Não pesquisa jurisprudência em tempo real.
- Não valida autenticidade documental.
- Não garante aceitação por tribunal, cartório ou órgão administrativo.
- Não substitui revisão de advogado responsável.

## Revisão Humana Obrigatória

Antes de qualquer uso real, revise:

- endereçamento e competência;
- classe processual e rito;
- qualificação das partes;
- fatos, fundamentos e pedidos;
- DER, NB, CID, datas, valores e documentos;
- procuração, poderes e OAB;
- anexos;
- valor da causa;
- regras locais do sistema de protocolo.

## IA/LLM e Responsabilidade

Quando IA externa estiver ativada, dados do caso podem ser enviados ao provedor configurado.

Use IA apenas quando houver autorização e base adequada para tratamento dos dados.

O sistema exige resposta estruturada e aplica validações, mas a IA ainda pode:

- omitir informação importante;
- interpretar fatos de forma inadequada;
- sugerir fundamentos incompletos;
- gerar texto que exija correção humana.

## LGPD e Sigilo

Considere sensíveis:

- textos jurídicos;
- uploads;
- documentos gerados;
- relatórios;
- logs;
- chaves de API;
- dados pessoais ou de saúde.

Não compartilhe arquivos reais em issues públicas, prints, exemplos ou commits.

## Retenção

Arquivos de runtime ficam em `output/` e `reports/`.

Para limpar candidatos a expurgo:

```bash
python -m src --cleanup-only
```

Para aplicar retenção:

```bash
python -m src --cleanup-only --apply-retention
```

O operador continua responsável por backups, controle de acesso e política interna de armazenamento.

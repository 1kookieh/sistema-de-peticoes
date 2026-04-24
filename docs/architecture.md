# Arquitetura

Este documento aprofunda a visão técnica do `Sistema de Petições`. Para uma visão de alto nível e instruções de uso, consulte o [README](../README.md).

## Princípios

1. **Simplicidade antes de tudo.** Uma única dependência de runtime (`python-docx`). Nenhuma API paga.
2. **Pipeline determinístico.** A mesma entrada produz a mesma saída byte a byte (ignorando o timestamp no nome do arquivo).
3. **Validação independente da geração.** O validador relê o `.docx` do disco como um oráculo externo — se o formatador tiver um bug, o validador pega.
4. **Integração por contrato, não por código.** A comunicação com o mundo externo é feita por JSON em disco, não por chamadas a SDKs específicos.

## Componentes

### `config.py`
Loader minimalista de `.env` (sem `python-dotenv`). Expõe `EMAIL_ADVOGADO`, `GMAIL_LABEL_PROCESSADO`, `OUTPUT_DIR` e `PROMPTS_DIR`. Valores do ambiente sobrescrevem os do arquivo.

### `src/gmail_reader.py`
Lê `mcp_inbox.json` (ou `INBOX_MOCK_PATH` para testes) e devolve uma lista de `Email` (dataclass). Cada `Email` carrega `thread_id`, `message_id`, `remetente`, `assunto` e `peticao_texto` — o texto já redigido.

### `src/formatar_docx.py`
Transforma o texto plano em `.docx` aplicando:

| Item | Valor |
|---|---|
| Papel | A4 |
| Margens | 3 / 3 / 2 / 2 cm (sup / esq / inf / dir) |
| Fonte | Times New Roman 12, preto |
| Alinhamento | Justificado (corpo); centralizado (endereçamento, título, nome e OAB) |
| Espaçamento | 1,5 entre linhas; 0 pt antes/depois |
| Recuo 1ª linha | 2,5 cm nos parágrafos corridos |
| Após endereçamento | 7 linhas em branco obrigatórias |
| Negrito | Endereçamento, título, seções, marcadores `a) b) c)`, nome e OAB |

Heurísticas usadas para identificar blocos:
- **Endereçamento**: linhas iniciadas por `EXCELENTÍSSIMO`, `EXMO.`, etc.
- **Título da ação**: linha totalmente em caixa alta seguida de linha em branco.
- **Seções**: numeração romana + espaço + caixa alta (`I - DOS FATOS`).
- **Marcadores de pedidos/quesitos**: `a)`, `b)`, `1)`, etc.
- **Fechamento**: linhas finais contendo `OAB` são centralizadas sem recuo.

### `src/validar_docx.py`
Reabre o `.docx` e acumula uma lista de violações:
- Margens fora de 3/3/2/2 cm.
- Fonte diferente de Times New Roman 12 em qualquer run.
- Endereçamento ou título não centralizados.
- Ausência das 7 linhas em branco após o endereçamento.
- Ausência de linha contendo `OAB` no fechamento.
- Presença de linha de assinatura (ex.: sequências de `_______`).

O retorno é uma lista de strings descritivas; lista vazia = documento em conformidade.

### `src/gmail_sender.py`
Serializa a resposta (com o `.docx` em base64) em `mcp_outbox.json`. Um integrador externo consome essa fila para o envio.

### `src/main.py`
Costura tudo: itera sobre `buscar_emails_pendentes`, chama `renderizar`, depois `validar`, enfileira via `enfileirar_resposta` e emite um relatório final. Exit codes:

| Código | Significado |
|---|---|
| 0 | Tudo OK |
| 1 | Falha em um ou mais itens |
| 2 | `EMAIL_ADVOGADO` ausente |
| 3 | Gerado, mas com violações |

## Fluxo de dados

```
mcp_inbox.json  ──▶  gmail_reader.py  ──▶  Email
                                             │
                                             ▼
                                       formatar_docx.py  ──▶  output/*.docx
                                             │
                                             ▼
                                       validar_docx.py   ──▶  list[str]
                                             │
                                             ▼
                                       gmail_sender.py   ──▶  mcp_outbox.json
```

## Extensibilidade

- **Nova fonte de entrada**: basta gravar `mcp_inbox.json` a partir de qualquer origem (API, webhook, planilha).
- **Novo canal de saída**: leia `mcp_outbox.json` e dispare o envio pelo canal desejado.
- **Nova regra de formatação/validação**: edite `prompts/prompt_formatacao_word.md` (regra humana) e adicione a verificação em `validar_docx.py`.

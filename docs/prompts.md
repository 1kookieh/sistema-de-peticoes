# Prompts

Os prompts ficam em `prompts/` e fazem parte do contrato de geração AI-first e formatação DOCX.

## Arquivos

| Arquivo | Função |
|---|---|
| `prompts/prompt_peticao.md` | Define regras jurídicas, limites, tipos de peça e cautelas de geração |
| `prompts/prompt_formatacao_word.md` | Define padrão esperado para formatação Word/DOCX |

## Como São Usados

No fluxo de criação:

- o backend carrega os prompts versionados;
- o prompt jurídico e o prompt de formatação são combinados com os dados do caso;
- o provider LLM deve responder JSON estruturado;
- a resposta é validada antes da renderização;
- o DOCX é gerado a partir da estrutura validada.

O relatório registra hashes em `prompt_usage`; o prompt completo não é salvo por padrão.

## Como Editar

Ao alterar prompts:

1. Use apenas dados fictícios.
2. Não inclua nomes, CPF, RG, OAB, NB, DER ou documentos reais.
3. Evite instruções contraditórias.
4. Mantenha separação entre conteúdo jurídico, formatação DOCX e alertas de revisão.
5. Rode os testes.

```bash
python -m compileall config.py src tests
pytest -q
```

## Regras de Segurança

- Não peça para a IA inventar fatos.
- Não peça para criar documentos inexistentes.
- Não misture comentários internos com texto final da peça.
- Não salve prompt completo com dados do caso em relatórios.
- Marque dados ausentes em campos próprios da resposta estruturada.

## Como Conferir Uso Real

Relatórios JSON incluem:

- `prompt_usage`;
- nomes dos prompts;
- caminho dos prompts;
- SHA-256;
- metadados `llm`.

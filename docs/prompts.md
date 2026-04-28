# Prompts

Os prompts ficam em `prompts/` e são parte do contrato de geração e formatação.

## Arquivos

| Arquivo | Função |
|---|---|
| `prompts/prompt_peticao.md` | Define regras jurídicas, limites, tipos de peça e cautelas de geração |
| `prompts/prompt_formatacao_word.md` | Define padrão esperado para formatação Word/DOCX |

## Como São Usados

O pipeline sempre carrega os prompts e registra hashes em `prompt_usage`.

No modo sem IA:

- os prompts funcionam como contrato versionado;
- o texto informado pelo usuário é validado e renderizado localmente.

No modo com IA:

- os prompts são combinados com os dados do caso;
- o sistema exige resposta JSON estruturada;
- a resposta é validada antes do DOCX;
- o DOCX é renderizado a partir da estrutura validada.

## Como Editar

Ao alterar prompts:

1. Use apenas dados fictícios.
2. Não inclua nomes, CPF, RG, OAB, NB, DER ou documentos reais.
3. Evite instruções contraditórias.
4. Mantenha separação entre:
   - conteúdo jurídico;
   - formatação DOCX;
   - checklist ou alertas de revisão.
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
- Marque dados ausentes em campos próprios da resposta estruturada, não dentro do DOCX final.

## Como Conferir Uso Real

Relatórios JSON incluem:

- `prompt_usage`;
- nomes dos prompts;
- caminho dos prompts;
- SHA-256;
- metadados `llm` quando IA é usada.

Isso permite verificar se os prompts versionados participaram do fluxo.

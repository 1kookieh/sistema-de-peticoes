# Decisões técnicas

Registro leve de decisões (ADR light). Cada entrada descreve o contexto, a decisão e as consequências aceitas.

---

## 1. Usar `python-docx` em vez de templating (Jinja + Word)

**Contexto.** Precisamos aplicar negrito seletivo, recuos de primeira linha, alinhamentos mistos e margens exatas em centímetros — regras difíceis de expressar via substituição textual em template.

**Decisão.** Construir os `.docx` programaticamente com `python-docx`, manipulando parágrafos e runs.

**Consequências.**
- (+) Controle total sobre o OOXML gerado.
- (+) Fácil de testar — o "documento" é uma estrutura Python antes de virar arquivo.
- (−) Mais código de formatação que um template simples.

---

## 2. Filas JSON em disco (`mcp_inbox.json` / `mcp_outbox.json`)

**Contexto.** O pipeline precisa ser integrável com Gmail, APIs REST ou qualquer outra fonte, sem acoplar o código Python a um SDK específico.

**Decisão.** Entrada e saída são arquivos JSON em disco. Integradores externos populam a inbox e consomem a outbox.

**Consequências.**
- (+) Código principal fica testável offline e desacoplado do canal.
- (+) Fácil de inspecionar manualmente (`cat mcp_outbox.json`).
- (−) Não há throughput ou concorrência — mas isso não é requisito deste escopo.

---

## 3. Validador separado do formatador

**Contexto.** O formatador pode evoluir e introduzir bugs sutis (ex.: esquecer o recuo em um tipo de parágrafo novo).

**Decisão.** Um módulo separado (`validar_docx.py`) relê o `.docx` do disco e verifica as regras de forma independente.

**Consequências.**
- (+) Rede de segurança: bug no formatador é detectado em vez de propagado.
- (+) Permite loops de autocorreção e métricas de qualidade.
- (−) Duplicação parcial das regras (tanto o formatador quanto o validador conhecem "margens 3/3/2/2") — aceitamos em troca do desacoplamento.

---

## 4. Loader de `.env` caseiro, sem `python-dotenv`

**Contexto.** Queremos manter o requirements.txt mínimo.

**Decisão.** `config.py` parseia o `.env` com `str.partition("=")` — 10 linhas de código.

**Consequências.**
- (+) Uma única dependência de runtime (`python-docx`).
- (−) Não suporta expansão de variáveis ou quoting avançado — aceitável para este projeto.

---

## 5. Prompts em Markdown versionado

**Contexto.** As regras jurídicas e de formatação mudam — e quem altera nem sempre é desenvolvedor.

**Decisão.** Manter `prompts/prompt_peticao.md` e `prompts/prompt_formatacao_word.md` sob versionamento, editáveis sem tocar no código Python.

**Consequências.**
- (+) Mudança de regra = PR, com histórico e revisão.
- (+) Integradores que usem LLM podem consumir o mesmo arquivo.
- (−) Regras "executáveis" (validação) continuam em Python — o Markdown é a fonte de verdade humana.

---

## 6. Exit codes semânticos no `main.py`

**Contexto.** O pipeline pode rodar em CI/CD.

**Decisão.** `0` OK, `1` falha, `2` configuração ausente, `3` gerado com violações.

**Consequências.**
- (+) Scripts de automação podem tratar cada caso.
- (+) `3` permite publicar um artefato "quase pronto" para revisão humana.

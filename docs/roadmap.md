# Roadmap

Ideias priorizadas para a evolução do `Sistema de Petições`. A ordem reflete intenção, não compromisso de prazo.

## Curto prazo

- [ ] **Suíte de testes (`pytest`)**
  - Golden files de `.docx` para o formatador.
  - Testes de contrato para o validador (cada regra tem pelo menos um caso positivo e um negativo).
- [ ] **Lint/format automatizado** (`ruff` + `black`) no CI.
- [ ] **Mensagens de violação com contexto** — hoje dizem "margem esquerda incorreta"; queremos "margem esquerda 2,8 cm, esperado 3,0 cm no parágrafo 4".

## Médio prazo

- [ ] **Export em `.pdf`** diretamente do pipeline (via `docx2pdf` ou LibreOffice headless).
- [ ] **Anexos embarcados** — receber documentos do processo junto com o texto da peça e incorporá-los ao envio.
- [ ] **API REST** (FastAPI) — expor `/peticoes` aceitando o JSON do inbox e retornando o `.docx` gerado + relatório de validação.
- [ ] **Interface CLI enxuta** (`python -m src peticao ./entrada.txt --saida ./peticao.docx`).

## Longo prazo

- [ ] **Dashboard de qualidade** — histórico de quantas peças passam em todas as validações na primeira tentativa, violações mais comuns.
- [ ] **Biblioteca de templates** por tipo de ação (trabalhista, previdenciária, cível), carregáveis via flag.
- [ ] **Verificação ortográfica** opcional (LanguageTool local).
- [ ] **Internacionalização** do padrão de formatação para outros sistemas jurídicos (pt-PT, es).

## Ideias descartadas (e por quê)

- **Editor WYSIWYG próprio** — fora do escopo; o Word já cumpre esse papel.
- **Persistência em banco de dados** — as filas JSON atendem o volume previsto.

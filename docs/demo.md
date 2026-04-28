# Demonstração Segura

Use este guia para demonstrar o projeto sem expor dados reais.

## Pré-requisitos

- Python 3.11+.
- Dependências instaladas.
- `.env` local baseado em `.env.example`.
- Dados fictícios em `examples/`.

## API e Web

```bash
uvicorn src.interfaces.api:app --host 127.0.0.1 --port 8000 --reload
```

Abra:

```text
http://127.0.0.1:8000
```

Fluxo recomendado:

1. Use detecção automática de peça e perfil.
2. Cole texto fictício ou envie arquivo fictício.
3. Use `LLM_PROVIDER=none` para demo sem IA externa.
4. Use `LLM_PROVIDER=mock` para demonstrar o fluxo LLM sem enviar dados.
5. Clique em `Gerar DOCX`.
6. Abra relatório HTML/JSON.

## CLI

```bash
python -m src --inbox examples/inbox_valid.json --profile judicial-inicial-jef --strict --no-outbox --report reports/demo_report.json
```

Com IA mock:

```bash
python -m src --inbox examples/inbox_valid.json --no-outbox --llm --llm-provider mock --output-mode minuta
```

## Desktop

```bash
python -m src.interfaces.desktop
```

## O Que Demonstrar

- API em `/api/v1`.
- Interface web local.
- Upload de texto, DOCX, PDF e imagem.
- Detecção automática de peça/perfil.
- Geração de DOCX.
- Validação sem geração pelo botão `Validar texto`.
- Relatórios JSON/HTML.
- Histórico local.
- Tema claro/escuro.
- IA mock sem envio externo.

## Cuidados

- Não use nomes reais, CPF, NIT, número de processo, dados médicos ou documentos de clientes.
- Não publique `output/`, `reports/`, inbox, outbox ou status locais.
- Não apresente a saída como peça pronta para protocolo.
- Explique sempre que revisão humana por advogado é obrigatória.

## Screenshot ou GIF

Ainda pendente. Use apenas dados fictícios quando adicionar imagem ou GIF ao repositório.

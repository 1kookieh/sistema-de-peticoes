# Notas para Recrutadores e Tech Leads

Resumo rápido para avaliação técnica do projeto.

## O Que É

Sistema Python/FastAPI que gera e valida documentos jurídicos `.docx`, com interface web, CLI, arquitetura em camadas, integração opcional com IA/LLM e preocupação explícita com LGPD e revisão humana.

## Por Que É Interessante

- **Domínio específico:** não é um CRUD genérico; trabalha com documentos jurídicos, DOCX e validação formal.
- **Arquitetura em camadas:** separa domínio, infraestrutura, interfaces e orquestração.
- **LLM com fronteira clara:** providers ficam em `src/infra/llm/`, não dentro das rotas.
- **Validação dupla:** valida texto antes da geração e reabre o DOCX para validar estrutura.
- **Segurança prática:** evita versionar runtime, protege downloads contra path traversal e documenta riscos de IA externa.
- **Testes reais:** cobre API, pipeline, DOCX, modos de saída, inferência e LLM mock.

## Onde Olhar Primeiro

1. `src/orchestration/pipeline.py` — fluxo principal.
2. `src/infra/llm/` — integração LLM.
3. `src/infra/docx_render.py` — renderização DOCX.
4. `src/core/validation/` — regras de validação.
5. `src/interfaces/api.py` — contrato REST.
6. `tests/` — cobertura dos fluxos críticos.

## Como Rodar em 5 Minutos

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python -m src --setup
uvicorn src.interfaces.api:app --host 127.0.0.1 --port 8000 --reload
```

Abra `http://127.0.0.1:8000`.

## Stack

Python 3.11+, FastAPI, Pydantic Settings, python-docx, pytest, HTML/CSS/JavaScript ESM, Docker e GitHub Actions.

## Limitação Importante

O sistema é técnico e documental. Ele não substitui análise jurídica humana nem garante que uma peça esteja pronta para protocolo.

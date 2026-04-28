# Segurança

Este projeto processa textos e documentos jurídicos, que podem conter dados pessoais e dados sensíveis.

## Reportar Vulnerabilidades

Abra uma issue privada ou entre em contato diretamente com o mantenedor antes de divulgar publicamente uma vulnerabilidade.

Não inclua dados reais de clientes, documentos completos, chaves de API ou arquivos `.env` no relato.

## Dados Sensíveis

Considere sensíveis:

- `.env`;
- chaves de API;
- `output/*.docx`;
- `reports/*.json`;
- `reports/*.html`;
- inbox, outbox e status locais;
- uploads e textos jurídicos;
- prints da interface contendo dados reais.

## Variáveis de Ambiente

Use `.env.example` como referência e mantenha `.env` fora do Git.

Nunca versionar:

```text
OPENAI_API_KEY
ANTHROPIC_API_KEY
GEMINI_API_KEY
OPENROUTER_API_KEY
API_TOKEN
```

## IA Externa

Quando `LLM_PROVIDER=openai`, o texto informado pode ser enviado ao provedor configurado.

Antes de usar IA externa:

- confirme autorização para tratamento dos dados;
- remova ou anonimize dados sensíveis quando possível;
- revise termos internos de sigilo;
- confira a peça gerada manualmente.

## API Local

Recomendações:

- mantenha a API em `127.0.0.1` para uso local;
- configure `API_TOKEN` se for expor em rede interna;
- não exponha a API publicamente sem autenticação, TLS, logging controlado e política de retenção;
- revise `API_ALLOWED_ORIGINS`.

## Retenção

Use retenção curta quando houver dados reais:

```bash
python -m src --cleanup-only
python -m src --cleanup-only --apply-retention
```

## Limitação

O sistema reduz riscos técnicos e formais, mas não garante segurança absoluta nem substitui revisão jurídica, operacional e de privacidade.

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

Quando `LLM_PROVIDER=openai` ou `LLM_PROVIDER=anthropic`, o texto informado pode ser enviado ao provedor configurado. `LLM_PROVIDER=ollama` usa endpoint local (`OLLAMA_BASE_URL`) e nao exige chave externa, mas ainda deve ser usado somente com modelos e ambientes confiaveis.

Antes de usar IA externa:

- confirme autorização para tratamento dos dados;
- remova ou anonimize dados sensíveis quando possível;
- marque consentimento explícito no fluxo web/API/CLI antes de enviar dados a provider externo;
- revise termos internos de sigilo;
- confira a peça gerada manualmente.

O pipeline aplica mascaramento automático antes de chamar providers externos para padrões como CPF, CNPJ, NIT, NB, RG, CEP, telefone e e-mail. Essa proteção reduz exposição acidental, mas não garante anonimização completa: nomes próprios, fatos sensíveis e descrições do caso podem continuar no texto. Trate IA externa como compartilhamento de dados com terceiro.

## API Local

Recomendações:

- mantenha a API em `127.0.0.1` para uso local;
- configure `API_TOKEN` se for expor em rede interna;
- em Docker, o projeto usa `API_REQUIRE_TOKEN=1` por padrão; defina `API_TOKEN` e envie `X-API-Token` nas rotas sensíveis;
- não use `API_REQUIRE_TOKEN=false` quando a API estiver exposta fora do seu computador;
- não exponha a API publicamente sem autenticação, TLS, logging controlado e política de retenção;
- revise `API_ALLOWED_ORIGINS`.

Para testes e desenvolvimento sem envio externo, use `LLM_PROVIDER=mock` com dados fictícios. Para IA local sem chave externa, use `LLM_PROVIDER=ollama` com dados autorizados e revise o ambiente local antes de processar casos reais.

## Retenção

Use retenção curta quando houver dados reais:

```bash
python -m src --cleanup-only
python -m src --cleanup-only --apply-retention
```

## Limitação

O sistema reduz riscos técnicos e formais, mas não garante segurança absoluta nem substitui revisão jurídica, operacional e de privacidade.

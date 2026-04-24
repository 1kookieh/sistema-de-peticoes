# Decisões Técnicas

Registro leve de decisões do projeto.

## 1. Uso supervisionado, não automação jurídica plena

**Contexto.** O projeto lida com peças jurídicas, dados sensíveis e responsabilidade profissional.

**Decisão.** O sistema valida forma e contrato de entrada, mas não afirma conformidade jurídica de mérito. Toda saída exige revisão humana.

**Consequências.**
- Reduz falsa sensação de segurança.
- Mantém o core simples.
- Exige documentação clara para operadores jurídicos.

## 2. Bloquear outbox quando há violação

**Contexto.** A versão inicial enfileirava a resposta mesmo quando o validador apontava problemas.

**Decisão.** Qualquer violação formal bloqueia a outbox. O status do item é registrado em `mcp_status.json`.

**Consequências.**
- Evita envio acidental de documento formalmente inválido.
- Permite auditoria local do motivo do bloqueio.

## 3. Filas JSON locais

**Contexto.** O pipeline precisa continuar integrável com Gmail, MCP ou outras pontes externas sem acoplar SDKs no core.

**Decisão.** Manter `mcp_inbox.json` e `mcp_outbox.json`, agora com validação de contrato, limite de tamanho e escrita atômica da outbox.

**Consequências.**
- Integração segue simples.
- Os arquivos devem ser tratados como sensíveis.
- Concorrência pesada continua fora do escopo.

## 4. Validador separado do formatador

**Contexto.** O formatador pode introduzir bugs visuais sutis.

**Decisão.** O validador reabre o `.docx` e verifica página, margens, fontes, endereçamento, OAB, local/data, recuo e assinatura gráfica.

**Consequências.**
- Aumenta confiança formal.
- Ainda não substitui revisão visual nem jurídica.

## 5. `pytest` como dependência de desenvolvimento

**Contexto.** Smoke tests não bastam para um pipeline jurídico supervisionado.

**Decisão.** Adicionar `requirements-dev.txt` com `pytest` e rodar testes no CI.

**Consequências.**
- Instalação runtime continua mínima.
- Desenvolvimento passa a ter uma suíte objetiva de regressão.

## 6. Perfis de validação

**Contexto.** “Padrão forense brasileiro” não é universal; JEF, Justiça Estadual, INSS e tabelionatos têm expectativas diferentes.

**Decisão.** Criar perfis explícitos em `src/profiles.py`, selecionáveis por `VALIDATION_PROFILE` ou `--profile`.

**Consequências.**
- Regras por contexto ficam auditáveis.
- Novos tribunais ou ritos podem ser adicionados sem alterar o validador inteiro.
- Perfil não substitui regra local de cartório, tribunal ou sistema de protocolo.

## 7. Relatório JSON e golden estrutural

**Contexto.** Comparar `.docx` byte a byte é frágil; o que importa são propriedades formais.

**Decisão.** Extrair estrutura do documento para JSON e usar golden files estruturais em testes.

**Consequências.**
- Regressões de layout ficam mais visíveis.
- O relatório também serve como evidência de revisão formal.
- O relatório pode conter dados sensíveis e não deve ser versionado quando vier de casos reais.

## 8. Retenção desligada por padrão

**Contexto.** Expurgo automático pode apagar trabalho jurídico se mal configurado.

**Decisão.** A política existe, mas a CLI só apaga com `--apply-retention`; sem essa flag, lista candidatos.

**Consequências.**
- Operador mantém controle explícito sobre exclusão.
- O projeto ganha um caminho seguro para reduzir acúmulo de dados sensíveis.

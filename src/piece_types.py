"""Catálogo de tipos de peças alinhado ao prompt jurídico versionado."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PieceType:
    id: str
    nome: str
    grupo: str
    profile_id: str
    exige_revisao: str


PIECE_TYPES: tuple[PieceType, ...] = (
    PieceType("auxilio-incapacidade-temporaria", "Petição Inicial — Auxílio por Incapacidade Temporária", "Benefícios por incapacidade", "judicial-inicial-jef", "Base clínica, DII, profissão habitual e documentos médicos."),
    PieceType("aposentadoria-incapacidade-permanente", "Petição Inicial — Aposentadoria por Incapacidade Permanente", "Benefícios por incapacidade", "judicial-inicial-jef", "Base clínica, incapacidade total/permanente e condições pessoais."),
    PieceType("aposentadoria-invalidez-acidentaria", "Petição Inicial — Aposentadoria por Invalidez Acidentária (B-92)", "Benefícios por incapacidade", "judicial-inicial-estadual", "Nexo ocupacional, CAT e competência estadual."),
    PieceType("auxilio-acidente", "Petição Inicial — Auxílio-Acidente (B-36)", "Benefícios por incapacidade", "judicial-inicial-jef", "Consolidação das lesões e redução da capacidade laboral."),
    PieceType("restabelecimento-beneficio-incapacidade", "Petição Inicial — Restabelecimento de Benefício por Incapacidade Cessado", "Benefícios por incapacidade", "judicial-inicial-jef", "DCB, laudos contemporâneos e manutenção da incapacidade."),
    PieceType("aposentadoria-idade-urbana", "Petição Inicial — Aposentadoria por Idade Urbana", "Aposentadorias", "judicial-inicial-jef", "Carência, idade, CNIS e DER."),
    PieceType("aposentadoria-idade-rural", "Petição Inicial — Aposentadoria por Idade Rural", "Aposentadorias", "judicial-inicial-jef", "Prova rural, início de prova material e testemunhas."),
    PieceType("aposentadoria-hibrida", "Petição Inicial — Aposentadoria Híbrida", "Aposentadorias", "judicial-inicial-jef", "Períodos rurais/urbanos e cálculo de carência."),
    PieceType("aposentadoria-tempo-contribuicao", "Petição Inicial — Aposentadoria por Tempo de Contribuição", "Aposentadorias", "judicial-inicial-jef", "Direito adquirido ou regra de transição após EC 103/2019."),
    PieceType("aposentadoria-especial", "Petição Inicial — Aposentadoria Especial", "Aposentadorias", "judicial-inicial-jef", "PPP, LTCAT, agentes nocivos e conversão quando cabível."),
    PieceType("aposentadoria-pcd-tempo", "Petição Inicial — Aposentadoria por Tempo — Pessoa com Deficiência", "Aposentadorias", "judicial-inicial-jef", "Avaliação biopsicossocial e grau de deficiência."),
    PieceType("revisao-aposentadoria", "Petição Inicial — Revisão de Aposentadoria", "Aposentadorias", "judicial-inicial-jef", "RMI, DIB, CNIS, carta de concessão e tese revisional."),
    PieceType("pensao-por-morte", "Petição Inicial — Pensão por Morte", "Outros benefícios previdenciários", "judicial-inicial-jef", "Data do óbito, qualidade de segurado e dependência."),
    PieceType("salario-maternidade", "Petição Inicial — Salário-Maternidade", "Outros benefícios previdenciários", "judicial-inicial-jef", "Nascimento/adoção, qualidade de segurada e carência quando aplicável."),
    PieceType("reconhecimento-tempo-contribuicao", "Petição Inicial — Reconhecimento de Tempo de Contribuição", "Outros benefícios previdenciários", "judicial-inicial-jef", "Vínculos, CTPS, CNIS e provas complementares."),
    PieceType("bpc-deficiencia-judicial", "Petição Inicial — BPC/LOAS — Pessoa com Deficiência", "BPC/LOAS judicial", "judicial-inicial-jef", "Impedimento de longo prazo, CadÚnico e miserabilidade."),
    PieceType("bpc-idoso-judicial", "Petição Inicial — BPC/LOAS — Idoso", "BPC/LOAS judicial", "judicial-inicial-jef", "Idade mínima, composição familiar e renda."),
    PieceType("ms-bpc-mora", "Mandado de Segurança — BPC/LOAS por Mora Administrativa", "BPC/LOAS judicial", "judicial-inicial-jef", "Distinguir mora continuada de indeferimento expresso."),
    PieceType("requerimento-bpc-idoso", "Requerimento Administrativo — BPC/LOAS — Idoso", "BPC/LOAS administrativo", "administrativo-inss", "CadÚnico, composição familiar e renda."),
    PieceType("requerimento-bpc-deficiencia", "Requerimento Administrativo — BPC/LOAS — Pessoa com Deficiência", "BPC/LOAS administrativo", "administrativo-inss", "Base clínica e avaliação biopsicossocial."),
    PieceType("recurso-bpc", "Recurso Administrativo — BPC/LOAS", "BPC/LOAS administrativo", "administrativo-inss", "Decisão administrativa, fundamentos de impugnação e documentos."),
    PieceType("requerimento-inss-geral", "Requerimento Administrativo ao INSS — Geral", "Administrativo INSS", "administrativo-inss", "Pedido objetivo, documentos e identificação do requerente."),
    PieceType("recurso-crps", "Recurso Administrativo ao INSS / CRPS", "Administrativo INSS", "administrativo-inss", "Decisão, prazo, pontos impugnados e provas."),
    PieceType("cumprimento-exigencia", "Cumprimento de Exigência Administrativa", "Administrativo INSS", "administrativo-inss", "Texto integral da exigência e resposta item a item."),
    PieceType("pedido-prioridade", "Pedido de Prioridade de Tramitação", "Administrativo INSS", "administrativo-inss", "Idade, doença grave ou fundamento legal da prioridade."),
    PieceType("mandado-seguranca-previdenciario", "Mandado de Segurança Previdenciário", "Ações especiais", "judicial-inicial-jef", "Ato coator, autoridade, prazo decadencial e prova pré-constituída."),
    PieceType("tutela-antecedente", "Tutela Antecipada em Caráter Antecedente", "Ações especiais", "judicial-inicial-estadual", "Probabilidade do direito, perigo de dano e pedido final futuro."),
    PieceType("recurso-inominado", "Recurso Inominado (JEF)", "Recursos e impugnações", "forense-basico", "Sentença, prazo, fundamentos recursais e pedidos."),
    PieceType("apelacao-civel", "Apelação Cível", "Recursos e impugnações", "forense-basico", "Sentença, capítulos impugnados e preparo quando cabível."),
    PieceType("agravo-instrumento", "Agravo de Instrumento", "Recursos e impugnações", "forense-basico", "Decisão agravada, urgência e peças obrigatórias."),
    PieceType("embargos-declaracao", "Embargos de Declaração", "Recursos e impugnações", "forense-basico", "Omissão, contradição, obscuridade ou erro material."),
    PieceType("contrarrazoes", "Contrarrazões de Recurso", "Recursos e impugnações", "forense-basico", "Recurso adverso, preliminares e manutenção da decisão."),
    PieceType("cumprimento-sentenca-implantacao", "Cumprimento de Sentença — Implantação do Benefício", "Cumprimento de sentença", "forense-basico", "Título judicial, trânsito/fase e obrigação de fazer."),
    PieceType("cumprimento-sentenca-rpv", "Cumprimento de Sentença — Expedição de RPV", "Cumprimento de sentença", "forense-basico", "Cálculos, teto de RPV e dados bancários quando necessários."),
    PieceType("impugnacao-calculos", "Impugnação aos Cálculos", "Cumprimento de sentença", "forense-basico", "Memória de cálculo, divergência objetiva e documentos."),
    PieceType("juntada-documentos", "Petição de Juntada de Documentos", "Petições intermediárias", "forense-basico", "Processo, documentos e finalidade da juntada."),
    PieceType("replica-contestacao", "Réplica / Impugnação à Contestação", "Petições intermediárias", "forense-basico", "Contestação, preliminares e pontos controvertidos."),
    PieceType("manifestacao-documentos", "Manifestação sobre Documentos Novos", "Petições intermediárias", "forense-basico", "Documentos, pertinência e contraditório."),
    PieceType("peticao-simples", "Petição Simples / Outro", "Petições intermediárias", "forense-basico", "Finalidade objetiva e contexto processual."),
    PieceType("inventario-extrajudicial", "Inventário Extrajudicial", "Sucessório e extrajudicial", "extrajudicial-tabelionato", "Herdeiros, bens, ITCMD, testamento e incapazes."),
    PieceType("alvara-judicial", "Alvará Judicial", "Sucessório e extrajudicial", "judicial-inicial-estadual", "Cabimento, valores/bens e interessados."),
    PieceType("usucapiao", "Usucapião", "Cível e sucessório", "judicial-inicial-estadual", "Posse, tempo, imóvel, confrontantes e documentos."),
    PieceType("revisao-auxilio-incapacidade-temporaria", "Petição Inicial — Revisão de Auxílio por Incapacidade Temporária", "Benefícios por incapacidade", "judicial-inicial-jef", "DIB, RMI, período devido e base clínica da revisão."),
    PieceType("revisao-auxilio-acidente", "Petição Inicial — Revisão de Auxílio-Acidente", "Benefícios por incapacidade", "judicial-inicial-jef", "Critério de cálculo, sequelas e documentação médica."),
    PieceType("aposentadoria-pcd-idade", "Petição Inicial — Aposentadoria por Idade — Pessoa com Deficiência", "Aposentadorias", "judicial-inicial-jef", "Idade, deficiência, carência e avaliação biopsicossocial."),
    PieceType("reconhecimento-atividade-especial", "Petição Inicial — Reconhecimento de Atividade Especial", "Outros benefícios previdenciários", "judicial-inicial-jef", "PPP, LTCAT, agentes nocivos e enquadramento por período."),
    PieceType("auxilio-reclusao", "Petição Inicial — Auxílio-Reclusão", "Outros benefícios previdenciários", "judicial-inicial-jef", "Qualidade de segurado, baixa renda, dependência e certidão de reclusão."),
    PieceType("revisao-pensao-por-morte", "Petição Inicial — Revisão de Pensão por Morte", "Outros benefícios previdenciários", "judicial-inicial-jef", "Óbito, dependência, base de cálculo e tese revisional."),
    PieceType("bpc-revisao-restabelecimento", "Petição Inicial — Revisão / Restabelecimento de BPC/LOAS", "BPC/LOAS judicial", "judicial-inicial-jef", "Decisão de cessação/revisão, composição familiar e prova social atual."),
    PieceType("recurso-ordinario-crps", "Recurso Ordinário ao CRPS", "Administrativo INSS", "administrativo-inss", "Decisão administrativa, prazo recursal e fundamentos de reforma."),
    PieceType("recurso-especial-crps", "Recurso Especial ao CRPS", "Administrativo INSS", "administrativo-inss", "Divergência, admissibilidade e decisão recorrida."),
    PieceType("pedido-reconsideracao-administrativa", "Pedido de Reconsideração Administrativa", "Administrativo INSS", "administrativo-inss", "Decisão, fato novo ou erro administrativo objetivo."),
    PieceType("ctc", "Requerimento — Certidão de Tempo de Contribuição (CTC)", "Serviços administrativos INSS", "administrativo-inss", "Regime de destino, períodos e impedimentos de contagem recíproca."),
    PieceType("copia-processo-administrativo", "Requerimento — Cópia Integral do Processo Administrativo", "Serviços administrativos INSS", "administrativo-inss", "NB/protocolo, identificação do interessado e finalidade."),
    PieceType("retificacao-cnis", "Requerimento — Retificação / Atualização de CNIS", "Serviços administrativos INSS", "administrativo-inss", "Vínculos, remunerações, provas e período a corrigir."),
    PieceType("justificacao-administrativa", "Justificação Administrativa", "Serviços administrativos INSS", "administrativo-inss", "Fatos a provar, testemunhas e documentos mínimos."),
    PieceType("acerto-vinculos-remuneracoes", "Requerimento — Acerto de Vínculos e Remunerações no CNIS", "Serviços administrativos INSS", "administrativo-inss", "Vínculo, remuneração, competência e prova documental."),
    PieceType("regularizacao-representante", "Requerimento — Regularização de Representante / Procurador", "Serviços administrativos INSS", "administrativo-inss", "Documento de representação, poderes e dados do procurador."),
    PieceType("agravo-interno", "Agravo Interno", "Recursos e impugnações", "forense-basico", "Decisão monocrática, prazo e fundamentos de reforma."),
    PieceType("pedilef-tnu", "Pedido de Uniformização de Interpretação de Lei (PEDILEF/TNU)", "Recursos e impugnações", "forense-basico", "Divergência entre turmas, questão de direito material e admissibilidade."),
    PieceType("recurso-especial-stj", "Recurso Especial (STJ)", "Recursos e impugnações", "forense-basico", "Violação de lei federal, divergência e juízo de admissibilidade."),
    PieceType("recurso-extraordinario-stf", "Recurso Extraordinário (STF)", "Recursos e impugnações", "forense-basico", "Questão constitucional, repercussão geral e admissibilidade."),
    PieceType("juizo-retratacao", "Juízo de Retratação", "Recursos e impugnações", "forense-basico", "Tese vinculante, recurso repetitivo ou precedente aplicável."),
    PieceType("cumprimento-sentenca-precatorio", "Cumprimento de Sentença — Expedição de Precatório", "Cumprimento de sentença", "forense-basico", "Valor acima do teto de RPV, cálculos e dados necessários."),
    PieceType("cumprimento-sentenca-astreintes", "Cumprimento de Sentença — Astreintes por Descumprimento", "Cumprimento de sentença", "forense-basico", "Ordem judicial, prazo, descumprimento e cálculo da multa."),
    PieceType("impugnacao-cumprimento-sentenca", "Impugnação ao Cumprimento de Sentença", "Cumprimento de sentença", "forense-basico", "Excesso, inexigibilidade, nulidade ou tese defensiva cabível."),
    PieceType("habilitacao-sucessoria-processo", "Habilitação Sucessória no Curso do Processo", "Cumprimento de sentença", "forense-basico", "Óbito, sucessores, documentos e regularização processual."),
    PieceType("tutela-urgencia-incidental", "Petição de Tutela de Urgência / Antecipada", "Petições intermediárias", "forense-basico", "Probabilidade, perigo de dano e fase processual."),
    PieceType("impugnacao-laudo-pericial", "Impugnação ao Laudo Pericial", "Petições intermediárias", "forense-basico", "Laudo, contradições, quesitos e pedido de esclarecimentos."),
    PieceType("quesitos-periciais", "Apresentação de Quesitos Periciais", "Petições intermediárias", "forense-basico", "Objeto da perícia, quesitos técnicos e documentos de apoio."),
    PieceType("especificacao-provas", "Especificação de Provas", "Petições intermediárias", "forense-basico", "Fatos controvertidos, provas pretendidas e pertinência."),
    PieceType("sobrepartilha-extrajudicial", "Sobrepartilha Extrajudicial", "Sucessório e extrajudicial", "extrajudicial-tabelionato", "Bens sobrevindos, consenso e requisitos notariais."),
    PieceType("cessao-direitos-hereditarios", "Cessão de Direitos Hereditários", "Sucessório e extrajudicial", "extrajudicial-tabelionato", "Forma pública, cedente, cessionário, objeto e anuências."),
    PieceType("renuncia-heranca", "Renúncia à Herança / Repúdio", "Sucessório e extrajudicial", "extrajudicial-tabelionato", "Forma pública ou termo judicial e análise de credores."),
    PieceType("inventario-judicial", "Inventário Judicial — Petição Inicial", "Cível e sucessório", "judicial-inicial-estadual", "Óbito, bens, herdeiros, ITCMD, testamento e incapazes."),
    PieceType("arrolamento-simples", "Arrolamento Simples — Petição Inicial", "Cível e sucessório", "judicial-inicial-estadual", "Óbito, bens, herdeiros e adequação do rito."),
    PieceType("arrolamento-sumario", "Arrolamento Sumário — Petição Inicial", "Cível e sucessório", "judicial-inicial-estadual", "Consenso, herdeiros capazes, partilha e adequação do rito."),
    PieceType("sobrepartilha-judicial", "Sobrepartilha — Petição Inicial", "Cível e sucessório", "judicial-inicial-estadual", "Bens descobertos após partilha e legitimidade."),
    PieceType("formal-partilha", "Formal de Partilha / Carta de Adjudicação", "Cível e sucessório", "forense-basico", "Decisão homologatória, trânsito e dados dos bens/herdeiros."),
    PieceType("habilitacao-herdeiros", "Habilitação de Herdeiros", "Cível e sucessório", "forense-basico", "Óbito, sucessores e prova documental."),
    PieceType("primeiras-declaracoes", "Primeiras Declarações do Inventariante", "Cível e sucessório", "forense-basico", "Inventariante, herdeiros, bens, dívidas e plano inicial."),
    PieceType("ultimas-declaracoes", "Últimas Declarações do Inventariante", "Cível e sucessório", "forense-basico", "Atualização de bens, dívidas, partilha e concordâncias."),
    PieceType("nomeacao-inventariante", "Nomeação / Substituição / Remoção de Inventariante", "Cível e sucessório", "forense-basico", "Legitimidade, motivo e documentos do inventário."),
    PieceType("procuracao-ad-judicia", "Procuração Ad Judicia", "Instrumentos de mandato", "instrumento-mandato", "Outorgante, outorgado, poderes, foro, data e assinatura."),
    PieceType("procuracao-administrativa-inss", "Procuração Administrativa Previdenciária / INSS", "Instrumentos de mandato", "instrumento-mandato", "Outorgante, procurador, poderes administrativos e validade."),
    PieceType("procuracao-ad-judicia-et-extra", "Procuração Ad Judicia et Extra", "Instrumentos de mandato", "instrumento-mandato", "Poderes judiciais e extrajudiciais devem ser expressos e revisados."),
    PieceType("substabelecimento-com-reserva", "Substabelecimento com Reserva de Poderes", "Instrumentos de mandato", "instrumento-mandato", "Procuração originária, substabelecente, substabelecido e reserva expressa."),
    PieceType("substabelecimento-sem-reserva", "Substabelecimento sem Reserva de Poderes", "Instrumentos de mandato", "instrumento-mandato", "Procuração originária, ciência do cliente e transferência integral de poderes."),
    PieceType("declaracao-hipossuficiencia", "Declaração de Hipossuficiência", "Instrumentos e declarações", "instrumento-mandato", "Declarante, situação econômica, data e assinatura."),
    PieceType("declaracao-residencia", "Declaração de Residência", "Instrumentos e declarações", "instrumento-mandato", "Declarante, endereço, finalidade e assinatura."),
    PieceType("declaracao-atividade-rural", "Declaração de Atividade Rural", "Instrumentos e declarações", "instrumento-mandato", "Período, atividade, local, testemunhas e documentos."),
)


def list_piece_types() -> list[PieceType]:
    return sorted(PIECE_TYPES, key=lambda item: (item.grupo, item.nome))


def get_piece_type(piece_type_id: str | None) -> PieceType | None:
    if not piece_type_id:
        return None
    for piece_type in PIECE_TYPES:
        if piece_type.id == piece_type_id:
            return piece_type
    raise ValueError(f"tipo de peça desconhecido: {piece_type_id}")


def infer_piece_type_id(texto: str) -> str | None:
    """Tenta identificar a peça a partir do texto.

    Heurística determinística baseada em (1) primeira linha (cabeçalho) e
    (2) palavras-chave do corpo. Retorna o `id` da peça mais provável ou
    ``None`` quando o texto não traz sinais suficientes — nesse caso o
    caller deve cair em um perfil padrão e seguir sem `piece_type`.

    Heurística manual em vez de NLP por dois motivos:

    - Não introduz dependência externa nem peso de modelo.
    - Mantém comportamento auditável — cada decisão é uma regra explícita
      revisável por quem opera o sistema.
    """
    if not texto or not texto.strip():
        return None

    t = texto.lower()
    primeira = next(
        (linha.strip() for linha in texto.splitlines() if linha.strip()),
        "",
    ).upper()

    # --- Instrumentos de mandato e declarações (prioridade alta: cabeçalho) ---
    if primeira.startswith(("PROCURAÇÃO", "PROCURACAO", "INSTRUMENTO PARTICULAR DE PROCURAÇÃO")):
        if "ad judicia et extra" in t or "judicia et extra" in t:
            return "procuracao-ad-judicia-et-extra"
        if any(k in t for k in ("inss", "previdenciári", "administrativ")):
            return "procuracao-administrativa-inss"
        return "procuracao-ad-judicia"

    if primeira.startswith(("SUBSTABELECIMENTO", "SUBSTABELECEMENTO")):
        if "sem reserva" in t:
            return "substabelecimento-sem-reserva"
        return "substabelecimento-com-reserva"

    if primeira.startswith(("DECLARAÇÃO", "DECLARACAO")):
        if "hipossufic" in t:
            return "declaracao-hipossuficiencia"
        if "atividade rural" in t or "rurícola" in t or "ruricola" in t:
            return "declaracao-atividade-rural"
        if "residênci" in t or "residenci" in t or "resido" in t:
            return "declaracao-residencia"

    # --- Recursos (palavras-chave fortes) ---
    if "recurso inominado" in t:
        return "recurso-inominado"
    if "agravo de instrumento" in t:
        return "agravo-instrumento"
    if "agravo interno" in t:
        return "agravo-interno"
    if "embargos de declaração" in t or "embargos de declaracao" in t:
        return "embargos-declaracao"
    if "contrarrazões" in t or "contrarrazoes" in t:
        return "contrarrazoes"
    if "apelação" in t and ("cível" in t or "civel" in t):
        return "apelacao-civel"
    if "pedilef" in t or ("uniformização" in t and "tnu" in t):
        return "pedilef-tnu"
    if "recurso especial" in t and ("stj" in t or "tribunal superior" in t):
        return "recurso-especial-stj"
    if "recurso extraordinário" in t or "recurso extraordinario" in t:
        return "recurso-extraordinario-stf"
    if "juízo de retratação" in t or "juizo de retratacao" in t:
        return "juizo-retratacao"
    if "recurso ordinário" in t and "crps" in t:
        return "recurso-ordinario-crps"
    if "recurso especial" in t and "crps" in t:
        return "recurso-especial-crps"
    if "reconsideração" in t or "reconsideracao" in t:
        return "pedido-reconsideracao-administrativa"

    # --- Cumprimento de sentença ---
    if "cumprimento de sentença" in t or "cumprimento da sentença" in t or "cumprimento de sentenca" in t:
        if "rpv" in t or "requisição de pequeno valor" in t:
            return "cumprimento-sentenca-rpv"
        if "precatório" in t or "precatorio" in t:
            return "cumprimento-sentenca-precatorio"
        if "astreintes" in t or "multa diária" in t or "multa diaria" in t:
            return "cumprimento-sentenca-astreintes"
        return "cumprimento-sentenca-implantacao"
    if "impugnação ao cumprimento" in t or "impugnacao ao cumprimento" in t:
        return "impugnacao-cumprimento-sentenca"
    if "impugnação aos cálculos" in t or "impugnacao aos calculos" in t or "impugnação dos cálculos" in t:
        return "impugnacao-calculos"

    # --- Mandado de segurança ---
    if "mandado de segurança" in t or "mandado de seguranca" in t:
        if "bpc" in t or "loas" in t:
            return "ms-bpc-mora"
        return "mandado-seguranca-previdenciario"

    # --- Sucessório / extrajudicial ---
    if "inventário extrajudicial" in t or "inventario extrajudicial" in t:
        return "inventario-extrajudicial"
    if "arrolamento sumário" in t or "arrolamento sumario" in t:
        return "arrolamento-sumario"
    if "arrolamento" in t and "simples" in t:
        return "arrolamento-simples"
    if "sobrepartilha" in t and "extrajudicial" in t:
        return "sobrepartilha-extrajudicial"
    if "sobrepartilha" in t:
        return "sobrepartilha-judicial"
    if "usucapião" in t or "usucapiao" in t:
        return "usucapiao"
    if "alvará" in t and ("judicial" in t or "juízo" in t):
        return "alvara-judicial"
    if "cessão de direitos hereditários" in t or "cessao de direitos hereditarios" in t:
        return "cessao-direitos-hereditarios"
    if "renúncia à herança" in t or "renuncia a heranca" in t or "repúdio à herança" in t:
        return "renuncia-heranca"
    if "habilitação sucessória" in t or "habilitacao sucessoria" in t:
        return "habilitacao-sucessoria-processo"
    if "habilitação" in t and "herdeiros" in t:
        return "habilitacao-herdeiros"
    if "primeiras declarações" in t or "primeiras declaracoes" in t:
        return "primeiras-declaracoes"
    if "últimas declarações" in t or "ultimas declaracoes" in t:
        return "ultimas-declaracoes"
    if "inventariante" in t and any(k in t for k in ("nomeação", "nomeacao", "remoção", "remocao", "substituição", "substituicao")):
        return "nomeacao-inventariante"
    if "formal de partilha" in t or "carta de adjudicação" in t:
        return "formal-partilha"
    if "inventário" in t or "inventario" in t:
        return "inventario-judicial"

    # --- Petições intermediárias ---
    if "impugnação ao laudo" in t or "impugnacao ao laudo" in t:
        return "impugnacao-laudo-pericial"
    if "quesitos periciais" in t or "apresentação de quesitos" in t:
        return "quesitos-periciais"
    if "especificação de provas" in t or "especificacao de provas" in t:
        return "especificacao-provas"
    if "tutela de urgência" in t or "tutela antecipada" in t or "tutela de urgencia" in t:
        if primeira.startswith(("EXCELENT", "AO JUÍZO", "AO JUIZO")):
            # Inicial pode ter pedido de tutela; só classifica como incidental
            # se claramente for petição intermediária (sem início do tipo "Excelentíssimo... [x] vem propor a presente ação")
            if "vem propor" not in t and "vem ajuizar" not in t and "petição inicial" not in t:
                return "tutela-urgencia-incidental"
    if "réplica" in t or "replica" in t or "impugnação à contestação" in t:
        return "replica-contestacao"
    if "manifestação sobre documentos" in t or "manifestacao sobre documentos" in t:
        return "manifestacao-documentos"
    if "juntada de documentos" in t or "juntada documental" in t:
        return "juntada-documentos"

    # --- Administrativo INSS / CRPS ---
    is_admin = primeira.startswith((
        "AO INSTITUTO",
        "AO INSS",
        "AO CRPS",
        "À AGÊNCIA",
        "AGÊNCIA",
        "À GERÊNCIA",
        "AO PRESIDENTE DO INSS",
    ))
    if is_admin:
        if "bpc" in t or "loas" in t:
            if "recurso" in t:
                return "recurso-bpc"
            if "deficiência" in t or "deficiencia" in t:
                return "requerimento-bpc-deficiencia"
            return "requerimento-bpc-idoso"
        if "ctc" in t or "certidão de tempo" in t or "certidao de tempo" in t:
            return "ctc"
        if "cópia integral" in t or "copia integral" in t or "cópia do processo" in t:
            return "copia-processo-administrativo"
        if "retificação" in t and "cnis" in t:
            return "retificacao-cnis"
        if "acerto" in t and "cnis" in t:
            return "acerto-vinculos-remuneracoes"
        if "justificação administrativa" in t or "justificacao administrativa" in t:
            return "justificacao-administrativa"
        if "regularização" in t and ("representante" in t or "procurador" in t):
            return "regularizacao-representante"
        if "prioridade" in t and ("tramitação" in t or "tramitacao" in t):
            return "pedido-prioridade"
        if "cumprimento de exigência" in t or "cumprimento de exigencia" in t:
            return "cumprimento-exigencia"
        if "recurso" in t and "crps" in t:
            return "recurso-crps"
        return "requerimento-inss-geral"

    # --- BPC/LOAS judicial ---
    if "bpc" in t or "loas" in t:
        if "revisão" in t or "revisao" in t or "restabelec" in t:
            return "bpc-revisao-restabelecimento"
        if "deficiência" in t or "deficiencia" in t:
            return "bpc-deficiencia-judicial"
        if "idoso" in t or "65 anos" in t:
            return "bpc-idoso-judicial"

    # --- Aposentadorias ---
    if "aposentadoria especial" in t or ("aposentadoria" in t and any(k in t for k in ("ppp", "ltcat", "agentes nocivos"))):
        return "aposentadoria-especial"
    if "aposentadoria" in t:
        if "rural" in t or "rurícola" in t or "ruricola" in t or "trabalhador rural" in t:
            return "aposentadoria-idade-rural"
        if "híbrida" in t or "hibrida" in t:
            return "aposentadoria-hibrida"
        if ("tempo de contribuição" in t or "tempo de contribuicao" in t) and ("deficiência" in t or "deficiencia" in t):
            return "aposentadoria-pcd-tempo"
        if "tempo de contribuição" in t or "tempo de contribuicao" in t:
            return "aposentadoria-tempo-contribuicao"
        if "idade" in t and ("deficiência" in t or "deficiencia" in t):
            return "aposentadoria-pcd-idade"
        if "idade" in t:
            return "aposentadoria-idade-urbana"
        if "invalidez" in t and ("acidentária" in t or "acidentaria" in t or "b-92" in t or "b92" in t):
            return "aposentadoria-invalidez-acidentaria"
        if "incapacidade permanente" in t or "invalidez" in t:
            return "aposentadoria-incapacidade-permanente"
        if "revisão" in t or "revisao" in t:
            return "revisao-aposentadoria"

    # --- Auxílios e demais benefícios ---
    if "auxílio-acidente" in t or "auxílio acidente" in t or "auxilio-acidente" in t or "b-36" in t or "b36" in t:
        if "revisão" in t or "revisao" in t:
            return "revisao-auxilio-acidente"
        return "auxilio-acidente"
    if any(k in t for k in (
        "auxílio-doença",
        "auxilio-doenca",
        "auxílio por incapacidade temporária",
        "auxilio por incapacidade temporaria",
        "incapacidade temporária",
        "incapacidade temporaria",
    )):
        if "revisão" in t or "revisao" in t:
            return "revisao-auxilio-incapacidade-temporaria"
        if "restabelec" in t:
            return "restabelecimento-beneficio-incapacidade"
        return "auxilio-incapacidade-temporaria"
    if "auxílio-reclusão" in t or "auxilio-reclusao" in t or "auxílio reclusão" in t:
        return "auxilio-reclusao"
    if "pensão por morte" in t or "pensao por morte" in t:
        if "revisão" in t or "revisao" in t:
            return "revisao-pensao-por-morte"
        return "pensao-por-morte"
    if "salário-maternidade" in t or "salario-maternidade" in t or "salário maternidade" in t:
        return "salario-maternidade"
    if ("tempo de contribuição" in t or "tempo de contribuicao" in t) and "reconhecimento" in t:
        return "reconhecimento-tempo-contribuicao"
    if "atividade especial" in t and "reconhecimento" in t:
        return "reconhecimento-atividade-especial"

    # --- Cabeçalho judicial genérico → petição simples ---
    if primeira.startswith(("EXCELENT", "AO JUÍZO", "AO JUIZO", "MERITÍSSIMO", "MERITISSIMO")):
        return "peticao-simples"

    return None

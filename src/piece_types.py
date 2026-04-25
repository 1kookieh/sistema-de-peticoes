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


# Linhas iniciais consideradas "cabeçalho/título" para a inferência.
_HEAD_LINES_FOR_TITLE = 30
_MAX_TITLE_LINE_CHARS = 140
_MIN_UPPER_RATIO_FOR_TITLE = 0.7


def _title_candidates(linhas: list[str]) -> list[str]:
    """Filtra linhas que parecem **títulos de ação**.

    Critérios cumulativos para considerar uma linha um título:

    - vem entre as primeiras ``_HEAD_LINES_FOR_TITLE`` não vazias;
    - tem no máximo ``_MAX_TITLE_LINE_CHARS`` caracteres;
    - pelo menos ``_MIN_UPPER_RATIO_FOR_TITLE`` das letras estão em caixa
      alta (o nome da ação no padrão forense brasileiro vem em CAIXA ALTA).

    Esse filtro elimina o ruído mais comum do detector anterior: linhas do
    corpo que citam jurisprudência ("...em agravo de instrumento (TRF-1...)")
    deixavam a inferência confusa porque a busca varria todo o cabeçalho.
    """
    candidates: list[str] = []
    for linha in linhas[:_HEAD_LINES_FOR_TITLE]:
        s = linha.strip()
        if not s or len(s) > _MAX_TITLE_LINE_CHARS:
            continue
        letras = [c for c in s if c.isalpha()]
        if not letras:
            # mantém linhas só com números/pontuação para não perder marcadores
            candidates.append(s)
            continue
        upper_ratio = sum(1 for c in letras if c.isupper()) / len(letras)
        if upper_ratio >= _MIN_UPPER_RATIO_FOR_TITLE:
            candidates.append(s)
    return candidates


def _normalize_for_match(value: str) -> str:
    """Remove acentos e dobra para maiúsculas, simplificando comparações.

    A normalização é feita só na detecção; o texto original do usuário
    permanece intacto para a geração do .docx.
    """
    import unicodedata

    nfkd = unicodedata.normalize("NFD", value)
    sem_acentos = "".join(c for c in nfkd if not unicodedata.combining(c))
    return sem_acentos.upper()


def _detect_from_title(head_norm: str) -> str | None:
    """Detector que olha apenas o cabeçalho/título nas primeiras linhas.

    Aqui ficam as regras com **alta especificidade**: só dispara quando o
    rótulo da ação está claramente no topo do documento. Isso evita falsos
    positivos quando palavras-chave aparecem no corpo, em jurisprudência
    citada ou em fundamentação.
    """
    H = head_norm  # alias curto para legibilidade

    # --- Recursos (título no topo) ---
    if "RECURSO INOMINADO" in H:
        return "recurso-inominado"
    if "AGRAVO DE INSTRUMENTO" in H:
        return "agravo-instrumento"
    if "AGRAVO INTERNO" in H:
        return "agravo-interno"
    if "EMBARGOS DE DECLARACAO" in H:
        return "embargos-declaracao"
    if "CONTRARRAZOES" in H:
        return "contrarrazoes"
    if "APELACAO" in H and ("CIVEL" in H or "RECURSO DE APELACAO" in H):
        return "apelacao-civel"
    if "PEDILEF" in H or ("UNIFORMIZACAO" in H and "TNU" in H):
        return "pedilef-tnu"
    if "RECURSO ESPECIAL" in H and ("STJ" in H or "TRIBUNAL SUPERIOR" in H):
        return "recurso-especial-stj"
    if "RECURSO EXTRAORDINARIO" in H:
        return "recurso-extraordinario-stf"
    if "JUIZO DE RETRATACAO" in H:
        return "juizo-retratacao"
    if "RECURSO ORDINARIO" in H and "CRPS" in H:
        return "recurso-ordinario-crps"
    if "RECURSO ESPECIAL" in H and "CRPS" in H:
        return "recurso-especial-crps"
    if "PEDIDO DE RECONSIDERACAO" in H:
        return "pedido-reconsideracao-administrativa"

    # --- Cumprimento de sentença ---
    if "CUMPRIMENTO DE SENTENCA" in H or "CUMPRIMENTO DA SENTENCA" in H:
        if "RPV" in H or "REQUISICAO DE PEQUENO VALOR" in H:
            return "cumprimento-sentenca-rpv"
        if "PRECATORIO" in H:
            return "cumprimento-sentenca-precatorio"
        if "ASTREINTES" in H or "MULTA DIARIA" in H:
            return "cumprimento-sentenca-astreintes"
        return "cumprimento-sentenca-implantacao"
    if "IMPUGNACAO AO CUMPRIMENTO" in H:
        return "impugnacao-cumprimento-sentenca"
    if "IMPUGNACAO AOS CALCULOS" in H or "IMPUGNACAO DOS CALCULOS" in H:
        return "impugnacao-calculos"

    # --- Mandado de segurança ---
    if "MANDADO DE SEGURANCA" in H:
        if "BPC" in H or "LOAS" in H:
            return "ms-bpc-mora"
        return "mandado-seguranca-previdenciario"

    # --- Sucessório / extrajudicial ---
    if "INVENTARIO EXTRAJUDICIAL" in H:
        return "inventario-extrajudicial"
    if "ARROLAMENTO SUMARIO" in H:
        return "arrolamento-sumario"
    if "ARROLAMENTO" in H and "SIMPLES" in H:
        return "arrolamento-simples"
    if "SOBREPARTILHA" in H and "EXTRAJUDICIAL" in H:
        return "sobrepartilha-extrajudicial"
    if "SOBREPARTILHA" in H:
        return "sobrepartilha-judicial"
    if "USUCAPIAO" in H:
        return "usucapiao"
    if "ALVARA" in H and ("JUDICIAL" in H or "JUIZO" in H):
        return "alvara-judicial"
    if "CESSAO DE DIREITOS HEREDITARIOS" in H:
        return "cessao-direitos-hereditarios"
    if "RENUNCIA A HERANCA" in H or "REPUDIO A HERANCA" in H:
        return "renuncia-heranca"
    if "HABILITACAO SUCESSORIA" in H:
        return "habilitacao-sucessoria-processo"
    if "HABILITACAO" in H and "HERDEIROS" in H:
        return "habilitacao-herdeiros"
    if "PRIMEIRAS DECLARACOES" in H:
        return "primeiras-declaracoes"
    if "ULTIMAS DECLARACOES" in H:
        return "ultimas-declaracoes"
    if "FORMAL DE PARTILHA" in H or "CARTA DE ADJUDICACAO" in H:
        return "formal-partilha"
    if "INVENTARIO JUDICIAL" in H or ("INVENTARIO" in H and ("JUIZO" in H or "VARA" in H)):
        return "inventario-judicial"
    if "INVENTARIO" in H:
        return "inventario-judicial"

    # --- Petições intermediárias ---
    if "IMPUGNACAO AO LAUDO" in H:
        return "impugnacao-laudo-pericial"
    if "QUESITOS PERICIAIS" in H or "APRESENTACAO DE QUESITOS" in H:
        return "quesitos-periciais"
    if "ESPECIFICACAO DE PROVAS" in H:
        return "especificacao-provas"
    if "REPLICA" in H or "IMPUGNACAO A CONTESTACAO" in H:
        return "replica-contestacao"
    if "MANIFESTACAO SOBRE DOCUMENTOS" in H:
        return "manifestacao-documentos"
    if "JUNTADA DE DOCUMENTOS" in H:
        return "juntada-documentos"
    if "TUTELA DE URGENCIA" in H or "TUTELA ANTECIPADA" in H:
        # Inicial pode pedir tutela; só classifica como incidental quando o
        # título principal é "TUTELA..." e não há "PETICAO INICIAL" antes.
        if "PETICAO INICIAL" not in H and "ACAO" not in H:
            return "tutela-urgencia-incidental"

    # --- Benefícios previdenciários (título da ação) ---
    if "APOSENTADORIA ESPECIAL" in H:
        return "aposentadoria-especial"
    if "APOSENTADORIA POR IDADE RURAL" in H or (
        "APOSENTADORIA" in H and ("RURAL" in H or "RURICOLA" in H or "TRABALHADOR RURAL" in H)
    ):
        return "aposentadoria-idade-rural"
    if "APOSENTADORIA HIBRIDA" in H:
        return "aposentadoria-hibrida"
    if "APOSENTADORIA" in H and "TEMPO DE CONTRIBUICAO" in H and ("DEFICIENCIA" in H or "PCD" in H):
        return "aposentadoria-pcd-tempo"
    if "APOSENTADORIA" in H and "TEMPO DE CONTRIBUICAO" in H:
        return "aposentadoria-tempo-contribuicao"
    if "APOSENTADORIA" in H and "POR IDADE" in H and ("DEFICIENCIA" in H or "PCD" in H):
        return "aposentadoria-pcd-idade"
    if "APOSENTADORIA" in H and "POR IDADE" in H:
        return "aposentadoria-idade-urbana"
    if "APOSENTADORIA POR INVALIDEZ ACIDENTARIA" in H or "B-92" in H or "B92" in H:
        return "aposentadoria-invalidez-acidentaria"
    if "APOSENTADORIA POR INCAPACIDADE PERMANENTE" in H or "APOSENTADORIA POR INVALIDEZ" in H:
        return "aposentadoria-incapacidade-permanente"
    if "REVISAO DE APOSENTADORIA" in H or ("APOSENTADORIA" in H and "REVISAO" in H):
        return "revisao-aposentadoria"

    if ("AUXILIO-ACIDENTE" in H or "AUXILIO ACIDENTE" in H or "B-36" in H or "B36" in H):
        if "REVISAO" in H:
            return "revisao-auxilio-acidente"
        return "auxilio-acidente"
    if (
        "AUXILIO-DOENCA" in H
        or "AUXILIO DOENCA" in H
        or "AUXILIO POR INCAPACIDADE TEMPORARIA" in H
        or "INCAPACIDADE TEMPORARIA" in H
    ):
        if "REVISAO" in H:
            return "revisao-auxilio-incapacidade-temporaria"
        if "RESTABELEC" in H:
            return "restabelecimento-beneficio-incapacidade"
        return "auxilio-incapacidade-temporaria"
    if "AUXILIO-RECLUSAO" in H or "AUXILIO RECLUSAO" in H:
        return "auxilio-reclusao"
    if "PENSAO POR MORTE" in H:
        if "REVISAO" in H:
            return "revisao-pensao-por-morte"
        return "pensao-por-morte"
    if "SALARIO-MATERNIDADE" in H or "SALARIO MATERNIDADE" in H:
        return "salario-maternidade"
    if "RECONHECIMENTO" in H and "TEMPO DE CONTRIBUICAO" in H:
        return "reconhecimento-tempo-contribuicao"
    if "RECONHECIMENTO" in H and "ATIVIDADE ESPECIAL" in H:
        return "reconhecimento-atividade-especial"

    # --- BPC/LOAS (título) ---
    if "BPC" in H or "LOAS" in H:
        if "REVISAO" in H or "RESTABELEC" in H:
            return "bpc-revisao-restabelecimento"
        if "DEFICIENCIA" in H:
            return "bpc-deficiencia-judicial"
        if "IDOSO" in H or "65 ANOS" in H:
            return "bpc-idoso-judicial"

    return None


def _detect_admin(head_norm: str) -> str | None:
    """Detector específico para fluxo administrativo (INSS/CRPS).

    Só dispara quando a primeira linha indica destinatário administrativo.
    """
    H = head_norm
    if "BPC" in H or "LOAS" in H:
        if "RECURSO" in H:
            return "recurso-bpc"
        if "DEFICIENCIA" in H:
            return "requerimento-bpc-deficiencia"
        return "requerimento-bpc-idoso"
    if "CTC" in H or "CERTIDAO DE TEMPO" in H:
        return "ctc"
    if "COPIA INTEGRAL" in H or "COPIA DO PROCESSO" in H:
        return "copia-processo-administrativo"
    if "RETIFICACAO" in H and "CNIS" in H:
        return "retificacao-cnis"
    if "ACERTO" in H and "CNIS" in H:
        return "acerto-vinculos-remuneracoes"
    if "JUSTIFICACAO ADMINISTRATIVA" in H:
        return "justificacao-administrativa"
    if "REGULARIZACAO" in H and ("REPRESENTANTE" in H or "PROCURADOR" in H):
        return "regularizacao-representante"
    if "PRIORIDADE" in H and "TRAMITACAO" in H:
        return "pedido-prioridade"
    if "CUMPRIMENTO DE EXIGENCIA" in H:
        return "cumprimento-exigencia"
    if "RECURSO" in H and "CRPS" in H:
        if "ORDINARIO" in H:
            return "recurso-ordinario-crps"
        if "ESPECIAL" in H:
            return "recurso-especial-crps"
        return "recurso-crps"
    if "RECONSIDERACAO" in H:
        return "pedido-reconsideracao-administrativa"
    return None


def infer_piece_type_id(texto: str) -> str | None:
    """Tenta identificar a peça a partir do texto.

    Estratégia em camadas, **da mais específica para a mais genérica**:

    1. **Cabeçalho explícito** de instrumentos privados (procurações,
       substabelecimentos, declarações). Quando a primeira linha é o nome
       do instrumento, a decisão é praticamente inequívoca.
    2. **Título da ação nas primeiras linhas** (até 30 não vazias). Aqui
       ficam recursos, cumprimento de sentença, mandado de segurança,
       sucessório, intermediárias e benefícios previdenciários.
    3. **Cabeçalho administrativo** (AO INSTITUTO, AO INSS, AO CRPS, etc.)
       com sub-classificação por palavra-chave do título.
    4. **Cabeçalho judicial genérico** (EXCELENTÍSSIMO, AO JUÍZO) sem
       título reconhecido → fallback ``peticao-simples``.
    5. Texto sem qualquer cabeçalho jurídico → ``None`` (caller aplica
       perfil padrão e segue sem rótulo de peça).

    Por que título antes de palavras-chave do corpo: textos jurídicos
    citam jurisprudência, doutrina e termos relacionados que produziam
    falsos positivos no detector anterior (ex.: petição de aposentadoria
    rural era classificada como "agravo de instrumento" porque citava um
    acórdão de agravo). Limitar a inferência ao topo do documento elimina
    quase todos esses ruídos.
    """
    if not texto or not texto.strip():
        return None

    linhas = [linha.strip() for linha in texto.splitlines() if linha.strip()]
    if not linhas:
        return None

    primeira_norm = _normalize_for_match(linhas[0])
    # Duas visões do cabeçalho:
    #   - estrita: apenas linhas curtas em CAIXA ALTA (títulos reais);
    #   - frouxa: primeiras linhas em qualquer caso, como rede de segurança
    #     para textos coloquiais que não seguem a tradição forense.
    titulos = _title_candidates(linhas)
    head_norm_strict = _normalize_for_match("\n".join(titulos))
    head_norm_loose = _normalize_for_match("\n".join(linhas[:10]))
    body_lower = texto.lower()

    # === 1. Instrumentos privados pelo cabeçalho ===
    if primeira_norm.startswith((
        "PROCURACAO",
        "INSTRUMENTO PARTICULAR DE PROCURACAO",
        "INSTRUMENTO PUBLICO DE PROCURACAO",
    )):
        if "ad judicia et extra" in body_lower or "judicia et extra" in body_lower:
            return "procuracao-ad-judicia-et-extra"
        if any(k in body_lower for k in ("inss", "previdenciári", "previdenciari", "administrativ")):
            return "procuracao-administrativa-inss"
        return "procuracao-ad-judicia"

    if primeira_norm.startswith(("SUBSTABELECIMENTO", "SUBSTABELECEMENTO")):
        if "sem reserva" in body_lower:
            return "substabelecimento-sem-reserva"
        return "substabelecimento-com-reserva"

    if primeira_norm.startswith("DECLARACAO"):
        if "hipossufic" in body_lower:
            return "declaracao-hipossuficiencia"
        if "atividade rural" in body_lower or "rurícola" in body_lower or "ruricola" in body_lower:
            return "declaracao-atividade-rural"
        if "residênci" in body_lower or "residenci" in body_lower or "resido " in body_lower:
            return "declaracao-residencia"
        # DECLARAÇÃO genérica não reconhecida — não força fallback aqui
        # para que o caller aplique perfil judicial padrão.
        return None

    # === 2. Cabeçalho administrativo INSS/CRPS (precede title-detect
    #        para evitar que BPC/LOAS no head dispare a regra judicial) ===
    is_admin = primeira_norm.startswith((
        "AO INSTITUTO",
        "AO INSS",
        "AO CRPS",
        "A AGENCIA",
        "AGENCIA",
        "A GERENCIA",
        "AO PRESIDENTE DO INSS",
    ))
    if is_admin:
        admin = _detect_admin(head_norm_strict) or _detect_admin(head_norm_loose)
        # Cabeçalho administrativo sem subtipo específico cai em
        # "requerimento-inss-geral" como fallback útil.
        return admin or "requerimento-inss-geral"

    # === 3. Título da ação nas primeiras linhas (judicial) ===
    # Primeiro a varredura estrita (só CAIXA ALTA), que elimina ruído de
    # citação de jurisprudência. Se nada bater, repetimos com cabeçalho
    # frouxo para acomodar textos coloquiais.
    titulo = _detect_from_title(head_norm_strict)
    if titulo:
        return titulo
    titulo = _detect_from_title(head_norm_loose)
    if titulo:
        return titulo

    # === 4. Cabeçalho judicial sem título → petição simples ===
    if primeira_norm.startswith((
        "EXCELENT",
        "AO JUIZO",
        "MERITISSIMO",
    )):
        return "peticao-simples"

    return None


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
    PieceType("auxilio-incapacidade-temporaria", "Petição Inicial â€” Auxílio por Incapacidade Temporária", "Benefícios por incapacidade", "judicial-inicial-jef", "Base clínica, DII, profissão habitual e documentos médicos."),
    PieceType("aposentadoria-incapacidade-permanente", "Petição Inicial â€” Aposentadoria por Incapacidade Permanente", "Benefícios por incapacidade", "judicial-inicial-jef", "Base clínica, incapacidade total/permanente e condições pessoais."),
    PieceType("aposentadoria-invalidez-acidentaria", "Petição Inicial â€” Aposentadoria por Invalidez Acidentária (B-92)", "Benefícios por incapacidade", "judicial-inicial-estadual", "Nexo ocupacional, CAT e competência estadual."),
    PieceType("auxilio-acidente", "Petição Inicial â€” Auxílio-Acidente (B-36)", "Benefícios por incapacidade", "judicial-inicial-jef", "Consolidação das lesões e redução da capacidade laboral."),
    PieceType("restabelecimento-beneficio-incapacidade", "Petição Inicial â€” Restabelecimento de Benefício por Incapacidade Cessado", "Benefícios por incapacidade", "judicial-inicial-jef", "DCB, laudos contemporâneos e manutenção da incapacidade."),
    PieceType("aposentadoria-idade-urbana", "Petição Inicial â€” Aposentadoria por Idade Urbana", "Aposentadorias", "judicial-inicial-jef", "Carência, idade, CNIS e DER."),
    PieceType("aposentadoria-idade-rural", "Petição Inicial â€” Aposentadoria por Idade Rural", "Aposentadorias", "judicial-inicial-jef", "Prova rural, início de prova material e testemunhas."),
    PieceType("aposentadoria-hibrida", "Petição Inicial â€” Aposentadoria Híbrida", "Aposentadorias", "judicial-inicial-jef", "Períodos rurais/urbanos e cálculo de carência."),
    PieceType("aposentadoria-tempo-contribuicao", "Petição Inicial â€” Aposentadoria por Tempo de Contribuição", "Aposentadorias", "judicial-inicial-jef", "Direito adquirido ou regra de transição após EC 103/2019."),
    PieceType("aposentadoria-especial", "Petição Inicial â€” Aposentadoria Especial", "Aposentadorias", "judicial-inicial-jef", "PPP, LTCAT, agentes nocivos e conversão quando cabível."),
    PieceType("aposentadoria-pcd-tempo", "Petição Inicial â€” Aposentadoria por Tempo â€” Pessoa com Deficiência", "Aposentadorias", "judicial-inicial-jef", "Avaliação biopsicossocial e grau de deficiência."),
    PieceType("revisao-aposentadoria", "Petição Inicial â€” Revisão de Aposentadoria", "Aposentadorias", "judicial-inicial-jef", "RMI, DIB, CNIS, carta de concessão e tese revisional."),
    PieceType("pensao-por-morte", "Petição Inicial â€” Pensão por Morte", "Outros benefícios previdenciários", "judicial-inicial-jef", "Data do óbito, qualidade de segurado e dependência."),
    PieceType("salario-maternidade", "Petição Inicial â€” Salário-Maternidade", "Outros benefícios previdenciários", "judicial-inicial-jef", "Nascimento/adoção, qualidade de segurada e carência quando aplicável."),
    PieceType("reconhecimento-tempo-contribuicao", "Petição Inicial â€” Reconhecimento de Tempo de Contribuição", "Outros benefícios previdenciários", "judicial-inicial-jef", "Vínculos, CTPS, CNIS e provas complementares."),
    PieceType("bpc-deficiencia-judicial", "Petição Inicial â€” BPC/LOAS â€” Pessoa com Deficiência", "BPC/LOAS judicial", "judicial-inicial-jef", "Impedimento de longo prazo, CadÃšnico e miserabilidade."),
    PieceType("bpc-idoso-judicial", "Petição Inicial â€” BPC/LOAS â€” Idoso", "BPC/LOAS judicial", "judicial-inicial-jef", "Idade mínima, composição familiar e renda."),
    PieceType("ms-bpc-mora", "Mandado de Segurança â€” BPC/LOAS por Mora Administrativa", "BPC/LOAS judicial", "judicial-inicial-jef", "Distinguir mora continuada de indeferimento expresso."),
    PieceType("requerimento-bpc-idoso", "Requerimento Administrativo â€” BPC/LOAS â€” Idoso", "BPC/LOAS administrativo", "administrativo-inss", "CadÃšnico, composição familiar e renda."),
    PieceType("requerimento-bpc-deficiencia", "Requerimento Administrativo â€” BPC/LOAS â€” Pessoa com Deficiência", "BPC/LOAS administrativo", "administrativo-inss", "Base clínica e avaliação biopsicossocial."),
    PieceType("recurso-bpc", "Recurso Administrativo â€” BPC/LOAS", "BPC/LOAS administrativo", "administrativo-inss", "Decisão administrativa, fundamentos de impugnação e documentos."),
    PieceType("requerimento-inss-geral", "Requerimento Administrativo ao INSS â€” Geral", "Administrativo INSS", "administrativo-inss", "Pedido objetivo, documentos e identificação do requerente."),
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
    PieceType("cumprimento-sentenca-implantacao", "Cumprimento de Sentença â€” Implantação do Benefício", "Cumprimento de sentença", "forense-basico", "Título judicial, trânsito/fase e obrigação de fazer."),
    PieceType("cumprimento-sentenca-rpv", "Cumprimento de Sentença â€” Expedição de RPV", "Cumprimento de sentença", "forense-basico", "Cálculos, teto de RPV e dados bancários quando necessários."),
    PieceType("impugnacao-calculos", "Impugnação aos Cálculos", "Cumprimento de sentença", "forense-basico", "Memória de cálculo, divergência objetiva e documentos."),
    PieceType("juntada-documentos", "Petição de Juntada de Documentos", "Petições intermediárias", "forense-basico", "Processo, documentos e finalidade da juntada."),
    PieceType("replica-contestacao", "Réplica / Impugnação à Contestação", "Petições intermediárias", "forense-basico", "Contestação, preliminares e pontos controvertidos."),
    PieceType("manifestacao-documentos", "Manifestação sobre Documentos Novos", "Petições intermediárias", "forense-basico", "Documentos, pertinência e contraditório."),
    PieceType("peticao-simples", "Petição Simples / Outro", "Petições intermediárias", "forense-basico", "Finalidade objetiva e contexto processual."),
    PieceType("inventario-extrajudicial", "Inventário Extrajudicial", "Sucessório e extrajudicial", "extrajudicial-tabelionato", "Herdeiros, bens, ITCMD, testamento e incapazes."),
    PieceType("alvara-judicial", "Alvará Judicial", "Sucessório e extrajudicial", "judicial-inicial-estadual", "Cabimento, valores/bens e interessados."),
    PieceType("usucapiao", "Usucapião", "Cível e sucessório", "judicial-inicial-estadual", "Posse, tempo, imóvel, confrontantes e documentos."),
    PieceType("revisao-auxilio-incapacidade-temporaria", "Petição Inicial â€” Revisão de Auxílio por Incapacidade Temporária", "Benefícios por incapacidade", "judicial-inicial-jef", "DIB, RMI, período devido e base clínica da revisão."),
    PieceType("revisao-auxilio-acidente", "Petição Inicial â€” Revisão de Auxílio-Acidente", "Benefícios por incapacidade", "judicial-inicial-jef", "Critério de cálculo, sequelas e documentação médica."),
    PieceType("aposentadoria-pcd-idade", "Petição Inicial â€” Aposentadoria por Idade â€” Pessoa com Deficiência", "Aposentadorias", "judicial-inicial-jef", "Idade, deficiência, carência e avaliação biopsicossocial."),
    PieceType("reconhecimento-atividade-especial", "Petição Inicial â€” Reconhecimento de Atividade Especial", "Outros benefícios previdenciários", "judicial-inicial-jef", "PPP, LTCAT, agentes nocivos e enquadramento por período."),
    PieceType("auxilio-reclusao", "Petição Inicial â€” Auxílio-Reclusão", "Outros benefícios previdenciários", "judicial-inicial-jef", "Qualidade de segurado, baixa renda, dependência e certidão de reclusão."),
    PieceType("revisao-pensao-por-morte", "Petição Inicial â€” Revisão de Pensão por Morte", "Outros benefícios previdenciários", "judicial-inicial-jef", "Ã“bito, dependência, base de cálculo e tese revisional."),
    PieceType("bpc-revisao-restabelecimento", "Petição Inicial â€” Revisão / Restabelecimento de BPC/LOAS", "BPC/LOAS judicial", "judicial-inicial-jef", "Decisão de cessação/revisão, composição familiar e prova social atual."),
    PieceType("recurso-ordinario-crps", "Recurso Ordinário ao CRPS", "Administrativo INSS", "administrativo-inss", "Decisão administrativa, prazo recursal e fundamentos de reforma."),
    PieceType("recurso-especial-crps", "Recurso Especial ao CRPS", "Administrativo INSS", "administrativo-inss", "Divergência, admissibilidade e decisão recorrida."),
    PieceType("pedido-reconsideracao-administrativa", "Pedido de Reconsideração Administrativa", "Administrativo INSS", "administrativo-inss", "Decisão, fato novo ou erro administrativo objetivo."),
    PieceType("ctc", "Requerimento â€” Certidão de Tempo de Contribuição (CTC)", "Serviços administrativos INSS", "administrativo-inss", "Regime de destino, períodos e impedimentos de contagem recíproca."),
    PieceType("copia-processo-administrativo", "Requerimento â€” Cópia Integral do Processo Administrativo", "Serviços administrativos INSS", "administrativo-inss", "NB/protocolo, identificação do interessado e finalidade."),
    PieceType("retificacao-cnis", "Requerimento â€” Retificação / Atualização de CNIS", "Serviços administrativos INSS", "administrativo-inss", "Vínculos, remunerações, provas e período a corrigir."),
    PieceType("justificacao-administrativa", "Justificação Administrativa", "Serviços administrativos INSS", "administrativo-inss", "Fatos a provar, testemunhas e documentos mínimos."),
    PieceType("acerto-vinculos-remuneracoes", "Requerimento â€” Acerto de Vínculos e Remunerações no CNIS", "Serviços administrativos INSS", "administrativo-inss", "Vínculo, remuneração, competência e prova documental."),
    PieceType("regularizacao-representante", "Requerimento â€” Regularização de Representante / Procurador", "Serviços administrativos INSS", "administrativo-inss", "Documento de representação, poderes e dados do procurador."),
    PieceType("agravo-interno", "Agravo Interno", "Recursos e impugnações", "forense-basico", "Decisão monocrática, prazo e fundamentos de reforma."),
    PieceType("pedilef-tnu", "Pedido de Uniformização de Interpretação de Lei (PEDILEF/TNU)", "Recursos e impugnações", "forense-basico", "Divergência entre turmas, questão de direito material e admissibilidade."),
    PieceType("recurso-especial-stj", "Recurso Especial (STJ)", "Recursos e impugnações", "forense-basico", "Violação de lei federal, divergência e juízo de admissibilidade."),
    PieceType("recurso-extraordinario-stf", "Recurso Extraordinário (STF)", "Recursos e impugnações", "forense-basico", "Questão constitucional, repercussão geral e admissibilidade."),
    PieceType("juizo-retratacao", "Juízo de Retratação", "Recursos e impugnações", "forense-basico", "Tese vinculante, recurso repetitivo ou precedente aplicável."),
    PieceType("cumprimento-sentenca-precatorio", "Cumprimento de Sentença â€” Expedição de Precatório", "Cumprimento de sentença", "forense-basico", "Valor acima do teto de RPV, cálculos e dados necessários."),
    PieceType("cumprimento-sentenca-astreintes", "Cumprimento de Sentença â€” Astreintes por Descumprimento", "Cumprimento de sentença", "forense-basico", "Ordem judicial, prazo, descumprimento e cálculo da multa."),
    PieceType("impugnacao-cumprimento-sentenca", "Impugnação ao Cumprimento de Sentença", "Cumprimento de sentença", "forense-basico", "Excesso, inexigibilidade, nulidade ou tese defensiva cabível."),
    PieceType("habilitacao-sucessoria-processo", "Habilitação Sucessória no Curso do Processo", "Cumprimento de sentença", "forense-basico", "Ã“bito, sucessores, documentos e regularização processual."),
    PieceType("tutela-urgencia-incidental", "Petição de Tutela de Urgência / Antecipada", "Petições intermediárias", "forense-basico", "Probabilidade, perigo de dano e fase processual."),
    PieceType("impugnacao-laudo-pericial", "Impugnação ao Laudo Pericial", "Petições intermediárias", "forense-basico", "Laudo, contradições, quesitos e pedido de esclarecimentos."),
    PieceType("quesitos-periciais", "Apresentação de Quesitos Periciais", "Petições intermediárias", "forense-basico", "Objeto da perícia, quesitos técnicos e documentos de apoio."),
    PieceType("especificacao-provas", "Especificação de Provas", "Petições intermediárias", "forense-basico", "Fatos controvertidos, provas pretendidas e pertinência."),
    PieceType("sobrepartilha-extrajudicial", "Sobrepartilha Extrajudicial", "Sucessório e extrajudicial", "extrajudicial-tabelionato", "Bens sobrevindos, consenso e requisitos notariais."),
    PieceType("cessao-direitos-hereditarios", "Cessão de Direitos Hereditários", "Sucessório e extrajudicial", "extrajudicial-tabelionato", "Forma pública, cedente, cessionário, objeto e anuências."),
    PieceType("renuncia-heranca", "Renúncia à Herança / Repúdio", "Sucessório e extrajudicial", "extrajudicial-tabelionato", "Forma pública ou termo judicial e análise de credores."),
    PieceType("inventario-judicial", "Inventário Judicial â€” Petição Inicial", "Cível e sucessório", "judicial-inicial-estadual", "Ã“bito, bens, herdeiros, ITCMD, testamento e incapazes."),
    PieceType("arrolamento-simples", "Arrolamento Simples â€” Petição Inicial", "Cível e sucessório", "judicial-inicial-estadual", "Ã“bito, bens, herdeiros e adequação do rito."),
    PieceType("arrolamento-sumario", "Arrolamento Sumário â€” Petição Inicial", "Cível e sucessório", "judicial-inicial-estadual", "Consenso, herdeiros capazes, partilha e adequação do rito."),
    PieceType("sobrepartilha-judicial", "Sobrepartilha â€” Petição Inicial", "Cível e sucessório", "judicial-inicial-estadual", "Bens descobertos após partilha e legitimidade."),
    PieceType("formal-partilha", "Formal de Partilha / Carta de Adjudicação", "Cível e sucessório", "forense-basico", "Decisão homologatória, trânsito e dados dos bens/herdeiros."),
    PieceType("habilitacao-herdeiros", "Habilitação de Herdeiros", "Cível e sucessório", "forense-basico", "Ã“bito, sucessores e prova documental."),
    PieceType("primeiras-declaracoes", "Primeiras Declarações do Inventariante", "Cível e sucessório", "forense-basico", "Inventariante, herdeiros, bens, dívidas e plano inicial."),
    PieceType("ultimas-declaracoes", "Ãšltimas Declarações do Inventariante", "Cível e sucessório", "forense-basico", "Atualização de bens, dívidas, partilha e concordâncias."),
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


"""CatÃ¡logo de tipos de peÃ§as alinhado ao prompt jurÃ­dico versionado."""
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
    PieceType("auxilio-incapacidade-temporaria", "PetiÃ§Ã£o Inicial â€” AuxÃ­lio por Incapacidade TemporÃ¡ria", "BenefÃ­cios por incapacidade", "judicial-inicial-jef", "Base clÃ­nica, DII, profissÃ£o habitual e documentos mÃ©dicos."),
    PieceType("aposentadoria-incapacidade-permanente", "PetiÃ§Ã£o Inicial â€” Aposentadoria por Incapacidade Permanente", "BenefÃ­cios por incapacidade", "judicial-inicial-jef", "Base clÃ­nica, incapacidade total/permanente e condiÃ§Ãµes pessoais."),
    PieceType("aposentadoria-invalidez-acidentaria", "PetiÃ§Ã£o Inicial â€” Aposentadoria por Invalidez AcidentÃ¡ria (B-92)", "BenefÃ­cios por incapacidade", "judicial-inicial-estadual", "Nexo ocupacional, CAT e competÃªncia estadual."),
    PieceType("auxilio-acidente", "PetiÃ§Ã£o Inicial â€” AuxÃ­lio-Acidente (B-36)", "BenefÃ­cios por incapacidade", "judicial-inicial-jef", "ConsolidaÃ§Ã£o das lesÃµes e reduÃ§Ã£o da capacidade laboral."),
    PieceType("restabelecimento-beneficio-incapacidade", "PetiÃ§Ã£o Inicial â€” Restabelecimento de BenefÃ­cio por Incapacidade Cessado", "BenefÃ­cios por incapacidade", "judicial-inicial-jef", "DCB, laudos contemporÃ¢neos e manutenÃ§Ã£o da incapacidade."),
    PieceType("aposentadoria-idade-urbana", "PetiÃ§Ã£o Inicial â€” Aposentadoria por Idade Urbana", "Aposentadorias", "judicial-inicial-jef", "CarÃªncia, idade, CNIS e DER."),
    PieceType("aposentadoria-idade-rural", "PetiÃ§Ã£o Inicial â€” Aposentadoria por Idade Rural", "Aposentadorias", "judicial-inicial-jef", "Prova rural, inÃ­cio de prova material e testemunhas."),
    PieceType("aposentadoria-hibrida", "PetiÃ§Ã£o Inicial â€” Aposentadoria HÃ­brida", "Aposentadorias", "judicial-inicial-jef", "PerÃ­odos rurais/urbanos e cÃ¡lculo de carÃªncia."),
    PieceType("aposentadoria-tempo-contribuicao", "PetiÃ§Ã£o Inicial â€” Aposentadoria por Tempo de ContribuiÃ§Ã£o", "Aposentadorias", "judicial-inicial-jef", "Direito adquirido ou regra de transiÃ§Ã£o apÃ³s EC 103/2019."),
    PieceType("aposentadoria-especial", "PetiÃ§Ã£o Inicial â€” Aposentadoria Especial", "Aposentadorias", "judicial-inicial-jef", "PPP, LTCAT, agentes nocivos e conversÃ£o quando cabÃ­vel."),
    PieceType("aposentadoria-pcd-tempo", "PetiÃ§Ã£o Inicial â€” Aposentadoria por Tempo â€” Pessoa com DeficiÃªncia", "Aposentadorias", "judicial-inicial-jef", "AvaliaÃ§Ã£o biopsicossocial e grau de deficiÃªncia."),
    PieceType("revisao-aposentadoria", "PetiÃ§Ã£o Inicial â€” RevisÃ£o de Aposentadoria", "Aposentadorias", "judicial-inicial-jef", "RMI, DIB, CNIS, carta de concessÃ£o e tese revisional."),
    PieceType("pensao-por-morte", "PetiÃ§Ã£o Inicial â€” PensÃ£o por Morte", "Outros benefÃ­cios previdenciÃ¡rios", "judicial-inicial-jef", "Data do Ã³bito, qualidade de segurado e dependÃªncia."),
    PieceType("salario-maternidade", "PetiÃ§Ã£o Inicial â€” SalÃ¡rio-Maternidade", "Outros benefÃ­cios previdenciÃ¡rios", "judicial-inicial-jef", "Nascimento/adoÃ§Ã£o, qualidade de segurada e carÃªncia quando aplicÃ¡vel."),
    PieceType("reconhecimento-tempo-contribuicao", "PetiÃ§Ã£o Inicial â€” Reconhecimento de Tempo de ContribuiÃ§Ã£o", "Outros benefÃ­cios previdenciÃ¡rios", "judicial-inicial-jef", "VÃ­nculos, CTPS, CNIS e provas complementares."),
    PieceType("bpc-deficiencia-judicial", "PetiÃ§Ã£o Inicial â€” BPC/LOAS â€” Pessoa com DeficiÃªncia", "BPC/LOAS judicial", "judicial-inicial-jef", "Impedimento de longo prazo, CadÃšnico e miserabilidade."),
    PieceType("bpc-idoso-judicial", "PetiÃ§Ã£o Inicial â€” BPC/LOAS â€” Idoso", "BPC/LOAS judicial", "judicial-inicial-jef", "Idade mÃ­nima, composiÃ§Ã£o familiar e renda."),
    PieceType("ms-bpc-mora", "Mandado de SeguranÃ§a â€” BPC/LOAS por Mora Administrativa", "BPC/LOAS judicial", "judicial-inicial-jef", "Distinguir mora continuada de indeferimento expresso."),
    PieceType("requerimento-bpc-idoso", "Requerimento Administrativo â€” BPC/LOAS â€” Idoso", "BPC/LOAS administrativo", "administrativo-inss", "CadÃšnico, composiÃ§Ã£o familiar e renda."),
    PieceType("requerimento-bpc-deficiencia", "Requerimento Administrativo â€” BPC/LOAS â€” Pessoa com DeficiÃªncia", "BPC/LOAS administrativo", "administrativo-inss", "Base clÃ­nica e avaliaÃ§Ã£o biopsicossocial."),
    PieceType("recurso-bpc", "Recurso Administrativo â€” BPC/LOAS", "BPC/LOAS administrativo", "administrativo-inss", "DecisÃ£o administrativa, fundamentos de impugnaÃ§Ã£o e documentos."),
    PieceType("requerimento-inss-geral", "Requerimento Administrativo ao INSS â€” Geral", "Administrativo INSS", "administrativo-inss", "Pedido objetivo, documentos e identificaÃ§Ã£o do requerente."),
    PieceType("recurso-crps", "Recurso Administrativo ao INSS / CRPS", "Administrativo INSS", "administrativo-inss", "DecisÃ£o, prazo, pontos impugnados e provas."),
    PieceType("cumprimento-exigencia", "Cumprimento de ExigÃªncia Administrativa", "Administrativo INSS", "administrativo-inss", "Texto integral da exigÃªncia e resposta item a item."),
    PieceType("pedido-prioridade", "Pedido de Prioridade de TramitaÃ§Ã£o", "Administrativo INSS", "administrativo-inss", "Idade, doenÃ§a grave ou fundamento legal da prioridade."),
    PieceType("mandado-seguranca-previdenciario", "Mandado de SeguranÃ§a PrevidenciÃ¡rio", "AÃ§Ãµes especiais", "judicial-inicial-jef", "Ato coator, autoridade, prazo decadencial e prova prÃ©-constituÃ­da."),
    PieceType("tutela-antecedente", "Tutela Antecipada em CarÃ¡ter Antecedente", "AÃ§Ãµes especiais", "judicial-inicial-estadual", "Probabilidade do direito, perigo de dano e pedido final futuro."),
    PieceType("recurso-inominado", "Recurso Inominado (JEF)", "Recursos e impugnaÃ§Ãµes", "forense-basico", "SentenÃ§a, prazo, fundamentos recursais e pedidos."),
    PieceType("apelacao-civel", "ApelaÃ§Ã£o CÃ­vel", "Recursos e impugnaÃ§Ãµes", "forense-basico", "SentenÃ§a, capÃ­tulos impugnados e preparo quando cabÃ­vel."),
    PieceType("agravo-instrumento", "Agravo de Instrumento", "Recursos e impugnaÃ§Ãµes", "forense-basico", "DecisÃ£o agravada, urgÃªncia e peÃ§as obrigatÃ³rias."),
    PieceType("embargos-declaracao", "Embargos de DeclaraÃ§Ã£o", "Recursos e impugnaÃ§Ãµes", "forense-basico", "OmissÃ£o, contradiÃ§Ã£o, obscuridade ou erro material."),
    PieceType("contrarrazoes", "ContrarrazÃµes de Recurso", "Recursos e impugnaÃ§Ãµes", "forense-basico", "Recurso adverso, preliminares e manutenÃ§Ã£o da decisÃ£o."),
    PieceType("cumprimento-sentenca-implantacao", "Cumprimento de SentenÃ§a â€” ImplantaÃ§Ã£o do BenefÃ­cio", "Cumprimento de sentenÃ§a", "forense-basico", "TÃ­tulo judicial, trÃ¢nsito/fase e obrigaÃ§Ã£o de fazer."),
    PieceType("cumprimento-sentenca-rpv", "Cumprimento de SentenÃ§a â€” ExpediÃ§Ã£o de RPV", "Cumprimento de sentenÃ§a", "forense-basico", "CÃ¡lculos, teto de RPV e dados bancÃ¡rios quando necessÃ¡rios."),
    PieceType("impugnacao-calculos", "ImpugnaÃ§Ã£o aos CÃ¡lculos", "Cumprimento de sentenÃ§a", "forense-basico", "MemÃ³ria de cÃ¡lculo, divergÃªncia objetiva e documentos."),
    PieceType("juntada-documentos", "PetiÃ§Ã£o de Juntada de Documentos", "PetiÃ§Ãµes intermediÃ¡rias", "forense-basico", "Processo, documentos e finalidade da juntada."),
    PieceType("replica-contestacao", "RÃ©plica / ImpugnaÃ§Ã£o Ã  ContestaÃ§Ã£o", "PetiÃ§Ãµes intermediÃ¡rias", "forense-basico", "ContestaÃ§Ã£o, preliminares e pontos controvertidos."),
    PieceType("manifestacao-documentos", "ManifestaÃ§Ã£o sobre Documentos Novos", "PetiÃ§Ãµes intermediÃ¡rias", "forense-basico", "Documentos, pertinÃªncia e contraditÃ³rio."),
    PieceType("peticao-simples", "PetiÃ§Ã£o Simples / Outro", "PetiÃ§Ãµes intermediÃ¡rias", "forense-basico", "Finalidade objetiva e contexto processual."),
    PieceType("inventario-extrajudicial", "InventÃ¡rio Extrajudicial", "SucessÃ³rio e extrajudicial", "extrajudicial-tabelionato", "Herdeiros, bens, ITCMD, testamento e incapazes."),
    PieceType("alvara-judicial", "AlvarÃ¡ Judicial", "SucessÃ³rio e extrajudicial", "judicial-inicial-estadual", "Cabimento, valores/bens e interessados."),
    PieceType("usucapiao", "UsucapiÃ£o", "CÃ­vel e sucessÃ³rio", "judicial-inicial-estadual", "Posse, tempo, imÃ³vel, confrontantes e documentos."),
    PieceType("revisao-auxilio-incapacidade-temporaria", "PetiÃ§Ã£o Inicial â€” RevisÃ£o de AuxÃ­lio por Incapacidade TemporÃ¡ria", "BenefÃ­cios por incapacidade", "judicial-inicial-jef", "DIB, RMI, perÃ­odo devido e base clÃ­nica da revisÃ£o."),
    PieceType("revisao-auxilio-acidente", "PetiÃ§Ã£o Inicial â€” RevisÃ£o de AuxÃ­lio-Acidente", "BenefÃ­cios por incapacidade", "judicial-inicial-jef", "CritÃ©rio de cÃ¡lculo, sequelas e documentaÃ§Ã£o mÃ©dica."),
    PieceType("aposentadoria-pcd-idade", "PetiÃ§Ã£o Inicial â€” Aposentadoria por Idade â€” Pessoa com DeficiÃªncia", "Aposentadorias", "judicial-inicial-jef", "Idade, deficiÃªncia, carÃªncia e avaliaÃ§Ã£o biopsicossocial."),
    PieceType("reconhecimento-atividade-especial", "PetiÃ§Ã£o Inicial â€” Reconhecimento de Atividade Especial", "Outros benefÃ­cios previdenciÃ¡rios", "judicial-inicial-jef", "PPP, LTCAT, agentes nocivos e enquadramento por perÃ­odo."),
    PieceType("auxilio-reclusao", "PetiÃ§Ã£o Inicial â€” AuxÃ­lio-ReclusÃ£o", "Outros benefÃ­cios previdenciÃ¡rios", "judicial-inicial-jef", "Qualidade de segurado, baixa renda, dependÃªncia e certidÃ£o de reclusÃ£o."),
    PieceType("revisao-pensao-por-morte", "PetiÃ§Ã£o Inicial â€” RevisÃ£o de PensÃ£o por Morte", "Outros benefÃ­cios previdenciÃ¡rios", "judicial-inicial-jef", "Ã“bito, dependÃªncia, base de cÃ¡lculo e tese revisional."),
    PieceType("bpc-revisao-restabelecimento", "PetiÃ§Ã£o Inicial â€” RevisÃ£o / Restabelecimento de BPC/LOAS", "BPC/LOAS judicial", "judicial-inicial-jef", "DecisÃ£o de cessaÃ§Ã£o/revisÃ£o, composiÃ§Ã£o familiar e prova social atual."),
    PieceType("recurso-ordinario-crps", "Recurso OrdinÃ¡rio ao CRPS", "Administrativo INSS", "administrativo-inss", "DecisÃ£o administrativa, prazo recursal e fundamentos de reforma."),
    PieceType("recurso-especial-crps", "Recurso Especial ao CRPS", "Administrativo INSS", "administrativo-inss", "DivergÃªncia, admissibilidade e decisÃ£o recorrida."),
    PieceType("pedido-reconsideracao-administrativa", "Pedido de ReconsideraÃ§Ã£o Administrativa", "Administrativo INSS", "administrativo-inss", "DecisÃ£o, fato novo ou erro administrativo objetivo."),
    PieceType("ctc", "Requerimento â€” CertidÃ£o de Tempo de ContribuiÃ§Ã£o (CTC)", "ServiÃ§os administrativos INSS", "administrativo-inss", "Regime de destino, perÃ­odos e impedimentos de contagem recÃ­proca."),
    PieceType("copia-processo-administrativo", "Requerimento â€” CÃ³pia Integral do Processo Administrativo", "ServiÃ§os administrativos INSS", "administrativo-inss", "NB/protocolo, identificaÃ§Ã£o do interessado e finalidade."),
    PieceType("retificacao-cnis", "Requerimento â€” RetificaÃ§Ã£o / AtualizaÃ§Ã£o de CNIS", "ServiÃ§os administrativos INSS", "administrativo-inss", "VÃ­nculos, remuneraÃ§Ãµes, provas e perÃ­odo a corrigir."),
    PieceType("justificacao-administrativa", "JustificaÃ§Ã£o Administrativa", "ServiÃ§os administrativos INSS", "administrativo-inss", "Fatos a provar, testemunhas e documentos mÃ­nimos."),
    PieceType("acerto-vinculos-remuneracoes", "Requerimento â€” Acerto de VÃ­nculos e RemuneraÃ§Ãµes no CNIS", "ServiÃ§os administrativos INSS", "administrativo-inss", "VÃ­nculo, remuneraÃ§Ã£o, competÃªncia e prova documental."),
    PieceType("regularizacao-representante", "Requerimento â€” RegularizaÃ§Ã£o de Representante / Procurador", "ServiÃ§os administrativos INSS", "administrativo-inss", "Documento de representaÃ§Ã£o, poderes e dados do procurador."),
    PieceType("agravo-interno", "Agravo Interno", "Recursos e impugnaÃ§Ãµes", "forense-basico", "DecisÃ£o monocrÃ¡tica, prazo e fundamentos de reforma."),
    PieceType("pedilef-tnu", "Pedido de UniformizaÃ§Ã£o de InterpretaÃ§Ã£o de Lei (PEDILEF/TNU)", "Recursos e impugnaÃ§Ãµes", "forense-basico", "DivergÃªncia entre turmas, questÃ£o de direito material e admissibilidade."),
    PieceType("recurso-especial-stj", "Recurso Especial (STJ)", "Recursos e impugnaÃ§Ãµes", "forense-basico", "ViolaÃ§Ã£o de lei federal, divergÃªncia e juÃ­zo de admissibilidade."),
    PieceType("recurso-extraordinario-stf", "Recurso ExtraordinÃ¡rio (STF)", "Recursos e impugnaÃ§Ãµes", "forense-basico", "QuestÃ£o constitucional, repercussÃ£o geral e admissibilidade."),
    PieceType("juizo-retratacao", "JuÃ­zo de RetrataÃ§Ã£o", "Recursos e impugnaÃ§Ãµes", "forense-basico", "Tese vinculante, recurso repetitivo ou precedente aplicÃ¡vel."),
    PieceType("cumprimento-sentenca-precatorio", "Cumprimento de SentenÃ§a â€” ExpediÃ§Ã£o de PrecatÃ³rio", "Cumprimento de sentenÃ§a", "forense-basico", "Valor acima do teto de RPV, cÃ¡lculos e dados necessÃ¡rios."),
    PieceType("cumprimento-sentenca-astreintes", "Cumprimento de SentenÃ§a â€” Astreintes por Descumprimento", "Cumprimento de sentenÃ§a", "forense-basico", "Ordem judicial, prazo, descumprimento e cÃ¡lculo da multa."),
    PieceType("impugnacao-cumprimento-sentenca", "ImpugnaÃ§Ã£o ao Cumprimento de SentenÃ§a", "Cumprimento de sentenÃ§a", "forense-basico", "Excesso, inexigibilidade, nulidade ou tese defensiva cabÃ­vel."),
    PieceType("habilitacao-sucessoria-processo", "HabilitaÃ§Ã£o SucessÃ³ria no Curso do Processo", "Cumprimento de sentenÃ§a", "forense-basico", "Ã“bito, sucessores, documentos e regularizaÃ§Ã£o processual."),
    PieceType("tutela-urgencia-incidental", "PetiÃ§Ã£o de Tutela de UrgÃªncia / Antecipada", "PetiÃ§Ãµes intermediÃ¡rias", "forense-basico", "Probabilidade, perigo de dano e fase processual."),
    PieceType("impugnacao-laudo-pericial", "ImpugnaÃ§Ã£o ao Laudo Pericial", "PetiÃ§Ãµes intermediÃ¡rias", "forense-basico", "Laudo, contradiÃ§Ãµes, quesitos e pedido de esclarecimentos."),
    PieceType("quesitos-periciais", "ApresentaÃ§Ã£o de Quesitos Periciais", "PetiÃ§Ãµes intermediÃ¡rias", "forense-basico", "Objeto da perÃ­cia, quesitos tÃ©cnicos e documentos de apoio."),
    PieceType("especificacao-provas", "EspecificaÃ§Ã£o de Provas", "PetiÃ§Ãµes intermediÃ¡rias", "forense-basico", "Fatos controvertidos, provas pretendidas e pertinÃªncia."),
    PieceType("sobrepartilha-extrajudicial", "Sobrepartilha Extrajudicial", "SucessÃ³rio e extrajudicial", "extrajudicial-tabelionato", "Bens sobrevindos, consenso e requisitos notariais."),
    PieceType("cessao-direitos-hereditarios", "CessÃ£o de Direitos HereditÃ¡rios", "SucessÃ³rio e extrajudicial", "extrajudicial-tabelionato", "Forma pÃºblica, cedente, cessionÃ¡rio, objeto e anuÃªncias."),
    PieceType("renuncia-heranca", "RenÃºncia Ã  HeranÃ§a / RepÃºdio", "SucessÃ³rio e extrajudicial", "extrajudicial-tabelionato", "Forma pÃºblica ou termo judicial e anÃ¡lise de credores."),
    PieceType("inventario-judicial", "InventÃ¡rio Judicial â€” PetiÃ§Ã£o Inicial", "CÃ­vel e sucessÃ³rio", "judicial-inicial-estadual", "Ã“bito, bens, herdeiros, ITCMD, testamento e incapazes."),
    PieceType("arrolamento-simples", "Arrolamento Simples â€” PetiÃ§Ã£o Inicial", "CÃ­vel e sucessÃ³rio", "judicial-inicial-estadual", "Ã“bito, bens, herdeiros e adequaÃ§Ã£o do rito."),
    PieceType("arrolamento-sumario", "Arrolamento SumÃ¡rio â€” PetiÃ§Ã£o Inicial", "CÃ­vel e sucessÃ³rio", "judicial-inicial-estadual", "Consenso, herdeiros capazes, partilha e adequaÃ§Ã£o do rito."),
    PieceType("sobrepartilha-judicial", "Sobrepartilha â€” PetiÃ§Ã£o Inicial", "CÃ­vel e sucessÃ³rio", "judicial-inicial-estadual", "Bens descobertos apÃ³s partilha e legitimidade."),
    PieceType("formal-partilha", "Formal de Partilha / Carta de AdjudicaÃ§Ã£o", "CÃ­vel e sucessÃ³rio", "forense-basico", "DecisÃ£o homologatÃ³ria, trÃ¢nsito e dados dos bens/herdeiros."),
    PieceType("habilitacao-herdeiros", "HabilitaÃ§Ã£o de Herdeiros", "CÃ­vel e sucessÃ³rio", "forense-basico", "Ã“bito, sucessores e prova documental."),
    PieceType("primeiras-declaracoes", "Primeiras DeclaraÃ§Ãµes do Inventariante", "CÃ­vel e sucessÃ³rio", "forense-basico", "Inventariante, herdeiros, bens, dÃ­vidas e plano inicial."),
    PieceType("ultimas-declaracoes", "Ãšltimas DeclaraÃ§Ãµes do Inventariante", "CÃ­vel e sucessÃ³rio", "forense-basico", "AtualizaÃ§Ã£o de bens, dÃ­vidas, partilha e concordÃ¢ncias."),
    PieceType("nomeacao-inventariante", "NomeaÃ§Ã£o / SubstituiÃ§Ã£o / RemoÃ§Ã£o de Inventariante", "CÃ­vel e sucessÃ³rio", "forense-basico", "Legitimidade, motivo e documentos do inventÃ¡rio."),
    PieceType("procuracao-ad-judicia", "ProcuraÃ§Ã£o Ad Judicia", "Instrumentos de mandato", "instrumento-mandato", "Outorgante, outorgado, poderes, foro, data e assinatura."),
    PieceType("procuracao-administrativa-inss", "ProcuraÃ§Ã£o Administrativa PrevidenciÃ¡ria / INSS", "Instrumentos de mandato", "instrumento-mandato", "Outorgante, procurador, poderes administrativos e validade."),
    PieceType("procuracao-ad-judicia-et-extra", "ProcuraÃ§Ã£o Ad Judicia et Extra", "Instrumentos de mandato", "instrumento-mandato", "Poderes judiciais e extrajudiciais devem ser expressos e revisados."),
    PieceType("substabelecimento-com-reserva", "Substabelecimento com Reserva de Poderes", "Instrumentos de mandato", "instrumento-mandato", "ProcuraÃ§Ã£o originÃ¡ria, substabelecente, substabelecido e reserva expressa."),
    PieceType("substabelecimento-sem-reserva", "Substabelecimento sem Reserva de Poderes", "Instrumentos de mandato", "instrumento-mandato", "ProcuraÃ§Ã£o originÃ¡ria, ciÃªncia do cliente e transferÃªncia integral de poderes."),
    PieceType("declaracao-hipossuficiencia", "DeclaraÃ§Ã£o de HipossuficiÃªncia", "Instrumentos e declaraÃ§Ãµes", "instrumento-mandato", "Declarante, situaÃ§Ã£o econÃ´mica, data e assinatura."),
    PieceType("declaracao-residencia", "DeclaraÃ§Ã£o de ResidÃªncia", "Instrumentos e declaraÃ§Ãµes", "instrumento-mandato", "Declarante, endereÃ§o, finalidade e assinatura."),
    PieceType("declaracao-atividade-rural", "DeclaraÃ§Ã£o de Atividade Rural", "Instrumentos e declaraÃ§Ãµes", "instrumento-mandato", "PerÃ­odo, atividade, local, testemunhas e documentos."),
)


def list_piece_types() -> list[PieceType]:
    return sorted(PIECE_TYPES, key=lambda item: (item.grupo, item.nome))


def get_piece_type(piece_type_id: str | None) -> PieceType | None:
    if not piece_type_id:
        return None
    for piece_type in PIECE_TYPES:
        if piece_type.id == piece_type_id:
            return piece_type
    raise ValueError(f"tipo de peÃ§a desconhecido: {piece_type_id}")


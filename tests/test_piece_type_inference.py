"""Testes do detector automático de tipo de peça."""
from __future__ import annotations

import pytest

from src.core.piece_inference import infer_piece_type_id
from src.core.piece_types import PIECE_TYPES, get_piece_type, list_piece_types


VALID_IDS = {item.id for item in PIECE_TYPES}


@pytest.mark.parametrize(
    "texto, esperado",
    [
        (
            "PROCURAÇÃO AD JUDICIA\n\nOutorgante: Fulano de Tal...",
            "procuracao-ad-judicia",
        ),
        (
            "PROCURAÇÃO AD JUDICIA ET EXTRA\n\npara fins judiciais e extrajudiciais",
            "procuracao-ad-judicia-et-extra",
        ),
        (
            "PROCURAÇÃO\n\nOutorga poderes para representação perante o INSS.",
            "procuracao-administrativa-inss",
        ),
        (
            "SUBSTABELECIMENTO COM RESERVA DE PODERES\n\nO advogado substabelece...",
            "substabelecimento-com-reserva",
        ),
        (
            "SUBSTABELECIMENTO SEM RESERVA DE PODERES\n\nTransfere integralmente...",
            "substabelecimento-sem-reserva",
        ),
        (
            "DECLARAÇÃO DE HIPOSSUFICIÊNCIA\n\nDeclaro, sob as penas da lei...",
            "declaracao-hipossuficiencia",
        ),
        (
            "EXCELENTÍSSIMO SENHOR DOUTOR JUIZ\n\nFulano interpõe RECURSO INOMINADO contra a sentença...",
            "recurso-inominado",
        ),
        (
            "EXCELENTÍSSIMO SENHOR DESEMBARGADOR\n\nApelação Cível em face da sentença que julgou improcedente...",
            "apelacao-civel",
        ),
        (
            "EMBARGOS DE DECLARAÇÃO\n\nA sentença incorreu em omissão...",
            "embargos-declaracao",
        ),
        (
            "EXCELENTÍSSIMO\n\nCumprimento de sentença para expedição de RPV no valor de...",
            "cumprimento-sentenca-rpv",
        ),
        (
            "EXCELENTÍSSIMO\n\nCumprimento de sentença para implantação do benefício previdenciário...",
            "cumprimento-sentenca-implantacao",
        ),
        (
            "EXCELENTÍSSIMO\n\nMandado de segurança previdenciário em face do ato coator...",
            "mandado-seguranca-previdenciario",
        ),
        (
            "AO TABELIONATO\n\nInventário extrajudicial com partilha consensual...",
            "inventario-extrajudicial",
        ),
        (
            "EXCELENTÍSSIMO\n\nUsucapião extraordinária do imóvel localizado em...",
            "usucapiao",
        ),
        (
            "AO INSTITUTO NACIONAL DO SEGURO SOCIAL\n\nRequerimento de retificação do CNIS...",
            "retificacao-cnis",
        ),
        (
            "AO INSTITUTO NACIONAL DO SEGURO SOCIAL\n\nRequerimento de BPC/LOAS - pessoa idosa de 67 anos...",
            "requerimento-bpc-idoso",
        ),
        (
            "AO INSTITUTO NACIONAL DO SEGURO SOCIAL\n\nRequerimento de BPC/LOAS por deficiência...",
            "requerimento-bpc-deficiencia",
        ),
        (
            "AO CRPS\n\nRecurso ordinário em face do indeferimento administrativo...",
            "recurso-ordinario-crps",
        ),
        (
            "EXCELENTÍSSIMO SENHOR DOUTOR JUIZ FEDERAL\n\nVem propor a presente petição inicial buscando aposentadoria por idade rural...",
            "aposentadoria-idade-rural",
        ),
        (
            "EXCELENTÍSSIMO SENHOR DOUTOR JUIZ FEDERAL\n\nAposentadoria especial com base em PPP e LTCAT, agentes nocivos comprovados...",
            "aposentadoria-especial",
        ),
        (
            "EXCELENTÍSSIMO\n\nPensão por morte em razão do óbito do segurado...",
            "pensao-por-morte",
        ),
        (
            "EXCELENTÍSSIMO\n\nAuxílio-doença com base em incapacidade temporária comprovada por laudo...",
            "auxilio-incapacidade-temporaria",
        ),
        (
            "EXCELENTÍSSIMO\n\nBPC/LOAS - pessoa com deficiência, impedimento de longo prazo...",
            "bpc-deficiencia-judicial",
        ),
        (
            "EXCELENTÍSSIMO SENHOR DOUTOR JUIZ\n\nPetição genérica sem palavras-chave específicas.",
            "peticao-simples",
        ),
    ],
)
def test_inferencia_de_tipo_de_peca(texto: str, esperado: str) -> None:
    assert esperado in VALID_IDS, f"id de teste inválido: {esperado}"
    detected = infer_piece_type_id(texto)
    assert detected == esperado, f"esperava {esperado}, obteve {detected!r}"


def test_inferencia_retorna_none_para_texto_irrelevante() -> None:
    assert infer_piece_type_id("") is None
    assert infer_piece_type_id("   \n\n\t  ") is None
    assert infer_piece_type_id("texto solto sem cabeçalho jurídico nem palavra-chave reconhecível") is None


def test_inferencia_priorizando_titulo_sobre_corpo() -> None:
    texto = (
        "EXCELENTÍSSIMO SENHOR DOUTOR JUIZ FEDERAL\n\n"
        "PETIÇÃO INICIAL - AÇÃO DE APOSENTADORIA POR IDADE RURAL\n\n"
        "MARIA DA SILVA, qualificada nos autos, vem propor a presente ação. "
        "Cita-se, por oportuno, acórdão proferido em agravo de instrumento "
        "(TRF-1, AI 1234) e em recurso especial do STJ que confirmaram tese "
        "semelhante. Pleiteia-se aposentadoria por idade rural com base em "
        "início de prova material e prova testemunhal..."
    )
    assert infer_piece_type_id(texto) == "aposentadoria-idade-rural"


def test_inferencia_titulo_prefere_acao_principal() -> None:
    texto = (
        "EXCELENTÍSSIMO SENHOR DOUTOR JUIZ FEDERAL\n\n"
        "AÇÃO DE APOSENTADORIA POR INVALIDEZ\n\n"
        "Cumpre observar que o autor já recebeu BPC/LOAS no passado, mas "
        "agora pleiteia aposentadoria por incapacidade permanente..."
    )
    assert infer_piece_type_id(texto) == "aposentadoria-incapacidade-permanente"


def test_inferencia_admin_inss_vence_bpc_judicial() -> None:
    texto = (
        "AO INSTITUTO NACIONAL DO SEGURO SOCIAL\n\n"
        "REQUERIMENTO DE BPC/LOAS - pessoa idosa de 67 anos..."
    )
    assert infer_piece_type_id(texto) == "requerimento-bpc-idoso"


def test_inferencia_recurso_inominado_com_aposentadoria_no_corpo() -> None:
    texto = (
        "EXCELENTÍSSIMO SENHOR DOUTOR JUIZ FEDERAL\n\n"
        "RECURSO INOMINADO\n\n"
        "Trata-se de recurso em face da sentença que indeferiu aposentadoria "
        "por idade rural ao recorrente. A sentença merece reforma..."
    )
    assert infer_piece_type_id(texto) == "recurso-inominado"


def test_inferencia_consistente_com_catalogo() -> None:
    catalog_ids = {item.id for item in list_piece_types()}
    samples = [
        "PROCURAÇÃO AD JUDICIA",
        "EXCELENTÍSSIMO\n\nrecurso inominado",
        "EXCELENTÍSSIMO\n\naposentadoria especial PPP LTCAT",
    ]
    for texto in samples:
        detected = infer_piece_type_id(texto)
        if detected is not None:
            assert detected in catalog_ids
            assert get_piece_type(detected) is not None

from src.core.validation.modes import normalize_mode, validar_modo_saida
from src.core.validation.docx import validar_texto_protocolavel
from tests.test_docx_validation import TEXTO_VALIDO


def test_normalize_mode_usa_minuta_por_padrao():
    assert normalize_mode(None) == "minuta"
    assert normalize_mode("") == "minuta"
    assert normalize_mode("modo-inexistente") == "minuta"


def test_modo_final_bloqueia_dado_faltante():
    texto = TEXTO_VALIDO + "\nDIB: [DADO FALTANTE: confirmar com cliente]"

    problemas = validar_modo_saida(texto, "final")

    assert any("modo 'final'" in problema for problema in problemas)


def test_modo_final_bloqueia_marca_de_ia():
    texto = TEXTO_VALIDO.replace("I - DOS FATOS", "I - DOS FATOS\nClaude: revisar este parágrafo")

    problemas = validar_modo_saida(texto, "final")

    assert any("marca de IA" in problema for problema in problemas)


def test_modo_final_bloqueia_instrucao_interna():
    texto = TEXTO_VALIDO + "\nInserir aqui os documentos médicos."

    problemas = validar_modo_saida(texto, "final")

    assert any("instrução interna" in problema for problema in problemas)


def test_modo_minuta_aceita_dado_faltante():
    texto = TEXTO_VALIDO + "\nDIB: [DADO FALTANTE: confirmar]"

    assert validar_modo_saida(texto, "minuta") == []


def test_validacao_textual_permite_marcador_pendente_em_minuta():
    texto = TEXTO_VALIDO + "\nDIB: [DADO FALTANTE: confirmar]"

    problemas = validar_texto_protocolavel(
        texto,
        "judicial-inicial-jef",
        allow_pending_markers=True,
    )

    assert not any("placeholders" in problema for problema in problemas)


def test_modo_minuta_bloqueia_marca_de_ia():
    texto = TEXTO_VALIDO + "\nChatGPT: completar fundamentação."

    problemas = validar_modo_saida(texto, "minuta")

    assert any("marca de IA" in problema for problema in problemas)


def test_modo_triagem_nao_bloqueia_marcadores():
    texto = "Caso incompleto. [DADO FALTANTE: DER]"

    assert validar_modo_saida(texto, "triagem") == []

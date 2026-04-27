"""Inferência determinística e declarativa de tipo de peça."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
import unicodedata


@dataclass(frozen=True)
class DetectionContext:
    primeira: str
    head_strict: str
    head_loose: str
    body: str


@dataclass(frozen=True)
class DetectionRule:
    piece_id: str
    matches: Callable[[DetectionContext], bool]


_HEAD_LINES_FOR_TITLE = 30
_MAX_TITLE_LINE_CHARS = 140
_MIN_UPPER_RATIO_FOR_TITLE = 0.7


def _normalize(value: str) -> str:
    nfkd = unicodedata.normalize("NFD", value)
    sem_acentos = "".join(c for c in nfkd if not unicodedata.combining(c))
    return sem_acentos.upper()


def _title_candidates(linhas: list[str]) -> list[str]:
    candidates: list[str] = []
    for linha in linhas[:_HEAD_LINES_FOR_TITLE]:
        s = linha.strip()
        if not s or len(s) > _MAX_TITLE_LINE_CHARS:
            continue
        letras = [c for c in s if c.isalpha()]
        if not letras:
            candidates.append(s)
            continue
        upper_ratio = sum(1 for c in letras if c.isupper()) / len(letras)
        if upper_ratio >= _MIN_UPPER_RATIO_FOR_TITLE:
            candidates.append(s)
    return candidates


def _contains(*terms: str) -> Callable[[str], bool]:
    return lambda value: all(term in value for term in terms)


def _any(*terms: str) -> Callable[[str], bool]:
    return lambda value: any(term in value for term in terms)


def _head(rule: Callable[[str], bool]) -> Callable[[DetectionContext], bool]:
    return lambda ctx: rule(ctx.head_strict) or rule(ctx.head_loose)


def _first_starts(*prefixes: str) -> Callable[[DetectionContext], bool]:
    return lambda ctx: ctx.primeira.startswith(prefixes)


def _body_any(*terms: str) -> Callable[[DetectionContext], bool]:
    return lambda ctx: any(term in ctx.body for term in terms)


INSTRUMENT_RULES: tuple[DetectionRule, ...] = (
    DetectionRule(
        "procuracao-ad-judicia-et-extra",
        lambda c: _first_starts("PROCURACAO", "INSTRUMENTO PARTICULAR DE PROCURACAO", "INSTRUMENTO PUBLICO DE PROCURACAO")(c)
        and _body_any("ad judicia et extra", "judicia et extra")(c),
    ),
    DetectionRule(
        "procuracao-administrativa-inss",
        lambda c: _first_starts("PROCURACAO", "INSTRUMENTO PARTICULAR DE PROCURACAO", "INSTRUMENTO PUBLICO DE PROCURACAO")(c)
        and _body_any("inss", "previdenciári", "previdenciari", "administrativ")(c),
    ),
    DetectionRule(
        "procuracao-ad-judicia",
        _first_starts("PROCURACAO", "INSTRUMENTO PARTICULAR DE PROCURACAO", "INSTRUMENTO PUBLICO DE PROCURACAO"),
    ),
    DetectionRule(
        "substabelecimento-sem-reserva",
        lambda c: _first_starts("SUBSTABELECIMENTO", "SUBSTABELECEMENTO")(c) and "sem reserva" in c.body,
    ),
    DetectionRule(
        "substabelecimento-com-reserva",
        _first_starts("SUBSTABELECIMENTO", "SUBSTABELECEMENTO"),
    ),
    DetectionRule(
        "declaracao-hipossuficiencia",
        lambda c: c.primeira.startswith("DECLARACAO") and "hipossufic" in c.body,
    ),
    DetectionRule(
        "declaracao-atividade-rural",
        lambda c: c.primeira.startswith("DECLARACAO") and _body_any("atividade rural", "rurícola", "ruricola")(c),
    ),
    DetectionRule(
        "declaracao-residencia",
        lambda c: c.primeira.startswith("DECLARACAO") and _body_any("residênci", "residenci", "resido ")(c),
    ),
)


ADMIN_RULES: tuple[DetectionRule, ...] = (
    DetectionRule("recurso-bpc", _head(lambda h: ("BPC" in h or "LOAS" in h) and "RECURSO" in h)),
    DetectionRule("requerimento-bpc-deficiencia", _head(lambda h: ("BPC" in h or "LOAS" in h) and "DEFICIENCIA" in h)),
    DetectionRule("requerimento-bpc-idoso", _head(_any("BPC", "LOAS"))),
    DetectionRule("ctc", _head(_any("CTC", "CERTIDAO DE TEMPO"))),
    DetectionRule("copia-processo-administrativo", _head(_any("COPIA INTEGRAL", "COPIA DO PROCESSO"))),
    DetectionRule("retificacao-cnis", _head(_contains("RETIFICACAO", "CNIS"))),
    DetectionRule("acerto-vinculos-remuneracoes", _head(_contains("ACERTO", "CNIS"))),
    DetectionRule("justificacao-administrativa", _head(_contains("JUSTIFICACAO ADMINISTRATIVA"))),
    DetectionRule("regularizacao-representante", _head(lambda h: "REGULARIZACAO" in h and ("REPRESENTANTE" in h or "PROCURADOR" in h))),
    DetectionRule("pedido-prioridade", _head(_contains("PRIORIDADE", "TRAMITACAO"))),
    DetectionRule("cumprimento-exigencia", _head(_contains("CUMPRIMENTO DE EXIGENCIA"))),
    DetectionRule("recurso-ordinario-crps", _head(_contains("RECURSO", "CRPS", "ORDINARIO"))),
    DetectionRule("recurso-especial-crps", _head(_contains("RECURSO", "CRPS", "ESPECIAL"))),
    DetectionRule("recurso-crps", _head(_contains("RECURSO", "CRPS"))),
    DetectionRule("pedido-reconsideracao-administrativa", _head(_contains("RECONSIDERACAO"))),
)


TITLE_RULES: tuple[DetectionRule, ...] = (
    DetectionRule("recurso-inominado", _head(_contains("RECURSO INOMINADO"))),
    DetectionRule("agravo-instrumento", _head(_contains("AGRAVO DE INSTRUMENTO"))),
    DetectionRule("agravo-interno", _head(_contains("AGRAVO INTERNO"))),
    DetectionRule("embargos-declaracao", _head(_contains("EMBARGOS DE DECLARACAO"))),
    DetectionRule("contrarrazoes", _head(_contains("CONTRARRAZOES"))),
    DetectionRule("apelacao-civel", _head(lambda h: "APELACAO" in h and ("CIVEL" in h or "RECURSO DE APELACAO" in h))),
    DetectionRule("pedilef-tnu", _head(lambda h: "PEDILEF" in h or ("UNIFORMIZACAO" in h and "TNU" in h))),
    DetectionRule("recurso-especial-stj", _head(lambda h: "RECURSO ESPECIAL" in h and ("STJ" in h or "TRIBUNAL SUPERIOR" in h))),
    DetectionRule("recurso-extraordinario-stf", _head(_contains("RECURSO EXTRAORDINARIO"))),
    DetectionRule("juizo-retratacao", _head(_contains("JUIZO DE RETRATACAO"))),
    DetectionRule("cumprimento-sentenca-rpv", _head(lambda h: ("CUMPRIMENTO DE SENTENCA" in h or "CUMPRIMENTO DA SENTENCA" in h) and ("RPV" in h or "REQUISICAO DE PEQUENO VALOR" in h))),
    DetectionRule("cumprimento-sentenca-precatorio", _head(lambda h: ("CUMPRIMENTO DE SENTENCA" in h or "CUMPRIMENTO DA SENTENCA" in h) and "PRECATORIO" in h)),
    DetectionRule("cumprimento-sentenca-astreintes", _head(lambda h: ("CUMPRIMENTO DE SENTENCA" in h or "CUMPRIMENTO DA SENTENCA" in h) and ("ASTREINTES" in h or "MULTA DIARIA" in h))),
    DetectionRule("cumprimento-sentenca-implantacao", _head(lambda h: "CUMPRIMENTO DE SENTENCA" in h or "CUMPRIMENTO DA SENTENCA" in h)),
    DetectionRule("impugnacao-cumprimento-sentenca", _head(_contains("IMPUGNACAO AO CUMPRIMENTO"))),
    DetectionRule("impugnacao-calculos", _head(_any("IMPUGNACAO AOS CALCULOS", "IMPUGNACAO DOS CALCULOS"))),
    DetectionRule("ms-bpc-mora", _head(lambda h: "MANDADO DE SEGURANCA" in h and ("BPC" in h or "LOAS" in h))),
    DetectionRule("mandado-seguranca-previdenciario", _head(_contains("MANDADO DE SEGURANCA"))),
    DetectionRule("inventario-extrajudicial", _head(_contains("INVENTARIO EXTRAJUDICIAL"))),
    DetectionRule("arrolamento-sumario", _head(_contains("ARROLAMENTO SUMARIO"))),
    DetectionRule("arrolamento-simples", _head(lambda h: "ARROLAMENTO" in h and "SIMPLES" in h)),
    DetectionRule("sobrepartilha-extrajudicial", _head(_contains("SOBREPARTILHA", "EXTRAJUDICIAL"))),
    DetectionRule("sobrepartilha-judicial", _head(_contains("SOBREPARTILHA"))),
    DetectionRule("usucapiao", _head(_contains("USUCAPIAO"))),
    DetectionRule("alvara-judicial", _head(lambda h: "ALVARA" in h and ("JUDICIAL" in h or "JUIZO" in h))),
    DetectionRule("cessao-direitos-hereditarios", _head(_contains("CESSAO DE DIREITOS HEREDITARIOS"))),
    DetectionRule("renuncia-heranca", _head(_any("RENUNCIA A HERANCA", "REPUDIO A HERANCA"))),
    DetectionRule("habilitacao-sucessoria-processo", _head(_contains("HABILITACAO SUCESSORIA"))),
    DetectionRule("habilitacao-herdeiros", _head(_contains("HABILITACAO", "HERDEIROS"))),
    DetectionRule("primeiras-declaracoes", _head(_contains("PRIMEIRAS DECLARACOES"))),
    DetectionRule("ultimas-declaracoes", _head(_contains("ULTIMAS DECLARACOES"))),
    DetectionRule("formal-partilha", _head(_any("FORMAL DE PARTILHA", "CARTA DE ADJUDICACAO"))),
    DetectionRule("inventario-judicial", _head(lambda h: "INVENTARIO JUDICIAL" in h or ("INVENTARIO" in h and ("JUIZO" in h or "VARA" in h)) or "INVENTARIO" in h)),
    DetectionRule("impugnacao-laudo-pericial", _head(_contains("IMPUGNACAO AO LAUDO"))),
    DetectionRule("quesitos-periciais", _head(_any("QUESITOS PERICIAIS", "APRESENTACAO DE QUESITOS"))),
    DetectionRule("especificacao-provas", _head(_contains("ESPECIFICACAO DE PROVAS"))),
    DetectionRule("replica-contestacao", _head(lambda h: "REPLICA" in h or "IMPUGNACAO A CONTESTACAO" in h)),
    DetectionRule("manifestacao-documentos", _head(_contains("MANIFESTACAO SOBRE DOCUMENTOS"))),
    DetectionRule("juntada-documentos", _head(_contains("JUNTADA DE DOCUMENTOS"))),
    DetectionRule("tutela-urgencia-incidental", _head(lambda h: ("TUTELA DE URGENCIA" in h or "TUTELA ANTECIPADA" in h) and "PETICAO INICIAL" not in h and "ACAO" not in h)),
    DetectionRule("aposentadoria-especial", _head(_contains("APOSENTADORIA ESPECIAL"))),
    DetectionRule("aposentadoria-idade-rural", _head(lambda h: "APOSENTADORIA POR IDADE RURAL" in h or ("APOSENTADORIA" in h and ("RURAL" in h or "RURICOLA" in h or "TRABALHADOR RURAL" in h)))),
    DetectionRule("aposentadoria-hibrida", _head(_contains("APOSENTADORIA HIBRIDA"))),
    DetectionRule("aposentadoria-pcd-tempo", _head(lambda h: "APOSENTADORIA" in h and "TEMPO DE CONTRIBUICAO" in h and ("DEFICIENCIA" in h or "PCD" in h))),
    DetectionRule("aposentadoria-tempo-contribuicao", _head(lambda h: "APOSENTADORIA" in h and "TEMPO DE CONTRIBUICAO" in h)),
    DetectionRule("aposentadoria-pcd-idade", _head(lambda h: "APOSENTADORIA" in h and "POR IDADE" in h and ("DEFICIENCIA" in h or "PCD" in h))),
    DetectionRule("aposentadoria-idade-urbana", _head(lambda h: "APOSENTADORIA" in h and "POR IDADE" in h)),
    DetectionRule("aposentadoria-invalidez-acidentaria", _head(_any("APOSENTADORIA POR INVALIDEZ ACIDENTARIA", "B-92", "B92"))),
    DetectionRule("aposentadoria-incapacidade-permanente", _head(_any("APOSENTADORIA POR INCAPACIDADE PERMANENTE", "APOSENTADORIA POR INVALIDEZ"))),
    DetectionRule("revisao-aposentadoria", _head(lambda h: "REVISAO DE APOSENTADORIA" in h or ("APOSENTADORIA" in h and "REVISAO" in h))),
    DetectionRule("revisao-auxilio-acidente", _head(lambda h: ("AUXILIO-ACIDENTE" in h or "AUXILIO ACIDENTE" in h or "B-36" in h or "B36" in h) and "REVISAO" in h)),
    DetectionRule("auxilio-acidente", _head(_any("AUXILIO-ACIDENTE", "AUXILIO ACIDENTE", "B-36", "B36"))),
    DetectionRule("revisao-auxilio-incapacidade-temporaria", _head(lambda h: ("AUXILIO-DOENCA" in h or "AUXILIO DOENCA" in h or "AUXILIO POR INCAPACIDADE TEMPORARIA" in h or "INCAPACIDADE TEMPORARIA" in h) and "REVISAO" in h)),
    DetectionRule("restabelecimento-beneficio-incapacidade", _head(lambda h: ("AUXILIO-DOENCA" in h or "AUXILIO DOENCA" in h or "AUXILIO POR INCAPACIDADE TEMPORARIA" in h or "INCAPACIDADE TEMPORARIA" in h) and "RESTABELEC" in h)),
    DetectionRule("auxilio-incapacidade-temporaria", _head(_any("AUXILIO-DOENCA", "AUXILIO DOENCA", "AUXILIO POR INCAPACIDADE TEMPORARIA", "INCAPACIDADE TEMPORARIA"))),
    DetectionRule("auxilio-reclusao", _head(_any("AUXILIO-RECLUSAO", "AUXILIO RECLUSAO"))),
    DetectionRule("revisao-pensao-por-morte", _head(lambda h: "PENSAO POR MORTE" in h and "REVISAO" in h)),
    DetectionRule("pensao-por-morte", _head(_contains("PENSAO POR MORTE"))),
    DetectionRule("salario-maternidade", _head(_any("SALARIO-MATERNIDADE", "SALARIO MATERNIDADE"))),
    DetectionRule("reconhecimento-tempo-contribuicao", _head(_contains("RECONHECIMENTO", "TEMPO DE CONTRIBUICAO"))),
    DetectionRule("reconhecimento-atividade-especial", _head(_contains("RECONHECIMENTO", "ATIVIDADE ESPECIAL"))),
    DetectionRule("bpc-revisao-restabelecimento", _head(lambda h: ("BPC" in h or "LOAS" in h) and ("REVISAO" in h or "RESTABELEC" in h))),
    DetectionRule("bpc-deficiencia-judicial", _head(lambda h: ("BPC" in h or "LOAS" in h) and "DEFICIENCIA" in h)),
    DetectionRule("bpc-idoso-judicial", _head(lambda h: ("BPC" in h or "LOAS" in h) and ("IDOSO" in h or "65 ANOS" in h))),
)


def _first_match(rules: tuple[DetectionRule, ...], ctx: DetectionContext) -> str | None:
    for rule in rules:
        if rule.matches(ctx):
            return rule.piece_id
    return None


def _strict_context(ctx: DetectionContext) -> DetectionContext:
    return DetectionContext(
        primeira=ctx.primeira,
        head_strict=ctx.head_strict,
        head_loose="",
        body=ctx.body,
    )


def _loose_context(ctx: DetectionContext) -> DetectionContext:
    return DetectionContext(
        primeira=ctx.primeira,
        head_strict="",
        head_loose=ctx.head_loose,
        body=ctx.body,
    )


def infer_piece_type_id(texto: str) -> str | None:
    if not texto or not texto.strip():
        return None

    linhas = [linha.strip() for linha in texto.splitlines() if linha.strip()]
    if not linhas:
        return None

    ctx = DetectionContext(
        primeira=_normalize(linhas[0]),
        head_strict=_normalize("\n".join(_title_candidates(linhas))),
        head_loose=_normalize("\n".join(linhas[:10])),
        body=texto.lower(),
    )

    detected = _first_match(INSTRUMENT_RULES, ctx)
    if detected:
        return detected
    if ctx.primeira.startswith("DECLARACAO"):
        return None

    is_admin = ctx.primeira.startswith((
        "AO INSTITUTO",
        "AO INSS",
        "AO CRPS",
        "A AGENCIA",
        "AGENCIA",
        "A GERENCIA",
        "AO PRESIDENTE DO INSS",
    ))
    if is_admin:
        return (
            _first_match(ADMIN_RULES, _strict_context(ctx))
            or _first_match(ADMIN_RULES, _loose_context(ctx))
            or "requerimento-inss-geral"
        )

    detected = _first_match(TITLE_RULES, _strict_context(ctx)) or _first_match(
        TITLE_RULES,
        _loose_context(ctx),
    )
    if detected:
        return detected

    if ctx.primeira.startswith(("EXCELENT", "AO JUIZO", "MERITISSIMO")):
        return "peticao-simples"
    return None

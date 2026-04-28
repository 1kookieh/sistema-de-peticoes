"""Extração de texto para uploads locais permitidos pela API."""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
import re
import os

from docx import Document
from PIL import Image
from pypdf import PdfReader


MAX_UPLOAD_BYTES = 25 * 1024 * 1024
MAX_TOTAL_UPLOAD_BYTES = 200 * 1024 * 1024
MAX_UPLOAD_FILES = 20
ALLOWED_UPLOAD_SUFFIXES = {".txt", ".md", ".docx", ".pdf", ".png", ".jpg", ".jpeg", ".webp"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
HEADER_LINE_RE = re.compile(r"^\s*(EXCELENT[ÍI]SSIMO|AO\s+TABELIONATO|AO\s+INSTITUTO)", re.IGNORECASE)
PIECE_TITLE_RE = re.compile(
    r"^\s*(A[CÇ][AÃ]O|PETI[CÇ][AÃ]O|RECURSO|MANDADO|CUMPRIMENTO|IMPUGNA[CÇ][AÃ]O|"
    r"CONTRARRAZ[ÕO]ES|EMBARGOS|REQUERIMENTO|AGRAVO|APELA[CÇ][AÃ]O|ALVAR[ÁA]|"
    r"INVENT[ÁA]RIO)\b",
    re.IGNORECASE,
)
SECTION_LINE_RE = re.compile(r"^\s*(?:[IVXLCDM]+)\s*[-–—]\s+", re.IGNORECASE)
LOCAL_DATE_RE = re.compile(
    r"^[A-ZÁÀÂÃÉÈÊÍÓÔÕÚÇ][\wÁÀÂÃÉÈÊÍÓÔÕÚÇáàâãéèêíóôõúç\s./-]+,\s*\d{1,2}\s+de\s+",
    re.IGNORECASE,
)
OAB_RE = re.compile(r"^\s*OAB\s*/?\s*[A-Z]{2}\s+\d", re.IGNORECASE)
TESSERACT_WINDOWS_PATH = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
LOCAL_TESSDATA_DIR = Path(os.environ.get("LOCALAPPDATA", "")) / "Tesseract-OCR" / "tessdata"


class FileExtractionError(ValueError):
    """Erro ao extrair texto de arquivo enviado pelo usuário."""


def _decode_text(data: bytes) -> str:
    """Decodifica texto exigindo UTF-8 (com ou sem BOM).

    O fallback para Latin-1/CP1252 foi removido porque aceitava silenciosamente
    qualquer sequência de bytes e produzia mojibake no DOCX final. Quem precisa
    enviar arquivo em outra codificação deve converter antes do upload.
    """
    for encoding in ("utf-8-sig", "utf-8"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise FileExtractionError(
        "arquivo de texto não está em UTF-8. Converta antes do upload "
        "(ex.: salvar como UTF-8 no editor) para evitar caracteres corrompidos."
    )


def _extract_docx(data: bytes) -> str:
    document = Document(BytesIO(data))
    paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs]
    return "\n\n".join(paragraph for paragraph in paragraphs if paragraph)


def _extract_pdf(data: bytes) -> str:
    reader = PdfReader(BytesIO(data))
    pages = [(page.extract_text() or "").strip() for page in reader.pages]
    return "\n\n".join(page for page in pages if page)


def _extract_image(data: bytes) -> str:
    try:
        import pytesseract
    except ImportError as exc:
        raise FileExtractionError("OCR de imagem não está instalado") from exc

    try:
        if TESSERACT_WINDOWS_PATH.exists():
            pytesseract.pytesseract.tesseract_cmd = str(TESSERACT_WINDOWS_PATH)
        config = f'--tessdata-dir "{LOCAL_TESSDATA_DIR}"' if (LOCAL_TESSDATA_DIR / "por.traineddata").exists() else ""
        image = Image.open(BytesIO(data))
        try:
            text = pytesseract.image_to_string(image, lang="por", config=config)
        except pytesseract.TesseractError:
            text = pytesseract.image_to_string(image, lang="eng")
    except pytesseract.TesseractNotFoundError as exc:
        raise FileExtractionError(
            "OCR não configurado. Instale o Tesseract OCR e deixe o executável no PATH."
        ) from exc
    except Exception as exc:
        raise FileExtractionError("não foi possível extrair texto da imagem") from exc
    return text


def _normalize_extracted_legal_text(text: str) -> str:
    """Reconstroi separacoes basicas perdidas por OCR/PDF antes da formatacao."""
    raw_lines = [line.strip() for line in text.replace("\r\n", "\n").replace("\r", "\n").splitlines()]
    lines = [line for line in raw_lines if line]
    if not lines:
        return ""

    normalized: list[str] = []
    header_mode = False
    for index, line in enumerate(lines):
        previous = lines[index - 1] if index else ""
        is_first_line = index == 0
        starts_new_block = (
            not is_first_line
            and (
                HEADER_LINE_RE.match(line)
                or PIECE_TITLE_RE.match(line)
                or SECTION_LINE_RE.match(line)
                or LOCAL_DATE_RE.match(line)
                or OAB_RE.match(line)
                or PIECE_TITLE_RE.match(previous)
                or line.lower().startswith("termos em que")
            )
        )

        if HEADER_LINE_RE.match(line):
            header_mode = True
        elif header_mode and (
            PIECE_TITLE_RE.match(line)
            or SECTION_LINE_RE.match(line)
            or line.lower().startswith(("joao ", "joão ", "maria ", "autor ", "requerente "))
        ):
            starts_new_block = True
            header_mode = False

        if starts_new_block and normalized and normalized[-1] != "":
            normalized.append("")

        normalized.append(line)

        if LOCAL_DATE_RE.match(line) and previous.lower().startswith("termos em que"):
            normalized.append("")

    return "\n".join(normalized)


def extract_text_from_upload(filename: str, data: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_UPLOAD_SUFFIXES:
        allowed = ", ".join(sorted(ALLOWED_UPLOAD_SUFFIXES))
        raise FileExtractionError(f"formato não suportado. Use: {allowed}")
    if len(data) > MAX_UPLOAD_BYTES:
        raise FileExtractionError(f"arquivo excede {MAX_UPLOAD_BYTES} bytes")

    try:
        if suffix in {".txt", ".md"}:
            text = _decode_text(data)
        elif suffix == ".docx":
            text = _extract_docx(data)
        elif suffix == ".pdf":
            text = _normalize_extracted_legal_text(_extract_pdf(data))
        else:
            text = _normalize_extracted_legal_text(_extract_image(data))
    except FileExtractionError:
        raise
    except Exception as exc:
        raise FileExtractionError("não foi possível extrair texto do arquivo") from exc

    text = text.strip()
    if not text:
        raise FileExtractionError("arquivo não contém texto extraível")
    return text


def extract_text_from_uploads(files: list[tuple[str, bytes]]) -> str:
    if len(files) > MAX_UPLOAD_FILES:
        raise FileExtractionError(
            f"limite de {MAX_UPLOAD_FILES} arquivos por requisição excedido"
        )
    total_bytes = sum(len(data) for _, data in files)
    if total_bytes > MAX_TOTAL_UPLOAD_BYTES:
        raise FileExtractionError(
            f"soma dos arquivos excede {MAX_TOTAL_UPLOAD_BYTES} bytes"
        )
    extracted: list[str] = []
    for filename, data in files:
        extracted.append(extract_text_from_upload(filename, data))
    return "\n\n".join(extracted).strip()


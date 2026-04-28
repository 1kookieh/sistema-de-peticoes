"""Convert structured LLM drafts into the plain petition text renderer input."""
from __future__ import annotations

from src.infra.llm.schemas import LegalDocumentDraft, LegalDocumentSection


def draft_to_petition_text(draft: LegalDocumentDraft) -> str:
    """Render a validated structured draft into the existing DOCX text pipeline."""
    blocks: list[str] = []
    if draft.court_addressing:
        blocks.append(draft.court_addressing.strip())

    blocks.append(draft.title.strip().upper())

    if draft.qualification:
        blocks.extend(_clean_many(draft.qualification))

    if draft.facts_summary:
        blocks.append(_section("DOS FATOS", draft.facts_summary))

    for section in draft.legal_grounds:
        blocks.append(_render_section(section))

    for section in draft.sections:
        blocks.append(_render_section(section))

    if draft.requests:
        requests = [f"{chr(97 + idx)}) {item}" for idx, item in enumerate(_clean_many(draft.requests))]
        blocks.append(_section("DOS PEDIDOS", requests))

    if draft.evidence:
        blocks.append(_section("DAS PROVAS", _clean_many(draft.evidence)))

    if draft.closing:
        blocks.extend(_clean_many(draft.closing))
    else:
        blocks.append("Termos em que, pede deferimento.")

    return "\n\n".join(block for block in blocks if block.strip()).strip()


def _render_section(section: LegalDocumentSection) -> str:
    lines: list[str] = [section.title.strip().upper()]
    lines.extend(_clean_many(section.paragraphs))
    lines.extend(f"- {item}" for item in _clean_many(section.bullets))
    lines.extend(f"{idx}. {item}" for idx, item in enumerate(_clean_many(section.numbered_items), start=1))
    return "\n\n".join(lines)


def _section(title: str, paragraphs: list[str]) -> str:
    return "\n\n".join([title, *_clean_many(paragraphs)])


def _clean_many(values: list[str]) -> list[str]:
    return [value.strip() for value in values if value and value.strip()]

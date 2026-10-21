"""División de documentos en fragmentos con metadatos."""
from __future__ import annotations

import hashlib
import re

from src.config import CHUNK_MAX_CHARS, CHUNK_OVERLAP_CHARS

HEADING_RE = re.compile(r"^(#{1,4})\s+(.*)$")


def _split_long_block(block: str, max_chars: int) -> list[str]:
    """Parte un bloque demasiado largo por oraciones; si no hay, por longitud."""
    if len(block) <= max_chars:
        return [block]
    sentences = re.split(r"(?<=[.!?;:])\s+", block)
    parts: list[str] = []
    current = ""
    for s in sentences:
        while len(s) > max_chars:  # oración sin cortes: se parte a la fuerza
            if current:
                parts.append(current)
                current = ""
            parts.append(s[:max_chars])
            s = s[max_chars:]
        if current and len(current) + 1 + len(s) > max_chars:
            parts.append(current)
            current = s
        else:
            current = f"{current} {s}".strip()
    if current:
        parts.append(current)
    return parts


def chunk_text(
    text: str,
    max_chars: int = CHUNK_MAX_CHARS,
    overlap: int = CHUNK_OVERLAP_CHARS,
) -> list[dict]:
    """Divide `text` en fragmentos de hasta `max_chars` caracteres.

    - Respeta párrafos (separados por línea en blanco).
    - Recuerda el último encabezado ('# Título') y lo guarda en cada fragmento.
    - Un fragmento nuevo repite el final del anterior (`overlap`) para no perder contexto.

    Devuelve una lista de {"text", "heading"}.
    """
    blocks: list[tuple[str, str]] = []  # (texto, encabezado vigente)
    heading = ""
    for raw in re.split(r"\n\s*\n", text):
        raw = raw.strip()
        if not raw:
            continue
        m = HEADING_RE.match(raw.splitlines()[0])
        if m and len(raw.splitlines()) == 1:
            heading = m.group(2).strip()
            blocks.append((raw, heading))
            continue
        for piece in _split_long_block(raw, max_chars):
            blocks.append((piece, heading))

    chunks: list[dict] = []
    current = ""
    current_heading = ""
    for block, h in blocks:
        if current and len(current) + 2 + len(block) > max_chars:
            chunks.append({"text": current, "heading": current_heading})
            tail = current[-overlap:] if overlap else ""
            # Empieza el siguiente fragmento en un límite de palabra.
            tail = tail[tail.find(" ") + 1:] if " " in tail else tail
            current = f"{tail}\n\n{block}".strip() if tail else block
            current_heading = h
        else:
            current = f"{current}\n\n{block}" if current else block
            current_heading = current_heading or h
    if current.strip():
        chunks.append({"text": current, "heading": current_heading})
    return chunks


def chunk_document(doc: dict) -> list[dict]:
    """Convierte un documento extraído en fragmentos listos para indexar."""
    out: list[dict] = []
    for page in doc["pages"]:
        for i, c in enumerate(chunk_text(page["text"])):
            page_tag = f"p{page['page']}" if page["page"] else "web"
            digest = hashlib.sha1(c["text"].encode("utf-8")).hexdigest()[:10]
            out.append(
                {
                    "chunk_id": f"{doc['source_id']}-{page_tag}-{i:03d}",
                    "source_id": doc["source_id"],
                    "url": doc["url"],
                    "title": doc["title"],
                    "type": doc.get("type"),
                    "published": doc.get("published"),
                    "school_cycle": doc.get("school_cycle"),
                    "faculty": doc.get("faculty"),
                    "status": doc.get("status"),
                    "page": page["page"],
                    "heading": c["heading"],
                    "text": c["text"],
                    "content_hash": digest,
                }
            )
    return out

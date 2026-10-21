"""Extracción de texto de PDFs y páginas HTML.

Ambas funciones devuelven una lista de "páginas": {"page": int | None, "text": str}.
Para HTML hay una sola entrada con page=None.
"""
from __future__ import annotations

import re
from pathlib import Path

from bs4 import BeautifulSoup

from src.config import MIN_CHARS_PER_PDF_PAGE


def clean_text(text: str) -> str:
    """Normaliza espacios y saltos de línea sin perder la separación por párrafos."""
    text = text.replace("\u00a0", " ").replace("\r", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pdf(path: Path) -> tuple[list[dict], list[int]]:
    """Extrae texto página por página con PyMuPDF.

    Devuelve (páginas, páginas_que_parecen_escaneadas). Las escaneadas
    necesitarán OCR en una etapa posterior.
    """
    import fitz  # PyMuPDF; se importa aquí para no exigirlo si solo se procesa HTML

    pages: list[dict] = []
    needs_ocr: list[int] = []
    with fitz.open(path) as pdf:
        for i, page in enumerate(pdf, start=1):
            text = clean_text(page.get_text("text"))
            if len(text) < MIN_CHARS_PER_PDF_PAGE:
                needs_ocr.append(i)
            pages.append({"page": i, "text": text})
    return pages, needs_ocr


def extract_html(path: Path) -> tuple[str, list[dict]]:
    """Extrae título y texto principal de una página HTML.

    Los encabezados se marcan con '#' para que el chunking los use como contexto.
    """
    soup = BeautifulSoup(path.read_bytes(), "html.parser")

    title = soup.title.get_text(strip=True) if soup.title else ""

    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "form"]):
        tag.decompose()

    root = soup.find("main") or soup.body or soup

    for level in range(1, 5):
        for h in root.find_all(f"h{level}"):
            h.replace_with(f"\n\n{'#' * level} {h.get_text(' ', strip=True)}\n\n")

    # Evita que párrafos, elementos de lista y filas de tabla se peguen entre sí.
    for tag in root.find_all(["p", "li", "tr", "br"]):
        tag.append("\n")

    text = clean_text(root.get_text())
    return title, [{"page": None, "text": text}]

"""Rutas y ajustes compartidos."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
DOCUMENTS_DIR = PROCESSED_DIR / "documents"
CHUNKS_FILE = PROCESSED_DIR / "chunks.jsonl"
MANIFEST_FILE = PROCESSED_DIR / "manifest.json"
SOURCES_FILE = DATA_DIR / "sources.yaml"

# Tamaño objetivo de cada fragmento, en caracteres (~600 tokens en español).
CHUNK_MAX_CHARS = 2500
CHUNK_OVERLAP_CHARS = 250

# Una página de PDF con menos caracteres que esto probablemente es un escaneo
# y necesitará OCR.
MIN_CHARS_PER_PDF_PAGE = 40

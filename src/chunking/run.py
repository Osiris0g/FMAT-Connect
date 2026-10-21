"""Genera data/processed/chunks.jsonl a partir de los documentos extraídos.

Uso:  python -m src.chunking.run
"""
from __future__ import annotations

import json

from src import config
from src.chunking.chunk import chunk_document


def main() -> None:
    files = sorted(config.DOCUMENTS_DIR.glob("*.json"))
    if not files:
        print("No hay documentos en data/processed/documents/. Corre primero: python -m src.ingest.run")
        return

    total = 0
    with config.CHUNKS_FILE.open("w", encoding="utf-8") as out:
        for f in files:
            doc = json.loads(f.read_text(encoding="utf-8"))
            chunks = chunk_document(doc)
            for c in chunks:
                out.write(json.dumps(c, ensure_ascii=False) + "\n")
            sizes = [len(c["text"]) for c in chunks]
            prom = sum(sizes) // len(sizes) if sizes else 0
            print(f"[+] {doc['source_id']}: {len(chunks)} fragmentos (promedio {prom} caracteres)")
            total += len(chunks)

    print(f"\nTotal: {total} fragmentos -> {config.CHUNKS_FILE}")


if __name__ == "__main__":
    main()

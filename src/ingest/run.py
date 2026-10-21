"""Descarga las fuentes de data/sources.yaml y extrae su texto.

Uso:  python -m src.ingest.run [--force]

Salida: data/processed/documents/<id>.json y data/processed/manifest.json
Si el contenido de una fuente no cambió (mismo hash), se omite el reprocesado.
"""
from __future__ import annotations

import argparse
import json
import time

import yaml

from src import config
from src.ingest.extract import extract_html, extract_pdf
from src.ingest.fetch import fetch


def load_sources() -> tuple[dict, list[dict]]:
    data = yaml.safe_load(config.SOURCES_FILE.read_text(encoding="utf-8"))
    return data.get("defaults", {}), data.get("sources", [])


def load_manifest() -> dict:
    if config.MANIFEST_FILE.exists():
        return json.loads(config.MANIFEST_FILE.read_text(encoding="utf-8"))
    return {}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="reprocesar aunque el hash no haya cambiado")
    args = parser.parse_args()

    defaults, sources = load_sources()
    user_agent = defaults.get("user_agent", "ChatBotUADY/0.1")
    delay = float(defaults.get("delay_seconds", 2.0))
    timeout = int(defaults.get("timeout_seconds", 30))

    config.DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest()
    summary = {"nuevos": 0, "sin_cambios": 0, "errores": 0}

    for n, src in enumerate(sources):
        sid = src["id"]
        if n > 0:
            time.sleep(delay)  # cortesía con el servidor

        try:
            info = fetch(src["url"], sid, config.RAW_DIR, user_agent, timeout)
        except Exception as exc:  # una fuente caída no debe frenar las demás
            print(f"[ERROR] {sid}: {exc}")
            summary["errores"] += 1
            continue

        if not args.force and manifest.get(sid, {}).get("sha256") == info["sha256"]:
            print(f"[=] {sid}: sin cambios")
            summary["sin_cambios"] += 1
            continue

        needs_ocr: list[int] = []
        title = src.get("title", "")
        if info["kind"] == "pdf":
            pages, needs_ocr = extract_pdf(info["path"])
        else:
            html_title, pages = extract_html(info["path"])
            title = title or html_title

        doc = {
            "source_id": sid,
            "url": src["url"],
            "title": title,
            "type": src.get("type"),
            "published": str(src["published"]) if src.get("published") else None,
            "school_cycle": src.get("school_cycle"),
            "faculty": src.get("faculty"),
            "status": src.get("status"),
            "kind": info["kind"],
            "sha256": info["sha256"],
            "fetched_at": info["fetched_at"],
            "needs_ocr_pages": needs_ocr,
            "pages": pages,
        }
        (config.DOCUMENTS_DIR / f"{sid}.json").write_text(
            json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        manifest[sid] = {"sha256": info["sha256"], "fetched_at": info["fetched_at"]}

        total_chars = sum(len(p["text"]) for p in pages)
        aviso = f"  ⚠ posible OCR en páginas {needs_ocr}" if needs_ocr else ""
        print(f"[+] {sid}: {len(pages)} pág., {total_chars} caracteres{aviso}")
        summary["nuevos"] += 1

    config.MANIFEST_FILE.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nResumen: {summary}")


if __name__ == "__main__":
    main()

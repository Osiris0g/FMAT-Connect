"""Descarga de documentos originales."""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import requests


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(url: str, source_id: str, raw_dir: Path, user_agent: str, timeout: int = 30) -> dict:
    """Descarga `url`, la guarda en `raw_dir` y devuelve info del archivo.

    Devuelve: {"path", "kind" ("pdf" | "html"), "sha256", "fetched_at"}
    """
    resp = requests.get(url, headers={"User-Agent": user_agent}, timeout=timeout)
    resp.raise_for_status()

    content_type = resp.headers.get("Content-Type", "").lower()
    is_pdf = "pdf" in content_type or url.lower().split("?")[0].endswith(".pdf")
    kind = "pdf" if is_pdf else "html"

    raw_dir.mkdir(parents=True, exist_ok=True)
    path = raw_dir / f"{source_id}.{kind}"
    path.write_bytes(resp.content)

    return {
        "path": path,
        "kind": kind,
        "sha256": sha256_bytes(resp.content),
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }

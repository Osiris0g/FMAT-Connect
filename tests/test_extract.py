from pathlib import Path

from src.ingest.extract import clean_text, extract_html


def test_clean_text_colapsa_espacios_y_saltos():
    assert clean_text("a   b \n\n\n\n c\u00a0d") == "a b\n\nc d"


def test_extract_html_marca_encabezados_y_quita_menu(tmp_path: Path):
    html = """<html><head><title>Control Escolar</title></head><body>
      <nav>Inicio | Contacto</nav>
      <main><h1>Inscripciones</h1><p>Del 5 al 6 de enero.</p>
      <h2>Requisitos</h2><ul><li>Credencial</li><li>Comprobante</li></ul></main>
      <footer>Pie de página</footer></body></html>"""
    f = tmp_path / "p.html"
    f.write_text(html, encoding="utf-8")
    title, pages = extract_html(f)
    text = pages[0]["text"]
    assert title == "Control Escolar"
    assert "# Inscripciones" in text and "## Requisitos" in text
    assert "Del 5 al 6 de enero." in text
    assert "Inicio | Contacto" not in text and "Pie de página" not in text
    assert "Credencial\nComprobante" in text

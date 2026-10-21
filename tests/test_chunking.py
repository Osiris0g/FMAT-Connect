from src.chunking.chunk import chunk_document, chunk_text


def test_respeta_tamano_maximo():
    texto = "\n\n".join(f"Párrafo {i}. " + "palabra " * 60 for i in range(20))
    chunks = chunk_text(texto, max_chars=800, overlap=100)
    assert len(chunks) > 1
    # el solapamiento puede pasarse un poco del máximo, pero no mucho
    assert all(len(c["text"]) <= 800 + 100 + 10 for c in chunks)


def test_guarda_encabezado_vigente():
    texto = "# Inscripciones\n\nLas inscripciones son el 5 de enero.\n\n# Exámenes\n\nLos exámenes inician el 22 de mayo."
    chunks = chunk_text(texto, max_chars=60, overlap=0)
    headings = {c["heading"] for c in chunks}
    assert "Inscripciones" in headings
    assert "Exámenes" in headings


def test_bloque_enorme_sin_cortes_se_parte():
    texto = "a" * 5000
    chunks = chunk_text(texto, max_chars=1000, overlap=0)
    assert len(chunks) == 5


def test_no_pierde_texto():
    texto = "\n\n".join(f"dato-{i} " + "x" * 200 for i in range(30))
    chunks = chunk_text(texto, max_chars=700, overlap=0)
    unido = "\n\n".join(c["text"] for c in chunks)
    for i in range(30):
        assert f"dato-{i} " in unido


def test_chunk_document_agrega_metadatos():
    doc = {
        "source_id": "demo", "url": "https://x/y.pdf", "title": "Demo", "type": "calendario",
        "published": "2023-03-17", "school_cycle": "ene-jul 2023", "faculty": "matematicas",
        "status": "historico",
        "pages": [{"page": 1, "text": "Inscripciones: 6 de enero."}, {"page": 2, "text": "Exámenes ordinarios en mayo."}],
    }
    chunks = chunk_document(doc)
    assert [c["page"] for c in chunks] == [1, 2]
    assert chunks[0]["chunk_id"] == "demo-p1-000"
    assert chunks[0]["url"] == "https://x/y.pdf"
    assert chunks[0]["published"] == "2023-03-17"

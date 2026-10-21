# ChatBot UADY

Asistente con IA que responde dudas de la **Facultad de Matemáticas de la UADY** (y que está pensado para crecer al resto de la universidad) usando únicamente **documentos y páginas oficiales**, y que siempre te lleva a la fuente original.

> **Estado:** en desarrollo temprano. Este README describe el diseño objetivo; las secciones marcadas con ☐ en la hoja de ruta aún no están implementadas.

## ¿Qué problema resuelve?

La información de la universidad existe, pero es difícil de encontrar:

- Está repartida en muchas páginas, algunas obsoletas o poco intuitivas.
- Datos clave (fechas de inscripción, requisitos, reglamentos) viven dentro de PDFs.
- Hay desinformación: respuestas en grupos y redes que no coinciden con lo oficial o están desactualizadas.

## ¿Qué hace?

Responde preguntas como:

- "¿Qué día es hoy?"
- "¿Cuándo son las inscripciones de la licenciatura X?"
- "¿Qué requisitos necesito para tal trámite?"

Y cada respuesta incluye:

- El **enlace al documento oficial** del que salió la información.
- La **fecha del documento**, para saber qué tan vigente es.
- Un aviso de **"no encontré esa información"** cuando los documentos no la respaldan, en lugar de inventar.

## ¿Cómo funciona?

Es un sistema **RAG** (*Retrieval-Augmented Generation*): el modelo no responde de memoria, sino a partir de fragmentos recuperados de los documentos oficiales.

```
Fuentes oficiales (web + PDFs)
        ↓
Ingesta: extracción de texto / OCR / limpieza
        ↓
Chunking + metadatos (URL, tipo, fecha, vigencia)
        ↓
Almacenamiento
  ├─ Base vectorial  → fragmentos de texto
  └─ Base estructurada → calendario y fechas
        ↓
Pregunta del usuario
        ↓
Router de intención
  ├─ fecha actual      → herramienta de fecha
  ├─ fechas oficiales  → consulta a la tabla de calendario
  └─ pregunta abierta  → búsqueda en documentos
        ↓
Recuperación híbrida (semántica + palabras clave) + filtro por vigencia
        ↓
LLM responde solo con ese contexto
        ↓
Respuesta + enlace oficial + fecha del documento
```

### Decisiones de diseño

- **Fechas en una tabla, no solo en texto.** Los periodos de inscripción y el calendario escolar se extraen a una base estructurada para consultarlos con exactitud.
- **Fecha actual como herramienta.** "¿Qué día es hoy?" nunca depende de los documentos.
- **Búsqueda híbrida.** Vectores para el significado y BM25 para nombres exactos de carreras o números de artículo.
- **Vigencia como metadato.** Cada fragmento guarda su fecha y el ciclo escolar al que aplica, para priorizar lo reciente y detectar contradicciones.
- **Respuestas con evidencia.** El prompt exige citar fuente y negarse a responder sin respaldo.

## Estructura del repositorio

```
chatbot-uady/
├── data/
│   ├── raw/             # PDFs y HTML originales descargados
│   ├── processed/       # texto limpio y fragmentos
│   └── sources.yaml     # lista de URLs y documentos oficiales
├── src/
│   ├── ingest/          # descarga, extracción de texto, OCR
│   ├── chunking/        # división en fragmentos y metadatos
│   ├── store/           # base vectorial y tabla de calendario
│   ├── retrieval/       # búsqueda híbrida y filtro de vigencia
│   ├── agent/           # router de intención, herramientas y prompt
│   └── app/             # interfaz (Streamlit al inicio)
├── eval/
│   └── questions.yaml   # preguntas reales con respuesta y fuente esperadas
├── scripts/
│   └── update_sources.py  # actualización periódica por hash de contenido
├── .env.example
├── requirements.txt
└── README.md
```

## Stack previsto

| Componente | Opción inicial |
|---|---|
| Lenguaje | Python 3.11+ |
| Extracción de PDFs | PyMuPDF / pdfplumber (+ Tesseract para escaneados) |
| Scraping | requests + BeautifulSoup |
| Base vectorial | Chroma |
| Datos estructurados | SQLite |
| LLM | Configurable (API de Claude o modelo local) |
| Interfaz | Streamlit (después FastAPI y/o bot de Telegram) |

## Instalación

```bash
git clone https://github.com/<tu-usuario>/chatbot-uady.git
cd chatbot-uady
python -m venv .venv
source .venv/bin/activate   # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # y completa tus credenciales
```

## Uso

> Los comandos finales dependerán de la implementación; este es el flujo planeado.

```bash
# 1. Descargar y procesar las fuentes listadas en data/sources.yaml
python -m src.ingest.run

# 2. Construir la base vectorial y la tabla de calendario
python -m src.store.build

# 3. Lanzar la interfaz
streamlit run src/app/main.py
```

## Evaluación

La calidad se mide con un conjunto de preguntas reales de estudiantes (`eval/questions.yaml`), cada una con su respuesta correcta y la fuente esperada. Cada cambio importante se corre contra este conjunto para saber si el sistema mejoró o empeoró.

## Hoja de ruta

- ☐ **Etapa 1:** reunir 15 a 20 fuentes clave de la Facultad de Matemáticas, ingesta y chunking.
- ☐ **Etapa 2:** base vectorial y RAG básico por consola, con citas.
- ☐ **Etapa 3:** tabla de calendario, herramienta de fecha y router de intención.
- ☐ **Etapa 4:** interfaz, set de evaluación y ajustes.
- ☐ **Después:** actualización automática semanal, bot de Telegram/WhatsApp, otras facultades de la UADY.

## Limitaciones y aviso

- Este proyecto **no es oficial** ni está afiliado a la UADY. Las respuestas pueden contener errores; ante cualquier trámite importante, **confirma siempre en el documento oficial enlazado** o directamente con la facultad.
- La calidad depende de la vigencia de las fuentes indexadas.
- Antes de hacer scraping, se revisan los términos de uso de los sitios consultados.

## Contribuir

Las ideas, fuentes oficiales faltantes y preguntas reales para la evaluación son bienvenidas. Abre un *issue* o un *pull request*.

## Licencia

Por definir.

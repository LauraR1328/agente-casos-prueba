"""
Redacta un plan de pruebas (caso, precondiciones, pasos y resultado esperado)
a partir de lo generado por src.generar_casos, y lo exporta a Word y CSV.

Uso (después de correr python -m src.generar_casos):
    python -m src.plan_pruebas

Genera en casos_generados/:
    plan_de_pruebas.docx   documento para revisión, una sección por historia
    plan_de_pruebas.csv    la misma información en tabla para Excel

Es un borrador: el tester debe revisar los resultados esperados antes de usarlos.
"""
import csv
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "casos_generados"
sys.path.insert(0, str(RAIZ / "src"))

import anthropic
from docx import Document
from docx.shared import Cm, Pt

from agente.config import MODELO
from agente.llm import texto_de_respuesta

COLUMNAS = ["ID", "Caso", "Precondiciones", "Pasos", "Resultado esperado"]

PROMPT = """Eres un analista de QA. Escribe un plan de pruebas para la historia de usuario.

Historia:
{historia}

Criterios de aceptación:
{criterios}

Casos planeados:
{casos}

Para CADA caso planeado escribe una fila con exactamente 5 campos separados por el carácter |:
ID | Caso | Precondiciones | Pasos | Resultado esperado

Reglas:
- ID con formato CP01, CP02, ... en el orden de los casos.
- Caso: una frase que resume qué se prueba.
- Precondiciones: estado inicial necesario (puede ser "Ninguna").
- Pasos: entre 2 y 5 pasos numerados separados por " ; " (ejemplo: 1. Crear una tarea con título "Prueba" ; 2. Revisar el estado).
- Resultado esperado: concreto y verificable, derivado de los criterios de aceptación.
- No uses encabezados, viñetas, markdown ni texto antes o después de las filas.
"""


def parsear_filas(texto: str) -> list[list[str]]:
    """Convierte las líneas 'ID | caso | ... | resultado' en listas de 5 campos."""
    filas = []
    for linea in texto.splitlines():
        partes = [p.strip() for p in linea.split("|")]
        if len(partes) == 5 and partes[0].upper().startswith("CP"):
            filas.append(partes)
    return filas


def redactar_plan(historia: str, criterios: str, casos: str, cliente) -> list[list[str]]:
    respuesta = cliente.messages.create(
        model=MODELO,
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": PROMPT.format(historia=historia, criterios=criterios, casos=casos),
        }],
    )
    return parsear_filas(texto_de_respuesta(respuesta))


def escribir_csv(ruta: Path, filas: list[list[str]]) -> None:
    # utf-8-sig para que Excel muestre bien las tildes
    with ruta.open("w", encoding="utf-8-sig", newline="") as f:
        escritor = csv.writer(f)
        escritor.writerow(["Historia"] + COLUMNAS)
        escritor.writerows(filas)


def construir_docx(secciones: list[tuple[str, str, list[list[str]]]], ruta: Path) -> None:
    doc = Document()

    for seccion in doc.sections:
        seccion.left_margin = seccion.right_margin = Cm(2.5)
        seccion.top_margin = seccion.bottom_margin = Cm(2.5)

    for nombre in ["Normal", "Heading 1", "Heading 2", "Title"]:
        doc.styles[nombre].font.name = "Arial"
    doc.styles["Normal"].font.size = Pt(12)

    doc.add_heading("Plan de pruebas: gestor de tareas", level=1)
    doc.add_paragraph(
        "Borrador generado por el agente a partir de las historias de usuario. "
        "Los resultados esperados deben ser revisados por el tester antes de su uso."
    )

    for hu_id, historia, filas in secciones:
        doc.add_heading(hu_id, level=2)
        doc.add_paragraph(historia)
        tabla = doc.add_table(rows=1, cols=len(COLUMNAS))
        tabla.style = "Table Grid"
        for celda, titulo in zip(tabla.rows[0].cells, COLUMNAS):
            celda.text = ""
            celda.paragraphs[0].add_run(titulo).bold = True
        for fila in filas:
            celdas = tabla.add_row().cells
            for celda, valor in zip(celdas, fila):
                celda.text = valor
        for fila in tabla.rows:
            for celda in fila.cells:
                for parrafo in celda.paragraphs:
                    for run in parrafo.runs:
                        run.font.size = Pt(10)
        doc.add_paragraph()

    doc.save(ruta)


def main():
    cliente = anthropic.Anthropic()  # toma ANTHROPIC_API_KEY del entorno (.env)
    carpetas = sorted(p for p in SALIDA.glob("HU-*") if p.is_dir())
    if not carpetas:
        print("No hay casos generados. Corre primero: python -m src.generar_casos")
        sys.exit(1)

    secciones, todas_las_filas = [], []
    for carpeta in carpetas:
        hu_id = carpeta.name
        historia = (RAIZ / "historias" / f"{hu_id}.txt").read_text(encoding="utf-8").strip()
        criterios = (carpeta / "criterios.txt").read_text(encoding="utf-8")
        casos = (carpeta / "plan_casos.txt").read_text(encoding="utf-8")
        print(f"Redactando plan de pruebas para {hu_id}...")
        filas = redactar_plan(historia, criterios, casos, cliente)
        print(f"  {len(filas)} casos con pasos y resultado esperado")
        secciones.append((hu_id, historia, filas))
        todas_las_filas.extend([[hu_id] + fila for fila in filas])

    escribir_csv(SALIDA / "plan_de_pruebas.csv", todas_las_filas)
    construir_docx(secciones, SALIDA / "plan_de_pruebas.docx")
    print(f"\nListo: {SALIDA / 'plan_de_pruebas.docx'}")


if __name__ == "__main__":
    main()

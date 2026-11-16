"""
Genera el documento de la Entrega 2 (prototipo parcial y avance de resultados).
Parte de la Entrega 1 y del anteproyecto, y aplica las observaciones del asesor.

Uso (desde la carpeta agente):
    python -m src.documento_entrega2

Lee resultados\\comparacion.json y casos_generados\\resumen_general.csv
(plan_de_pruebas.csv es opcional). Escribe entrega2\\Entrega2_Trabajo_de_grado.docx.
"""
import csv
import json
from datetime import date, timedelta
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

RAIZ = Path(__file__).resolve().parents[1]
SALIDA_DIR = RAIZ / "entrega2"

AUTORA = "Laura Natalia Ruiz Jiménez"
CODIGO = "100322881"
ASESOR = "Wilson Eduardo Soto Forero"
META_PUNTOS = 15.0

# Fechas límite del programa.
FECHA_ANTEPROYECTO = date(2026, 9, 20)
FECHA_E1 = date(2026, 10, 24)
FECHA_E2 = date(2026, 11, 16)
FECHA_FINAL = date(2026, 12, 12)

# Semana 1 del calendario de ejecución: lunes siguiente al anteproyecto.
INICIO_S1 = date(2026, 9, 21)
NUM_SEMANAS = 12  # S1 (21 sep) a S12 (13 dic)

MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]

HISTORIAS_E1 = [
    ("HU-01", "Crear tarea",
     "Como usuario, quiero crear una tarea con título, descripción opcional y fecha límite opcional, para organizar mi trabajo.",
     ["CA1. La tarea se crea con estado pendiente y un identificador único.",
      "CA2. Si el título está vacío o solo tiene espacios, se rechaza la creación.",
      "CA3. Si el título supera 100 caracteres, se rechaza.",
      "CA4. Si la fecha límite es anterior a hoy, se rechaza.",
      "CA5. Una fecha límite igual a hoy o posterior, o la ausencia de fecha, es válida."]),
    ("HU-02", "Editar tarea",
     "Como usuario, quiero editar el título, la descripción o la fecha límite de una tarea, para mantener su información al día.",
     ["CA1. Los cambios quedan reflejados en la tarea.",
      "CA2. Se aplican las mismas validaciones de título y fecha que al crear.",
      "CA3. Si una validación falla, la tarea no cambia.",
      "CA4. Si la tarea no existe, se informa el error.",
      "CA5. Una tarea terminada no se puede editar."]),
    ("HU-03", "Eliminar tarea",
     "Como usuario, quiero eliminar una tarea, para quitar lo que ya no es necesario.",
     ["CA1. La tarea deja de existir y no aparece en ninguna consulta.",
      "CA2. Las demás tareas no se ven afectadas.",
      "CA3. Si la tarea no existe, se informa el error."]),
    ("HU-04", "Asignar responsable",
     "Como usuario, quiero asignar un responsable a una tarea, para saber quién se encarga de ella.",
     ["CA1. El nombre queda guardado sin espacios sobrantes.",
      "CA2. Un nombre vacío o de solo espacios se rechaza.",
      "CA3. Reasignar reemplaza al responsable anterior.",
      "CA4. Si la tarea no existe, se informa el error.",
      "CA5. No se puede asignar responsable a una tarea terminada."]),
    ("HU-05", "Cambiar estado",
     "Como usuario, quiero cambiar el estado de una tarea, para reflejar su avance.",
     ["CA1. Se permiten las transiciones pendiente a en progreso, en progreso a terminada y en progreso a pendiente.",
      "CA2. No se puede pasar de pendiente a terminada.",
      "CA3. Una tarea terminada no cambia de estado.",
      "CA4. Para pasar a en progreso, la tarea debe tener responsable.",
      "CA5. Un estado desconocido se rechaza.",
      "CA6. Si la tarea no existe, se informa el error."]),
    ("HU-06", "Filtrar por estado",
     "Como usuario, quiero filtrar las tareas por estado, para ver en qué punto está cada una.",
     ["CA1. Devuelve solo las tareas que tienen ese estado.",
      "CA2. Si ninguna coincide, devuelve una lista vacía.",
      "CA3. Un estado desconocido se rechaza."]),
    ("HU-07", "Filtrar por rango de fecha límite",
     "Como usuario, quiero ver las tareas cuya fecha límite cae dentro de un rango, para planear mi semana.",
     ["CA1. Devuelve las tareas con fecha dentro del rango, incluidos los extremos.",
      "CA2. Las tareas sin fecha límite no aparecen.",
      "CA3. Si la fecha inicial es posterior a la final, se rechaza.",
      "CA4. Si ninguna coincide, devuelve una lista vacía."]),
]

# Cronograma: (id, actividad, inicio, fin, entregable, estado)
# Las fechas de A2 a A15 son propuestas a partir de la Entrega 1 y de los avances; confirmarlas.
ACTIVIDADES = [
    ("A1", "Formulación y entrega del anteproyecto", date(2026, 9, 1), date(2026, 9, 20),
     "Anteproyecto (20 sep)", "Completada"),
    ("A2", "Diseño de la arquitectura del agente y definición del caso de estudio", date(2026, 9, 21), date(2026, 10, 7),
     "Entrega 1", "Completada"),
    ("A3", "Línea base manual: siete pruebas y medición de cobertura", date(2026, 9, 28), date(2026, 10, 16),
     "Entrega 1", "Completada"),
    ("A4", "Regla de parada (nodo 5) y sus seis pruebas", date(2026, 10, 5), date(2026, 10, 16),
     "Entrega 1", "Completada"),
    ("A5", "Entrega 1", FECHA_E1, FECHA_E1, "Entregada el 24 oct, en fecha", "Completada"),
    ("A6", "Nodos con modelo de lenguaje: interpretar, planear, generar funcional y unitario",
     date(2026, 10, 25), date(2026, 11, 6), "Nodos 1, 2, 3a y 3b", "Completada"),
    ("A7", "Nodo de ejecución y ciclo de retroalimentación por cobertura",
     date(2026, 11, 2), date(2026, 11, 10), "Ciclo funcionando", "Completada"),
    ("A8", "Corrección de la medición y evaluación inicial (7 historias × 3 repeticiones)",
     date(2026, 11, 9), date(2026, 11, 12), "resultados/comparacion.json", "Completada"),
    ("A9", "Redacción y entrega de la Entrega 2", date(2026, 11, 9), FECHA_E2,
     "Entrega 2 (16 nov)", "En curso"),
    ("A10", "Subir el repositorio a GitHub (v0.2)", date(2026, 11, 13), date(2026, 11, 16),
     "Repositorio con etiqueta v0.2", "Pendiente"),
    ("A11", "Incorporación de la retroalimentación del tutor", date(2026, 11, 17), date(2026, 11, 22),
     "Documento ajustado", "Pendiente"),
    ("A12", "Línea base con LLM sin retroalimentación y medición de tiempo", date(2026, 11, 17), date(2026, 11, 22),
     "Cifras de línea base adicional", "Pendiente"),
    ("A13", "Cobertura de criterios de aceptación", date(2026, 11, 18), date(2026, 11, 23),
     "Métrica complementaria", "Pendiente"),
    ("A14", "Análisis de causas de las pruebas que no pasan", date(2026, 11, 19), date(2026, 11, 26),
     "Clasificación de fallos", "Pendiente"),
    ("A15", "Validación del plan de pruebas por un tester", date(2026, 11, 23), date(2026, 11, 27),
     "Plan de pruebas validado", "Pendiente"),
    ("A16", "Redacción de resultados, discusión y conclusiones", date(2026, 11, 23), date(2026, 12, 4),
     "Capítulos 4 a 6", "Pendiente"),
    ("A17", "Revisión de referencias (APA 7, DOI o URL) y formato", date(2026, 11, 30), date(2026, 12, 5),
     "Referencias completas", "Pendiente"),
    ("A18", "Revisión final, resumen e índices", date(2026, 12, 6), date(2026, 12, 9),
     "Documento final", "Pendiente"),
    ("A19", "Etiqueta v1.0 del repositorio", date(2026, 12, 10), date(2026, 12, 10),
     "Versión 1.0", "Pendiente"),
    ("A20", "Entrega final", FECHA_FINAL, FECHA_FINAL, "Documento final entregado", "Pendiente"),
    ("A21", "Sustentación", FECHA_FINAL, FECHA_FINAL, "Sustentación", "Pendiente"),
]

COLOR_HECHO = "7F7F7F"
COLOR_PENDIENTE = "2E75B6"


# ---------------------------------------------------------------- calendario

def semana_inicio(n):
    return INICIO_S1 + timedelta(weeks=n - 1)


def semana_fin(n):
    return semana_inicio(n) + timedelta(days=6)


def fmt(d):
    return f"{d.day} {MESES[d.month - 1]}"


def semanas_de(inicio, fin):
    """Números de semana (1..12) que se solapan con [inicio, fin]."""
    return [s for s in range(1, NUM_SEMANAS + 1)
            if inicio <= semana_fin(s) and fin >= semana_inicio(s)]


def etiqueta_semanas(inicio, fin):
    sem = semanas_de(inicio, fin)
    if not sem:
        return "Previa al calendario"
    return f"S{sem[0]}" if len(sem) == 1 else f"S{sem[0]}–S{sem[-1]}"


# ---------------------------------------------------------------- datos

def leer_csv(ruta: Path) -> list:
    if not ruta.exists():
        raise SystemExit(f"Falta el archivo: {ruta}. Ejecuta primero python -m src.generar_casos")
    with ruta.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def cargar_datos():
    ruta_comp = RAIZ / "resultados" / "comparacion.json"
    if not ruta_comp.exists():
        raise SystemExit(f"Falta el archivo: {ruta_comp}. Ejecuta primero python -m src.evaluar")
    comp = json.loads(ruta_comp.read_text(encoding="utf-8"))
    historias = comp["historias"]
    hus = sorted(historias)

    corridas = {hu: historias[hu]["repeticiones"] for hu in hus}
    todas = [r for hu in hus for r in corridas[hu]]
    coberturas = [r["cobertura"] for r in todas if "cobertura" in r]
    iteraciones = [r["iteraciones"] for r in todas if "iteraciones" in r]

    # Con la regla de parada, una ejecución de 1 iteración solo termina si cobertura >= 80.
    incoherentes = [r for r in todas if r.get("iteraciones") == 1 and r.get("cobertura", 0) < 80]
    if incoherentes:
        print(f"AVISO: {len(incoherentes)} ejecuciones terminaron en 1 iteración con cobertura < 80 %. "
              "Revisa resultados/comparacion.json antes de entregar.")

    plan_csv = RAIZ / "casos_generados" / "plan_de_pruebas.csv"
    return {
        "manual": float(comp["cobertura_manual"]),
        "repeticiones": comp.get("repeticiones", len(corridas[hus[0]])),
        "hus": hus,
        "historias": historias,
        "corridas": corridas,
        "media_global": round(sum(coberturas) / len(coberturas), 1),
        "sobre_umbral": sum(1 for c in coberturas if c >= 80),
        "total_corridas": len(coberturas),
        "primera_iteracion": sum(1 for i in iteraciones if i == 1),
        "iter_media": round(sum(iteraciones) / len(iteraciones), 2) if iteraciones else 0,
        "resumen": leer_csv(RAIZ / "casos_generados" / "resumen_general.csv"),
        "plan": leer_csv(plan_csv) if plan_csv.exists() else [],
    }


# ---------------------------------------------------------------- formato

def configurar_documento() -> Document:
    doc = Document()
    for seccion in doc.sections:
        seccion.left_margin = seccion.right_margin = Cm(2.5)
        seccion.top_margin = seccion.bottom_margin = Cm(2.5)

    normal = doc.styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(12)
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.space_after = Pt(6)

    for nombre, tamanio in [("Heading 1", 14), ("Heading 2", 12), ("Heading 3", 12)]:
        estilo = doc.styles[nombre]
        estilo.font.name = "Arial"
        estilo.font.size = Pt(tamanio)
        estilo.font.bold = True
        estilo.font.color.rgb = RGBColor(0, 0, 0)

    # Word pedirá actualizar los campos (índice) al abrir el archivo.
    actualizar = OxmlElement("w:updateFields")
    actualizar.set(qn("w:val"), "true")
    doc.settings.element.append(actualizar)
    return doc


def parrafo(doc, texto, centrado=False):
    p = doc.add_paragraph(texto)
    if centrado:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    else:
        p.paragraph_format.first_line_indent = Cm(1.25)
    return p


def sin_sangria(doc, texto):
    p = doc.add_paragraph(texto)
    p.paragraph_format.first_line_indent = None
    return p


def encabezado_tabla(doc, etiqueta, numero, titulo):
    t = doc.add_paragraph()
    t.paragraph_format.keep_with_next = True
    t.add_run(f"{etiqueta} {numero}").bold = True
    t.add_run().add_break()
    t.add_run(titulo).italic = True


def nota(doc, texto):
    n = doc.add_paragraph()
    r = n.add_run("Nota. ")
    r.italic = True
    r.font.size = Pt(10)
    r2 = n.add_run(texto)
    r2.font.size = Pt(10)
    doc.add_paragraph()


def tabla(doc, numero, titulo, encabezados, filas, texto_nota, tamanio=10):
    encabezado_tabla(doc, "Tabla", numero, titulo)
    grid = doc.add_table(rows=1, cols=len(encabezados))
    grid.style = "Table Grid"
    grid.alignment = WD_TABLE_ALIGNMENT.CENTER
    for celda, texto in zip(grid.rows[0].cells, encabezados):
        celda.text = ""
        celda.paragraphs[0].add_run(str(texto)).bold = True
    for fila in filas:
        celdas = grid.add_row().cells
        for celda, valor in zip(celdas, fila):
            celda.text = str(valor)
    for fila in grid.rows:
        for celda in fila.cells:
            for par in celda.paragraphs:
                par.paragraph_format.line_spacing = 1.0
                par.paragraph_format.space_after = Pt(0)
                for run in par.runs:
                    run.font.size = Pt(tamanio)
    nota(doc, texto_nota)


def sombrear(celda, color):
    tc_pr = celda._tc.get_or_add_tcPr()
    sombra = OxmlElement("w:shd")
    sombra.set(qn("w:val"), "clear")
    sombra.set(qn("w:color"), "auto")
    sombra.set(qn("w:fill"), color)
    tc_pr.append(sombra)


def gantt(doc, numero, titulo, actividades, texto_nota):
    actividades = [a for a in actividades if semanas_de(a[2], a[3])]
    encabezado_tabla(doc, "Figura", numero, titulo)
    grid = doc.add_table(rows=len(actividades) + 1, cols=NUM_SEMANAS + 1)
    grid.style = "Table Grid"
    grid.alignment = WD_TABLE_ALIGNMENT.CENTER
    grid.autofit = False
    ancho_etiqueta, ancho_semana = Cm(6.0), Cm(0.8)
    grid.columns[0].width = ancho_etiqueta
    for s_idx in range(1, NUM_SEMANAS + 1):
        grid.columns[s_idx].width = ancho_semana

    margenes = OxmlElement("w:tblCellMar")
    for lado in ("left", "right"):
        elem = OxmlElement(f"w:{lado}")
        elem.set(qn("w:w"), "28")
        elem.set(qn("w:type"), "dxa")
        margenes.append(elem)
    grid._tbl.tblPr.append(margenes)

    def fijar(celda, texto, ancho, tam=7, negrita=False, centrado=True):
        celda.width = ancho
        celda.text = ""
        par = celda.paragraphs[0]
        par.paragraph_format.space_after = Pt(0)
        par.paragraph_format.line_spacing = 1.0
        if centrado:
            par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = par.add_run(texto)
        run.font.size = Pt(tam)
        run.bold = negrita

    fijar(grid.rows[0].cells[0], "Actividad / semana", ancho_etiqueta, 8, True, centrado=False)
    for s in range(1, NUM_SEMANAS + 1):
        fijar(grid.rows[0].cells[s], f"S{s}", ancho_semana, 7, True)

    for i, (aid, nombre, ini, fin, _, estado) in enumerate(actividades, start=1):
        fila = grid.rows[i].cells
        fijar(fila[0], f"{aid}. {nombre}", ancho_etiqueta, 7, False, centrado=False)
        color = COLOR_HECHO if estado == "Completada" else COLOR_PENDIENTE
        activas = set(semanas_de(ini, fin))
        for s in range(1, NUM_SEMANAS + 1):
            celda = fila[s]
            celda.width = ancho_semana
            if s in activas:
                sombrear(celda, color)
            celda.paragraphs[0].paragraph_format.space_after = Pt(0)
    doc.add_paragraph()
    nota(doc, texto_nota)


def agregar_campo_indice(doc, instruccion, texto_inicial):
    p = doc.add_paragraph()
    run = p.add_run()
    inicio = OxmlElement("w:fldChar")
    inicio.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = instruccion
    separador = OxmlElement("w:fldChar")
    separador.set(qn("w:fldCharType"), "separate")
    texto = OxmlElement("w:t")
    texto.text = texto_inicial
    fin = OxmlElement("w:fldChar")
    fin.set(qn("w:fldCharType"), "end")
    for elemento in (inicio, instr, separador, texto, fin):
        run._r.append(elemento)


def referencias(doc, lista):
    doc.add_heading("Referencias", level=1)
    for ref in sorted(lista, key=lambda x: x.lower()):
        p = doc.add_paragraph(ref)
        p.paragraph_format.left_indent = Cm(1.25)
        p.paragraph_format.first_line_indent = Cm(-1.25)
        p.paragraph_format.line_spacing = 1.15


# ---------------------------------------------------------------- contenido

def construir(doc, d):
    manual = d["manual"]
    media = d["media_global"]
    reps = d["repeticiones"]
    total = d["total_corridas"]
    sobre = d["sobre_umbral"]
    n_plan = len(d["plan"])
    pasan = sum(int(float(r["pruebas_pasan"])) for r in d["resumen"])
    fallan = sum(int(float(r["pruebas_fallan"])) for r in d["resumen"])
    tasa = round(100 * pasan / (pasan + fallan), 1) if (pasan + fallan) else 0.0
    tasas_hu = []
    for r in d["resumen"]:
        p_, f_ = int(float(r["pruebas_pasan"])), int(float(r["pruebas_fallan"]))
        if p_ + f_:
            tasas_hu.append(100 * p_ / (p_ + f_))
    comparacion = "por debajo de" if media < manual else "por encima de"
    diferencia = media - manual
    meta_cumplida = diferencia >= META_PUNTOS

    # ---- Portada
    for _ in range(3):
        doc.add_paragraph()
    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = t.add_run("INSTITUCIÓN UNIVERSITARIA POLITÉCNICO GRANCOLOMBIANO")
    r.bold = True
    parrafo(doc, "Facultad de Ingeniería, Diseño e Innovación", centrado=True)
    parrafo(doc, "Ingeniería de Software · Grupo de investigación E-TIC", centrado=True)
    for _ in range(3):
        doc.add_paragraph()
    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = t.add_run("Agente de inteligencia artificial para la generación híbrida de casos de prueba a partir de historias de usuario")
    r.bold = True
    r.font.size = Pt(16)
    parrafo(doc, "Entrega 2: prototipo parcial y avance de resultados", centrado=True)
    for _ in range(3):
        doc.add_paragraph()
    parrafo(doc, f"Presenta: {AUTORA}, código {CODIGO}", centrado=True)
    parrafo(doc, f"Asesor: {ASESOR}", centrado=True)
    for _ in range(2):
        doc.add_paragraph()
    parrafo(doc, "Noviembre de 2026", centrado=True)
    doc.add_page_break()

    # ---- Índices
    doc.add_heading("Tabla de contenido", level=1)
    agregar_campo_indice(doc, 'TOC \\o "1-2" \\h \\z \\u',
                         "Clic derecho sobre este texto y elegir «Actualizar campo» para generar el índice.")
    doc.add_heading("Índice de tablas", level=1)
    for linea in [
        "Tabla 1. Estado de los objetivos específicos",
        "Tabla 2. Comparación de antecedentes de generación de casos de prueba",
        "Tabla 3. Fases del marco de diseño, entregables y validación",
        "Tabla 4. Historias de usuario del caso de estudio y sus criterios de aceptación",
        "Tabla 5. Nodos del agente",
        "Tabla 6. Stack tecnológico",
        "Tabla 7. Cronograma de actividades hasta la entrega final",
        "Tabla 8. Línea base manual inicial",
        "Tabla 9. Cobertura de líneas por historia",
        "Tabla 10. Pruebas unitarias generadas que pasan y fallan por historia",
    ]:
        sin_sangria(doc, linea)
    doc.add_heading("Índice de figuras", level=1)
    sin_sangria(doc, "Figura 1. Diagrama de Gantt del cronograma (semanas 1 a 12)")
    doc.add_page_break()

    # ---- Resumen
    doc.add_heading("Resumen", level=1)
    parrafo(doc, (
        "El diseño manual de casos de prueba a partir de historias de usuario es lento y depende de la experiencia de quien "
        "lo hace. Este trabajo presenta un agente de inteligencia artificial que genera pruebas funcionales (escenarios Gherkin) "
        "y unitarias (funciones pytest) a partir de historias en lenguaje natural. Después de cada ronda, el agente ejecuta las "
        "pruebas, mide la cobertura de líneas y repite el ciclo hasta alcanzar 80 % o agotar tres iteraciones. Se implementó como "
        "un grafo de cinco nodos con LangGraph y el modelo claude-haiku-5-5. Se evaluó sobre siete historias de un sistema de "
        f"gestión de tareas, con {reps} repeticiones por historia, frente a una línea base manual de {manual:.1f} % de cobertura de "
        f"líneas. La cobertura media del agente fue de {media:.1f} %, {comparacion} la línea base, y {sobre} de {total} ejecuciones "
        f"alcanzaron el umbral. El {tasa:.1f} % de las pruebas generadas pasó al ejecutarse. El agente no supera la línea base "
        "en este caso de estudio, y la tasa de pruebas que pasan muestra que la cobertura por sí sola no basta para evaluar las pruebas."
    ))
    parrafo(doc, "Palabras clave: pruebas de software, historias de usuario, agentes de inteligencia artificial, cobertura de código, modelos de lenguaje.")
    doc.add_page_break()

    # ---- 1. Introducción
    doc.add_heading("1. Introducción", level=1)
    doc.add_heading("1.1 Planteamiento del problema", level=2)
    parrafo(doc, (
        "El aseguramiento de calidad es una de las actividades más costosas del ciclo de vida del software. Dentro de esa fase, "
        "el diseño de casos de prueba es un punto de fricción recurrente: los equipos deben traducir requisitos expresados en "
        "lenguaje natural, casi siempre historias de usuario, en pruebas que verifiquen el comportamiento esperado por el negocio "
        "y la correcta implementación del código. Esa traducción se hace en su mayoría a mano, lo que la hace lenta, dependiente "
        "de la experiencia del analista y difícil de mantener cuando los requisitos cambian."
    ))
    parrafo(doc, (
        "El problema tiene respaldo en cifras de la industria. Según el World Quality Report 2023–24, las empresas de servicios "
        "financieros destinan cerca del 31 % de su presupuesto de TI a calidad y pruebas (Capgemini & Sogeti, 2023). A pesar de "
        "esa inversión, la automatización de pruebas se ubica en 44 % a nivel global, de modo que buena parte de las pruebas "
        "empresariales todavía se diseña a mano (Capgemini & Sogeti, 2024). La etapa de requisitos concentra una proporción alta "
        "de los defectos introducidos durante el desarrollo (Standish Group, 1994), y un defecto detectado al final de un proyecto "
        "puede costar hasta 100 veces más que uno detectado durante la toma de requisitos (Stecklein et al., 2004)."
    ))
    parrafo(doc, (
        "Frente a esta situación, las técnicas clásicas de generación automática trabajan sobre la estructura del código y no sobre "
        "lo que el requisito pide, por lo que no resuelven la trazabilidad entre historia y prueba. Los modelos de lenguaje sí "
        "entienden el texto natural, pero una invocación en una sola pasada no verifica ni corrige lo que genera, y eso produce "
        "cobertura incompleta y resultados que varían entre ejecuciones. Un agente puede planear pasos, ejecutar herramientas, "
        "observar resultados y refinar los casos. Esa capacidad de autoverificación es la que este trabajo aprovecha."
    ))
    doc.add_heading("1.2 Justificación", level=2)
    parrafo(doc, (
        "Resolver este problema es relevante porque la generación híbrida, funcional y unitaria, a partir de un mismo insumo "
        "acerca lo que el área de negocio espera, expresado en criterios de aceptación, a lo que el código efectivamente hace, "
        "verificado a nivel de unidad. La literatura revisada sugiere que incorporar retroalimentación de ejecución en el ciclo de "
        "generación mejora los resultados frente a una sola pasada del modelo (Zhang et al., 2025)."
    ))
    parrafo(doc, (
        "Para el programa, el proyecto articula dos competencias del perfil de Ingeniería de Software: el aseguramiento de calidad "
        "y el desarrollo de soluciones basadas en inteligencia artificial. Para el grupo de investigación E-TIC deja un antecedente "
        "y un artefacto reutilizable para futuros trabajos sobre IA agéntica en otras etapas del ciclo de vida."
    ))
    doc.add_heading("1.3 Objetivos", level=2)
    doc.add_heading("1.3.1 Objetivo general", level=3)
    parrafo(doc, (
        "Diseñar, implementar y evaluar un agente de inteligencia artificial que genere de forma híbrida casos de prueba "
        "funcionales y unitarios a partir de historias de usuario en lenguaje natural, con un ciclo de retroalimentación basado "
        "en cobertura de código."
    ))
    doc.add_heading("1.3.2 Objetivos específicos", level=3)
    parrafo(doc, "La Tabla 1 presenta el estado de cada objetivo específico a la fecha de esta entrega.")
    tabla(doc, 1, "Estado de los objetivos específicos",
          ["Objetivo específico", "Resultado", "Estado"],
          [
              ["Diseñar la arquitectura del agente, incluidos los módulos de interpretación, generación, ejecución y retroalimentación, y justificar el stack",
               "Grafo de cinco nodos con ciclo de cobertura documentado (Entrega 1)", "Completado"],
              ["Implementar un prototipo funcional sobre un sistema de gestión de tareas, con generación funcional (BDD/Gherkin) y unitaria (pytest) y medición de cobertura",
               "Nodos 1 a 5 implementados. Los escenarios Gherkin se generan, pero no se ejecutan en la evaluación", "Completado con una salvedad"],
              ["Evaluar el prototipo frente a una línea base manual y a generación por LLM sin retroalimentación, con cobertura, cobertura de criterios de aceptación y tiempo de generación",
               f"Evaluación inicial con {reps} repeticiones frente a la línea base manual. Pendientes: línea base sin retroalimentación, cobertura de criterios y tiempo", "En curso"],
          ],
          "Elaboración propia con base en los objetivos del anteproyecto y el avance del proyecto.")

    doc.add_heading("1.4 Marco teórico", level=2)
    parrafo(doc, (
        "El trabajo se apoya en dos ejes: la generación automática de casos de prueba y la inteligencia artificial agéntica. Las "
        "técnicas clásicas, como la búsqueda evolutiva de EvoSuite, exploran las entradas de un programa a partir de su estructura "
        "interna, sin considerar la intención funcional descrita en los requisitos. Esa limitación ha llevado a explorar enfoques "
        "que parten del lenguaje natural."
    ))
    parrafo(doc, (
        "Las revisiones sistemáticas recientes documentan un crecimiento marcado de trabajos sobre generación de pruebas unitarias "
        "con modelos de lenguaje, y señalan como retos la falta de retroalimentación de ejecución y el carácter no determinista de "
        "estos modelos (Zhang et al., 2025). HITS atiende la cobertura de ramas difíciles segmentando el método antes de generar "
        "las pruebas (Wang et al., 2024). Incluso en un enfoque centrado en el código, una única invocación del modelo resulta insuficiente."
    ))
    parrafo(doc, (
        "A diferencia de una invocación aislada, un agente planea una secuencia de pasos, invoca herramientas externas, como un "
        "framework de pruebas o un medidor de cobertura, y usa los resultados para refinar su salida. Esto se ha explorado en "
        "sistemas que realimentan la generación con el reporte de cobertura de la ronda anterior (Dong et al., 2025), y en "
        "arquitecturas multiagente donde varios agentes especializados llegan a consenso sobre el resultado esperado de una prueba "
        "(Xu et al., 2025). Más cerca del insumo de este trabajo, hay propuestas que generan especificaciones de prueba a partir de "
        "historias de usuario (Rahman y Zhu, 2024) y otras que derivan casos de prueba desde casos de uso mediante grafos de flujo "
        "de control generados por el modelo (Yang et al., 2025). La Tabla 2 resume estos antecedentes y la limitación de cada uno "
        "frente a esta propuesta. Ninguno combina insumo en lenguaje natural, generación híbrida de pruebas funcionales y unitarias, "
        "y retroalimentación de cobertura dentro de un mismo ciclo."
    ))
    tabla(doc, 2, "Comparación de antecedentes de generación de casos de prueba con modelos de lenguaje y agentes",
          ["Trabajo", "Insumo", "Técnica", "Limitación frente a esta propuesta"],
          [
              ["HITS (Wang et al., 2024)", "Código fuente existente", "Segmenta el método antes de generar, para alcanzar ramas difíciles",
               "No parte de requisitos en lenguaje natural; solo genera pruebas unitarias"],
              ["Dong et al. (2025), survey de agentes", "Código fuente existente", "Realimenta la generación con el reporte de cobertura de la ronda anterior",
               "Aplicado sobre código existente; no parte de historias de usuario ni de pruebas funcionales"],
              ["Xu et al. (2025)", "Código fuente en Java", "Agentes especializados generan casos; un panel de modelos llega a consenso sobre el resultado esperado",
               "Limitado a pruebas unitarias en Java; no parte de historias de usuario"],
              ["Rahman y Zhu (2024)", "Historias de usuario", "El modelo genera la especificación de la prueba junto con la historia",
               "Genera especificaciones, no necesariamente pruebas ejecutables con retroalimentación de cobertura"],
              ["Yang et al. (2025), LLMCFG-TGen", "Casos de uso en lenguaje natural", "El modelo genera un grafo de flujo de control; cada camino se convierte en un caso de prueba",
               "Parte de casos de uso, no de historias ágiles; produce casos descritos en texto, no pruebas unitarias ejecutables"],
          ],
          "Elaboración propia con base en Wang et al. (2024), Dong et al. (2025), Xu et al. (2025), Rahman y Zhu (2024) y Yang et al. (2025).",
          tamanio=9)
    doc.add_page_break()

    # ---- 2. Metodología
    doc.add_heading("2. Estrategia metodológica y desarrollo", level=1)
    doc.add_heading("2.1 Enfoque metodológico", level=2)
    parrafo(doc, (
        "El desarrollo sigue Design Science Research (Peffers et al., 2007), un marco adecuado cuando el resultado es un artefacto "
        "que debe diseñarse, construirse y evaluarse empíricamente. La Tabla 3 relaciona cada actividad del marco con lo realizado, "
        "con el entregable correspondiente y con la forma de validarla."
    ))
    tabla(doc, 3, "Fases del marco de diseño, entregables y validación",
          ["Actividad DSR", "Realización en el proyecto", "Entregable", "Validación"],
          [
              ["Identificación del problema", "Costo de diseñar pruebas a mano a partir de historias", "Sección 1", "Cifras de la industria citadas"],
              ["Definición de objetivos", "Objetivo general y tres objetivos específicos", "Sección 1.3", "Estado de cada objetivo (Tabla 1)"],
              ["Diseño y desarrollo", "Grafo de cinco nodos con ciclo de cobertura", "Código del agente; repositorio", "Pruebas del nodo de decisión (seis pruebas)"],
              ["Demostración", f"Ejecución sobre siete historias con {reps} repeticiones cada una", "resultados/comparacion.json",
               "Repetición independiente de cada historia"],
              ["Evaluación", "Cobertura frente a la línea base; proporción de pruebas que pasan", "Sección 4",
               "Línea base manual y, pendiente, LLM sin retroalimentación"],
              ["Comunicación", "Documento de la Entrega 2 y documento final", "Este documento; sustentación", "Revisión del tutor"],
          ],
          "Elaboración propia con base en Peffers et al. (2007).")

    doc.add_heading("2.2 Caso de estudio", level=2)
    parrafo(doc, (
        "El sistema bajo prueba es un gestor de tareas en Python que guarda los datos en memoria e implementa siete funcionalidades: "
        "crear, editar y eliminar tareas, asignar responsable, cambiar estado, y filtrar por estado y por fecha límite. La fecha "
        "actual se inyecta como dependencia para que las pruebas no dependan del reloj del sistema. La Tabla 4 presenta las historias "
        "de usuario con sus criterios de aceptación, que son la entrada del agente."
    ))
    filas_hu = [[hu, titulo, historia, "\n".join(cas)] for hu, titulo, historia, cas in HISTORIAS_E1]
    tabla(doc, 4, "Historias de usuario del caso de estudio y sus criterios de aceptación",
          ["ID", "Funcionalidad", "Historia de usuario", "Criterios de aceptación"], filas_hu,
          "Elaboración propia. Las historias y criterios se mantienen como en la Entrega 1.", tamanio=8)

    doc.add_heading("2.3 Arquitectura del agente", level=2)
    parrafo(doc, (
        "El agente se modela como un grafo de estados con cinco nodos. El primero interpreta la historia y extrae criterios de "
        "aceptación, actores y condiciones de borde. El segundo planea qué casos funcionales y unitarios hacen falta. Los nodos 3a "
        "y 3b generan escenarios Gherkin y pruebas pytest. El cuarto ejecuta las pruebas y mide la cobertura. El quinto decide si el "
        "ciclo termina o si regresa a la planeación con las líneas no cubiertas. La Tabla 5 resume los nodos."
    ))
    tabla(doc, 5, "Nodos del agente",
          ["Nodo", "Función", "Tipo", "Entrada", "Salida"],
          [
              ["1. interpretar", "Extrae criterios de aceptación", "Modelo de lenguaje", "Historia", "Criterios"],
              ["2. planear", "Propone casos; prioriza líneas no cubiertas", "Modelo de lenguaje", "Criterios y números de línea", "Plan de casos"],
              ["3a. generar funcional", "Escenarios Gherkin", "Modelo de lenguaje", "Plan de casos", "Escenarios .feature"],
              ["3b. generar unitario", "Funciones pytest", "Modelo de lenguaje", "Plan de casos y criterios", "Pruebas .py"],
              ["4. ejecutar", "Ejecuta pytest con coverage.py", "Determinista", "Pruebas", "Cobertura y líneas no cubiertas"],
              ["5. decidir", "Termina si la cobertura es ≥ 80 % o se llega a la iteración 3", "Determinista", "Cobertura e iteración", "Terminar o continuar"],
          ],
          "Elaboración propia. Parámetros definidos en src/agente/config.py.")
    parrafo(doc, (
        "El ciclo se detiene cuando la cobertura de líneas alcanza 80 % o cuando se completan tres iteraciones, para evitar ciclos "
        "indefinidos y controlar el costo de las llamadas al modelo. El modelo es claude-haiku-5-5. Durante el desarrollo, el modelo "
        "inicial fue retirado por el proveedor y las llamadas devolvieron error 404, por lo que se migró al modelo vigente. Cualquier "
        "repetición del experimento debe usar el mismo modelo."
    ))

    doc.add_heading("2.4 Stack tecnológico", level=2)
    parrafo(doc, (
        "La Tabla 6 presenta las herramientas del proyecto. En la Entrega 1 el proveedor del modelo y el modelo concreto estaban "
        "pendientes; ya están fijados y se citan aquí."
    ))
    tabla(doc, 6, "Stack tecnológico del proyecto",
          ["Componente", "Herramienta", "Función en el proyecto"],
          [
              ["Lenguaje", "Python 3.14", "Lenguaje del sistema bajo prueba y del agente"],
              ["Orquestación del agente", "LangGraph", "Modela el agente como grafo de estados con la decisión de repetir el ciclo"],
              ["Modelo de lenguaje", "Claude (Anthropic), modelo claude-haiku-5-5", "Interpreta historias, planea y genera las pruebas (nodos 1, 2, 3a y 3b)"],
              ["Pruebas unitarias", "pytest", "Ejecuta las pruebas unitarias del agente y de la línea base"],
              ["Pruebas funcionales", "Gherkin (.feature)", "Escenarios generados; su ejecución con pytest-bdd queda pendiente"],
              ["Cobertura", "coverage.py (pytest-cov)", "Mide cobertura de líneas; alimenta el ciclo de retroalimentación"],
              ["Documentos", "python-docx", "Genera el plan de pruebas y este documento en Word"],
              ["Control de versiones", "Git y GitHub", "Historial del código y evidencia de avance"],
          ],
          "Elaboración propia. Versiones en requirements.txt.")

    doc.add_heading("2.5 Protocolo de evaluación", level=2)
    parrafo(doc, (
        f"Cada historia se procesó {reps} veces de forma independiente. La línea base manual se midió ejecutando las siete pruebas "
        "del proyecto sobre el mismo sistema. Para comparar en igualdad de condiciones, la cobertura se mide solo por líneas: la "
        "línea base de la Entrega 1 (68 %) incluía ramas, y por eso no es directamente comparable con la cobertura de líneas del agente. "
        "Para cada ejecución del agente se registraron la cobertura y el número de iteraciones. En la corrida de generación se "
        "registraron además las pruebas que pasan y las que fallan."
    ))
    doc.add_heading("2.6 Validez y limitaciones", level=2)
    parrafo(doc, (
        "Durante la evaluación se detectó un error de medición: pytest ejecutaba también las pruebas de las historias anteriores y "
        "las pruebas manuales, lo que inflaba la cobertura de las historias posteriores. El nodo de ejecución se corrigió para que "
        "cada historia ejecute solo sus propias pruebas. Todas las cifras de este documento provienen de la versión corregida."
    ))
    parrafo(doc, (
        "Otras limitaciones son las siguientes. El modelo de lenguaje no es determinista, por lo que las repeticiones varían. El caso "
        "de estudio es un único sistema pequeño. La cobertura de líneas no indica si una prueba verifica el comportamiento correcto, "
        "y las pruebas se evalúan solo contra el sistema, sin un oráculo independiente. Los escenarios Gherkin se generan, pero no "
        "se ejecutan en esta evaluación."
    ))

    # ---- 3. Cronograma
    doc.add_heading("3. Cronograma de actividades", level=1)
    doc.add_heading("3.1 Fechas del programa y calendario", level=2)
    parrafo(doc, (
        "Las fechas límite del programa son el anteproyecto (20 de septiembre de 2026), la Entrega 1 (24 de octubre), la Entrega 2 "
        "(16 de noviembre) y la entrega final con sustentación (12 de diciembre). El calendario de ejecución empieza la semana "
        "siguiente al anteproyecto, el 21 de septiembre, y se organiza en doce semanas hasta el 13 de diciembre. La Tabla 7 presenta "
        "las actividades con sus semanas, fechas y entregables."
    ))
    doc.add_heading("3.2 Ejecución frente al plan", level=2)
    parrafo(doc, (
        "La Entrega 1 se entregó el 24 de octubre, en la fecha límite, con el diseño de la arquitectura, el caso de estudio, la línea "
        "base y la regla de parada. Al 26 de octubre la fase de construcción del prototipo había comenzado, como preveía el plan. "
        "La construcción de los nodos con modelo de lenguaje, el ciclo de retroalimentación y la evaluación inicial se completaron "
        "antes del 12 de noviembre. Lo que resta corresponde a la Entrega 2, que vence el 16 de noviembre, y a las mediciones "
        "complementarias y la redacción final."
    ))
    filas_cron = []
    for aid, nombre, ini, fin, entregable, estado in ACTIVIDADES:
        if ini < INICIO_S1 and fin < INICIO_S1:
            sem = "Previa"
        else:
            sem = etiqueta_semanas(ini, fin)
        filas_cron.append([aid, nombre, sem, f"{fmt(ini)}–{fmt(fin)}" if ini != fin else fmt(ini), entregable, estado])
    tabla(doc, 7, "Cronograma de actividades hasta la entrega final",
          ["ID", "Actividad", "Semana", "Fechas (2026)", "Entregable", "Estado"],
          filas_cron,
          "Elaboración propia. Fechas de las actividades A2 a A15 propuestas a partir de la Entrega 1 y del avance del proyecto. "
          "Estado al 12 de noviembre de 2026.", tamanio=8)
    gantt(doc, 1, "Diagrama de Gantt del cronograma (semanas 1 a 12)", ACTIVIDADES,
          "Gris: actividad completada. Azul: actividad en curso o pendiente. S1 = 21 de septiembre; S12 = 7 a 13 de diciembre. "
          "Las actividades anteriores a S1 (anteproyecto) no aparecen en la figura.")

    doc.add_heading("3.3 Desviaciones y riesgos", level=2)
    parrafo(doc, (
        "No hay desviaciones en las fechas límite del programa. El riesgo principal es la Entrega 2 y la semana final: la línea base "
        "con LLM sin retroalimentación (A12) y el análisis de fallos (A14) dependen del tiempo disponible para ejecutar el modelo y "
        "clasificar las pruebas. Si alguna de estas actividades se atrasa, se reduce el número de repeticiones antes que el alcance "
        "de la sustentación."
    ))
    doc.add_page_break()

    # ---- 4. Resultados
    doc.add_heading("4. Resultados", level=1)
    doc.add_heading("4.1 Línea base manual", level=2)
    parrafo(doc, (
        "La línea base de la Entrega 1 usa siete pruebas escritas a mano y las siete pasan. Con cobertura de líneas y ramas, la "
        "cobertura total es de 68 %. La Tabla 8 presenta la cifra de líneas que se compara con el agente."
    ))
    tabla(doc, 8, "Línea base manual inicial",
          ["Medida", "Valor", "Fuente"],
          [
              ["Pruebas manuales que pasan", "7 de 7", "Entrega 1"],
              ["Cobertura de líneas y ramas", "68 %", "Entrega 1"],
              ["Cobertura de líneas (valor de comparación)", f"{manual:.1f} %", "resultados/comparacion.json"],
          ],
          "Elaboración propia. La diferencia entre el 68 % con ramas y el valor de líneas se explica en la sección 2.5.")

    doc.add_heading("4.2 Cobertura del agente por historia", level=2)
    parrafo(doc, (
        f"La Tabla 9 resume la cobertura de líneas de las {reps} repeticiones de cada historia. La media global del agente fue de "
        f"{media:.1f} %, frente a {manual:.1f} % de la línea base manual. De las {total} ejecuciones, {sobre} alcanzaron el umbral de "
        f"80 %. El número medio de iteraciones fue de {d['iter_media']:.2f}, y en {d['primera_iteracion']} ejecuciones el ciclo "
        "terminó en la primera iteración."
    ))
    filas_cob = []
    for hu in d["hus"]:
        h = d["historias"][hu]
        ok = sum(1 for r in d["corridas"][hu] if r.get("cobertura", 0) >= 80)
        filas_cob.append([hu, f"{h['cobertura_min']:.1f}", f"{h['cobertura_media']:.1f}",
                          f"{h['cobertura_max']:.1f}", f"{ok} de {reps}"])
    filas_cob.append(["Línea base manual", f"{manual:.1f}", f"{manual:.1f}", f"{manual:.1f}", "—"])
    tabla(doc, 9, "Cobertura de líneas por historia (porcentaje)",
          ["Historia", "Mínima", "Media", "Máxima", "Ejecuciones ≥ 80 %"], filas_cob,
          f"Elaboración propia a partir de resultados/comparacion.json, con {reps} repeticiones por historia.")

    doc.add_heading("4.3 Pruebas generadas", level=2)
    parrafo(doc, (
        "La Tabla 10 muestra cuántas pruebas unitarias de la última corrida de generación pasan y cuántas fallan. En conjunto, "
        f"{pasan} pruebas pasaron y {fallan} fallaron, una tasa de {tasa:.1f} %."
    ))
    filas_pas = []
    for r in d["resumen"]:
        p_, f_ = int(float(r["pruebas_pasan"])), int(float(r["pruebas_fallan"]))
        tot = p_ + f_
        filas_pas.append([r["historia"], tot, p_, f_, f"{100 * p_ / tot:.1f}" if tot else "—"])
    tabla(doc, 10, "Pruebas unitarias generadas que pasan y fallan por historia",
          ["Historia", "Total", "Pasan", "Fallan", "Tasa que pasa (%)"], filas_pas,
          "Elaboración propia a partir de casos_generados/resumen_general.csv. Una corrida por historia.")

    doc.add_heading("4.4 Plan de pruebas", level=2)
    parrafo(doc, (
        f"El agente redactó un plan de pruebas con {n_plan} casos, cada uno con precondiciones, pasos y resultado esperado. El plan "
        "se entrega como archivo Word (casos_generados/plan_de_pruebas.docx). Los resultados esperados son un borrador que el "
        "tester debe validar antes de usarlos."
    ))
    doc.add_heading("4.5 Cumplimiento de la meta", level=2)
    parrafo(doc, (
        f"El anteproyecto planteó superar la línea base en al menos {META_PUNTOS:.0f} puntos porcentuales. La diferencia observada "
        f"es de {diferencia:+.1f} puntos ({media:.1f} % frente a {manual:.1f} %). "
        + ("La meta se cumple." if meta_cumplida else "La meta no se cumple con los resultados actuales.")
    ))
    doc.add_page_break()

    # ---- 5. Discusión
    doc.add_heading("5. Discusión", level=1)
    doc.add_heading("5.1 Cobertura frente a la línea base manual", level=2)
    parrafo(doc, (
        f"La cobertura media del agente ({media:.1f} %) quedó {comparacion} la línea base manual ({manual:.1f} %). La línea base "
        "se diseñó con pruebas dirigidas a cada funcionalidad y con los casos de borde que el diseño manual suele omitir. El agente "
        "genera conjuntos de pruebas que pueden ejercitar las mismas rutas varias veces. Esta explicación es una hipótesis: la "
        "comparación con la línea base de LLM sin retroalimentación debe confirmarla o descartarla."
    ))
    doc.add_heading("5.2 Pruebas que no pasan", level=2)
    if tasas_hu:
        parrafo(doc, (
            f"La proporción de pruebas que pasan varía entre historias, entre {min(tasas_hu):.1f} % y {max(tasas_hu):.1f} %, como muestra "
            "la Tabla 10. Un fallo puede deberse a un error de la prueba generada o a un defecto real del sistema. Clasificar cada "
            "fallo en una de esas dos categorías es el siguiente paso del análisis. Mientras tanto, la cobertura no debe presentarse "
            "sin la tasa de pruebas que pasan, porque una prueba que falla también ejecuta líneas."
        ))
    doc.add_heading("5.3 Alcance del ciclo de retroalimentación", level=2)
    parrafo(doc, (
        f"En {d['primera_iteracion']} de {total} ejecuciones el ciclo terminó en la primera iteración, lo que indica que el umbral se "
        "alcanzó sin retroalimentación en esos casos. El nodo de planeación recibe únicamente los números de las líneas no cubiertas, "
        "no su contenido (src/agente/nodo_planear.py). Con solo el número de línea, el modelo tiene poca información para decidir "
        "qué caso escribir. Esta es una limitación de diseño y la primera línea de trabajo futuro."
    ))
    doc.add_heading("5.4 Implicaciones para el enfoque híbrido", level=2)
    parrafo(doc, (
        "A partir de una misma entrada, el agente produce pruebas funcionales y unitarias, lo que corresponde al propósito híbrido "
        "del anteproyecto. Su utilidad práctica depende de la revisión humana: las pruebas que fallan deben clasificarse antes de "
        "contar como evidencia."
    ))

    # ---- 6. Conclusiones
    doc.add_heading("6. Conclusiones y trabajo futuro", level=1)
    parrafo(doc, (
        "Se implementó un agente de cinco nodos que genera pruebas funcionales y unitarias a partir de historias de usuario, las "
        "ejecuta y reutiliza la cobertura para una nueva ronda de generación. El prototipo funciona de extremo a extremo sobre el "
        f"caso de estudio. Su cobertura media ({media:.1f} %) quedó {comparacion} la línea base manual ({manual:.1f} %), y el "
        f"{100 - tasa:.1f} % de sus pruebas no pasó. La meta de {META_PUNTOS:.0f} puntos no se alcanzó en este caso de estudio."
    ))
    parrafo(doc, (
        "Como trabajo futuro se proponen tres líneas. La primera es entregar el contenido de las líneas no cubiertas a los nodos de "
        "planeación y generación, y no solo sus números. La segunda es clasificar los fallos y añadir un paso de validación de los "
        "resultados esperados contra los criterios de aceptación. La tercera es repetir el experimento con más sistemas y más "
        "repeticiones, y ejecutar los escenarios Gherkin con pytest-bdd."
    ))

    doc.add_page_break()
    referencias(doc, [
        "Anthropic. (s. f.). Claude API documentation. https://docs.claude.com",
        "Capgemini & Sogeti. (2023). World Quality Report 2023–24. Capgemini. [URL por completar]",
        "Capgemini & Sogeti. (2024). World Quality Report 2024–25. Capgemini. [URL por completar]",
        "Coverage.py. (s. f.). Coverage.py documentation. https://coverage.readthedocs.io/",
        "Cucumber. (s. f.). Gherkin reference. https://cucumber.io/docs/gherkin/reference/",
        "Dong, Y., Jiang, X., Qian, J., Wang, T., Zhang, K., Jin, Z., & Li, G. (2025). A survey on code generation with LLM-based agents. arXiv. https://arxiv.org/abs/2508.00083",
        "LangChain. (s. f.). LangGraph documentation. https://langchain-ai.github.io/langgraph/",
        "Peffers, K., Tuunanen, T., Rothenberger, M. A., & Chatterjee, S. (2007). A design science research methodology for information systems research. Journal of Management Information Systems, 24(3), 45–77. https://doi.org/10.2753/MIS0742-1222240302",
        "pytest-dev. (s. f.). pytest documentation. https://docs.pytest.org/",
        "Rahman, T., & Zhu, Y. (2024). Automated user story generation with test case specification using large language model. arXiv. https://arxiv.org/abs/2404.01558",
        "Standish Group International. (1994). The CHAOS report. https://www.standishgroup.com/sample_research_files/chaos_report_1994.pdf",
        "Stecklein, J., Dabney, J., Dick, B., Haskins, B., Lovell, R., & Moroney, G. (2004). Error cost escalation through the project life cycle. En Proceedings of the 14th Annual International Symposium of INCOSE. [DOI o URL por completar]",
        "Wang, Z., Liu, K., Li, G., & Jin, Z. (2024). HITS: High-coverage LLM-based unit test generation via method slicing. En Proceedings of the 39th IEEE/ACM International Conference on Automated Software Engineering (pp. 1258–1268). [DOI por completar]",
        "Xu, Q., Wang, G., Briand, L., & Liu, K. (2025). Hallucination to consensus: Multi-agent LLMs for end-to-end test generation. arXiv. https://arxiv.org/abs/2506.02943",
        "Yang, Z., et al. (2025). LLMCFG-TGen: Using LLM-generated control flow graphs to automatically create test cases from use cases. arXiv. https://arxiv.org/abs/2512.06401 [lista completa de autores por completar]",
        "Zhang, Q., Fang, C., Zheng, Y., Zhang, Y., Zhao, Y., Huang, R., Zhou, J., Yang, Y., Zheng, T., & Chen, Z. (2025). Large language models for unit testing: A systematic literature review. arXiv. https://arxiv.org/abs/2506.15227",
    ])


PENDIENTES = [
    "Confirmar las fechas propuestas de las actividades A2 a A15 con tu registro real (tabla 8 y figura 1).",
    "Reconciliar la línea base: la Entrega 1 reporta 71 de 94 líneas (75,5 %) y evaluar.py reporta el valor de comparacion.json. Ejecuta: pytest tests\\test_tareas_manual.py --cov=gestor_tareas --cov-report=term.",
    "Completar las URL o DOI marcados en las referencias (Capgemini, Stecklein, Wang et al.).",
    "Completar la lista de autores de Yang et al. (2025); la Entrega 1 solo tiene el primer autor.",
    "Verificar que el 50 % de defectos en la etapa de requisitos aparece en el CHAOS Report de 1994. Si no, cambia la fuente de esa cifra.",
    "Medir la línea base con LLM sin retroalimentación (MAX_ITERACIONES = 1), el tiempo de generación y la cobertura de criterios de aceptación.",
    "Clasificar las pruebas que fallan en error del agente o defecto real del sistema (sección 5.2).",
    "Confirmar o descartar la hipótesis de la sección 5.1 con la línea base de LLM sin retroalimentación.",
    "Confirmar la sustentación en la fecha del programa (12 de diciembre).",
]


def main():
    datos = cargar_datos()
    if datos["media_global"] >= datos["manual"]:
        print("AVISO: la cobertura media del agente supera la línea base. Revisa las secciones 4.5 y 5.1.")
    SALIDA_DIR.mkdir(exist_ok=True)
    doc = configurar_documento()
    construir(doc, datos)
    ruta = SALIDA_DIR / "Entrega2_Trabajo_de_grado.docx"
    doc.save(ruta)
    print(f"Documento generado: {ruta}")
    print("\nAntes de entregar, revisa:")
    for p in PENDIENTES:
        print(f"  - {p}")


if __name__ == "__main__":
    main()

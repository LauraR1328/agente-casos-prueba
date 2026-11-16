"""Nodo 3b: genera pruebas unitarias con pytest."""
import ast
import os
import anthropic
from .config import MODELO
from .llm import texto_de_respuesta


CABECERA_TEST = '''"""Pruebas unitarias generadas por el agente - {titulo}."""
from datetime import date, timedelta
import pytest
from gestor_tareas import (
    GestorTareas,
    EstadoTarea,
    ErrorValidacion,
    TareaNoEncontrada,
    OperacionNoPermitida,
)

HOY = date(2026, 11, 1)


@pytest.fixture
def gestor():
    return GestorTareas(hoy=lambda: HOY)

'''


def limpiar_cuerpo(cuerpo: str) -> str:
    """
    Deja solo código Python válido: quita bloques markdown, texto antes del
    primer test y texto explicativo al final que el modelo pudiera añadir.
    """
    lineas = [l for l in cuerpo.splitlines() if not l.strip().startswith("```")]

    # Recortar todo lo que aparece antes del primer test, comentario CA o decorador
    inicio = next(
        (i for i, l in enumerate(lineas)
         if l.startswith(("def test_", "# CA", "@"))),
        0,
    )
    lineas = lineas[inicio:]

    # Si queda texto no válido como Python, cortar desde esa línea hasta el final
    for _ in range(3):
        try:
            ast.parse("\n".join(lineas))
            break
        except SyntaxError as e:
            if not e.lineno:
                break
            lineas = lineas[: e.lineno - 1]

    return "\n".join(lineas).strip()


def generar_pruebas_unitarias(estado: dict) -> dict:
    """
    Genera funciones pytest concretas a partir del plan de casos de prueba.
    Incluye una cabecera con los imports necesarios.
    """
    historia = estado["historia"]
    plan = estado.get("plan", [])
    criterios = estado.get("criterios", [])
    lineas = estado.get("lineas_no_cubiertas", [])

    cliente = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    contexto_lineas = ""
    if lineas:
        contexto_lineas = f"\nLíneas no cubiertas aún: {lineas}. Genera pruebas que ejerciten esas líneas."

    prompt = f"""Eres un experto en pruebas de software con Python y pytest.

Genera funciones de prueba pytest para los casos listados.

Reglas:
- Cada función empieza con test_
- Nombre descriptivo en snake_case
- Usa el fixture gestor (ya definido, retorna GestorTareas con HOY = date(2026, 11, 1))
- Importaciones y fixture ya están en el archivo; NO los repitas
- Genera SOLO las funciones, sin imports ni fixtures
- Etiqueta cada prueba con un comentario # CA<n> indicando el criterio que cubre
- Las validaciones usan pytest.raises(ErrorValidacion), pytest.raises(TareaNoEncontrada), pytest.raises(OperacionNoPermitida)
- Transiciones válidas: pendiente->en_progreso (con responsable), en_progreso->terminada, en_progreso->pendiente
- Transición inválida: pendiente->terminada lanza OperacionNoPermitida
- Para pasar a en_progreso la tarea debe tener responsable asignado

Historia:
{historia}

Criterios de aceptación:
{chr(10).join(criterios)}

Casos de prueba:
{chr(10).join(f'- {c}' for c in plan)}
{contexto_lineas}"""

    respuesta = cliente.messages.create(
        model=MODELO,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    cuerpo = texto_de_respuesta(respuesta)

    cuerpo = limpiar_cuerpo(cuerpo)

    titulo = historia.split(",")[0].strip()[:50]
    cabecera = CABECERA_TEST.format(titulo=titulo)
    contenido = cabecera + cuerpo + "\n"

    num_tests = cuerpo.count("def test_")
    print(f"\n[Nodo 3b] Funciones pytest generadas: {num_tests}")

    return {**estado, "pruebas_unitarias": contenido}

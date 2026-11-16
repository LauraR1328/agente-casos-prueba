"""Nodo 3a: genera escenarios Gherkin (pruebas funcionales BDD)."""
import os
import anthropic
from .config import MODELO
from .llm import texto_de_respuesta


PLANTILLA_FEATURE = """# language: es
Característica: {titulo}

{escenarios}
"""


def generar_pruebas_funcionales(estado: dict) -> dict:
    """
    Genera un archivo .feature con escenarios Gherkin a partir del plan de casos.
    Cada escenario cubre un criterio de aceptación.
    """
    historia = estado["historia"]
    plan = estado.get("plan", [])
    criterios = estado.get("criterios", [])

    cliente = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    prompt = f"""Eres un experto en BDD (Behavior-Driven Development).
Genera escenarios Gherkin en español para los casos de prueba listados.

Reglas:
- Usa exactamente: Escenario:, Dado, Cuando, Entonces, Y
- Cada escenario debe tener un nombre descriptivo único
- No incluyas la línea "Característica:" ni "# language:", solo los escenarios
- El código del módulo se llama gestor_tareas y la clase principal GestorTareas
- Los pasos deben ser concretos y ejecutables
- Genera un escenario por caso de prueba

Historia de usuario:
{historia}

Criterios de aceptación:
{chr(10).join(criterios)}

Casos de prueba a cubrir:
{chr(10).join(f'- {c}' for c in plan)}"""

    respuesta = cliente.messages.create(
        model=MODELO,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    escenarios = texto_de_respuesta(respuesta)

    # Extraer título de la historia para el archivo feature
    titulo = historia.split(",")[0].replace("Como usuario", "").strip()
    if not titulo:
        titulo = "Funcionalidad del sistema"

    contenido_feature = PLANTILLA_FEATURE.format(
        titulo=titulo,
        escenarios=escenarios,
    )

    num_escenarios = escenarios.count("Escenario:")
    print(f"\n[Nodo 3a] Escenarios Gherkin generados: {num_escenarios}")

    return {**estado, "pruebas_funcionales": contenido_feature}

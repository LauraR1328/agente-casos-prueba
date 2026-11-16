"""Nodo 2: planea los casos de prueba a partir de criterios y líneas no cubiertas."""
import os
import anthropic
from .config import MODELO
from .llm import texto_de_respuesta


def planear_casos(estado: dict) -> dict:
    """
    A partir de los criterios de aceptación y las líneas no cubiertas de la
    iteración anterior, genera un plan de casos de prueba.

    Cada caso del plan es una cadena que describe qué debe probar.
    """
    historia = estado["historia"]
    criterios = estado.get("criterios", [])
    lineas = estado.get("lineas_no_cubiertas", [])
    iteracion = estado.get("iteracion", 0)

    cliente = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    contexto_lineas = ""
    if lineas:
        contexto_lineas = f"\nLíneas de código no cubiertas por las pruebas actuales: {lineas}\nPrioriza casos que ejerciten esas líneas."

    prompt = f"""Eres un analista de pruebas de software. Se te da una historia de usuario con sus criterios de aceptación.

Genera una lista de casos de prueba concretos, uno por línea. Cada caso debe:
- Ser específico (qué entrada, qué acción, qué resultado esperado)
- Mencionar explícitamente el criterio de aceptación que valida
- Incluir casos de borde (valores límite, entradas inválidas, estados inesperados)

Responde SOLO con la lista de casos, uno por línea, sin numeración ni explicaciones.

Historia:
{historia}

Criterios de aceptación:
{chr(10).join(criterios)}
{contexto_lineas}"""

    respuesta = cliente.messages.create(
        model=MODELO,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    texto = texto_de_respuesta(respuesta)
    plan = [linea.strip() for linea in texto.splitlines() if linea.strip()]

    print(f"\n[Nodo 2] Iteración {iteracion + 1}. Casos planeados: {len(plan)}")

    return {**estado, "plan": plan}

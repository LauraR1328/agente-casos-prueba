"""Nodo 1: interpreta la historia de usuario y extrae criterios de aceptación."""
import os
import anthropic
from .config import MODELO
from .llm import texto_de_respuesta


def interpretar_historia(estado: dict) -> dict:
    """
    Recibe la historia de usuario en texto plano y devuelve una lista de
    criterios de aceptación estructurados.

    Cada criterio es una cadena con formato 'CAn. <descripción>'.
    """
    historia = estado["historia"]

    cliente = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    prompt = f"""Eres un analista de calidad de software. Se te entrega una historia de usuario.

Tu tarea es extraer los criterios de aceptación, uno por línea, con el formato:
CA1. <descripción>
CA2. <descripción>
...

Solo extrae los criterios. No agregues explicaciones ni texto adicional.
Si la historia ya incluye criterios explícitos, úsalos tal como están.
Si no los incluye, infiere los criterios mínimos necesarios para validar la historia.

Historia de usuario:
{historia}"""

    respuesta = cliente.messages.create(
        model=MODELO,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    texto = texto_de_respuesta(respuesta)
    criterios = [linea.strip() for linea in texto.splitlines() if linea.strip()]

    print(f"\n[Nodo 1] Criterios extraídos: {len(criterios)}")
    for c in criterios:
        print(f"  {c}")

    return {**estado, "criterios": criterios}

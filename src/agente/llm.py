"""Utilidades para leer las respuestas del modelo de Anthropic."""


def texto_de_respuesta(respuesta) -> str:
    """
    Une solo los bloques de tipo 'text' de la respuesta.

    Los modelos recientes pueden devolver bloques de razonamiento ('thinking')
    antes del texto, así que no se puede asumir que content[0] es texto.
    """
    partes = [b.text for b in respuesta.content if getattr(b, "type", None) == "text"]
    return "".join(partes).strip()

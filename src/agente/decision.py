"""Nodo 5 del agente: decide si el ciclo termina o vuelve a la planeación."""
from .config import MAX_ITERACIONES, UMBRAL_COBERTURA

TERMINAR = "terminar"
CONTINUAR = "continuar"


def decidir_siguiente_paso(
    cobertura: float,
    iteracion: int,
    umbral: float = UMBRAL_COBERTURA,
    max_iteraciones: int = MAX_ITERACIONES,
) -> str:
    """Devuelve ``TERMINAR`` o ``CONTINUAR``.

    ``iteracion`` es el número de ciclos de generación ya completados.
    El ciclo termina si la cobertura alcanza el umbral o si se agotó el
    máximo de iteraciones; en cualquier otro caso continúa.
    """
    if not 0 <= cobertura <= 100:
        raise ValueError("La cobertura debe estar entre 0 y 100")
    if iteracion < 0:
        raise ValueError("La iteración no puede ser negativa")
    if cobertura >= umbral or iteracion >= max_iteraciones:
        return TERMINAR
    return CONTINUAR

"""Nodo 5: decide si el ciclo termina o regresa a la planeación."""
from .config import UMBRAL_COBERTURA, MAX_ITERACIONES


def decidir(estado: dict) -> str:
    """
    Evalúa el estado del ciclo y retorna una de dos cadenas que LangGraph
    usa como nombre de la siguiente arista:

    - "continuar": la cobertura no alcanzó el umbral y quedan iteraciones.
    - "terminar": la cobertura alcanzó el umbral o se agotaron las iteraciones.

    Lanza ValueError si los valores requeridos no están presentes o son inválidos.
    """
    cobertura = estado.get("cobertura")
    iteracion = estado.get("iteracion", 0)

    if cobertura is None:
        raise ValueError("El estado no contiene 'cobertura'.")
    if not isinstance(cobertura, (int, float)):
        raise ValueError(f"'cobertura' debe ser numérico, se recibió: {type(cobertura)}")
    if not isinstance(iteracion, int) or iteracion < 0:
        raise ValueError(f"'iteracion' debe ser un entero no negativo, se recibió: {iteracion}")

    if cobertura >= UMBRAL_COBERTURA:
        print(f"[Nodo 5] Cobertura {cobertura:.1f}% ≥ umbral {UMBRAL_COBERTURA}% → terminar")
        return "terminar"

    if iteracion >= MAX_ITERACIONES:
        print(f"[Nodo 5] Iteraciones agotadas ({iteracion}/{MAX_ITERACIONES}) → terminar")
        return "terminar"

    print(f"[Nodo 5] Cobertura {cobertura:.1f}% < umbral {UMBRAL_COBERTURA}%, "
          f"iteración {iteracion}/{MAX_ITERACIONES} → continuar")
    return "continuar"

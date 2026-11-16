"""
Ejecuta el agente sobre una historia de usuario específica.

Uso:
    python -m src.ejecutar_hu HU-01
    python -m src.ejecutar_hu HU-03

Si no se indica historia, ejecuta sobre HU-01 como ejemplo.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from evaluar import HISTORIAS


def main():
    hu_id = sys.argv[1] if len(sys.argv) > 1 else "HU-01"

    if hu_id not in HISTORIAS:
        print(f"Historia '{hu_id}' no encontrada. Disponibles: {list(HISTORIAS.keys())}")
        sys.exit(1)

    historia = HISTORIAS[hu_id]

    # Importar aquí para que el PYTHONPATH ya esté configurado
    from agente.grafo import ejecutar_sobre_historia

    estado = ejecutar_sobre_historia(historia)

    print(f"\nResultado final para {hu_id}:")
    print(f"  Cobertura: {estado.get('cobertura', 0):.1f}%")
    print(f"  Iteraciones realizadas: {estado.get('iteracion', 0)}")
    print(f"  Líneas aún sin cubrir: {estado.get('lineas_no_cubiertas', [])}")


if __name__ == "__main__":
    main()

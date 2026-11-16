"""
Script de evaluación comparativa.

Ejecuta las tres configuraciones sobre las 7 historias de usuario y
guarda los resultados en resultados/comparacion.json.

Uso:
    python -m src.evaluar [--repeticiones N]
"""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Historias de usuario del caso de estudio
HISTORIAS = {
    "HU-01": (
        "Como usuario, quiero crear una tarea con título, descripción opcional y "
        "fecha límite opcional, para organizar mi trabajo. "
        "CA1. La tarea se crea con estado pendiente y un identificador único. "
        "CA2. Si el título está vacío o solo tiene espacios, se rechaza la creación. "
        "CA3. Si el título supera 100 caracteres, se rechaza. "
        "CA4. Si la fecha límite es anterior a hoy, se rechaza. "
        "CA5. Una fecha límite igual a hoy o posterior, o la ausencia de fecha, es válida."
    ),
    "HU-02": (
        "Como usuario, quiero editar el título, la descripción o la fecha límite de una tarea, "
        "para mantener su información al día. "
        "CA1. Los cambios quedan reflejados en la tarea. "
        "CA2. Se aplican las mismas validaciones de título y fecha que al crear. "
        "CA3. Si una validación falla, la tarea no cambia. "
        "CA4. Si la tarea no existe, se informa el error. "
        "CA5. Una tarea terminada no se puede editar."
    ),
    "HU-03": (
        "Como usuario, quiero eliminar una tarea, para quitar lo que ya no es necesario. "
        "CA1. La tarea deja de existir y no aparece en ninguna consulta. "
        "CA2. Las demás tareas no se ven afectadas. "
        "CA3. Si la tarea no existe, se informa el error."
    ),
    "HU-04": (
        "Como usuario, quiero asignar un responsable a una tarea, para saber quién se encarga. "
        "CA1. El nombre queda guardado sin espacios sobrantes. "
        "CA2. Un nombre vacío o de solo espacios se rechaza. "
        "CA3. Reasignar reemplaza al responsable anterior. "
        "CA4. Si la tarea no existe, se informa el error. "
        "CA5. No se puede asignar responsable a una tarea terminada."
    ),
    "HU-05": (
        "Como usuario, quiero cambiar el estado de una tarea, para reflejar su avance. "
        "CA1. Se permiten las transiciones pendiente→en progreso, en progreso→terminada "
        "y en progreso→pendiente. "
        "CA2. No se puede pasar de pendiente a terminada. "
        "CA3. Una tarea terminada no cambia de estado. "
        "CA4. Para pasar a en progreso, la tarea debe tener responsable. "
        "CA5. Un estado desconocido se rechaza. "
        "CA6. Si la tarea no existe, se informa el error."
    ),
    "HU-06": (
        "Como usuario, quiero filtrar las tareas por estado, para ver en qué punto está cada una. "
        "CA1. Devuelve solo las tareas que tienen ese estado. "
        "CA2. Si ninguna coincide, devuelve una lista vacía. "
        "CA3. Un estado desconocido se rechaza."
    ),
    "HU-07": (
        "Como usuario, quiero ver las tareas cuya fecha límite cae dentro de un rango, "
        "para planear mi semana. "
        "CA1. Devuelve las tareas con fecha dentro del rango, incluidos los extremos. "
        "CA2. Las tareas sin fecha límite no aparecen. "
        "CA3. Si la fecha inicial es posterior a la final, se rechaza. "
        "CA4. Si ninguna coincide, devuelve una lista vacía."
    ),
}


def medir_cobertura_base() -> float:
    """Ejecuta solo las pruebas manuales y retorna la cobertura."""
    resultado = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_tareas_manual.py",
         "--cov=gestor_tareas", "--cov-report=json:coverage_base.json", "-q", "--tb=no"],
        capture_output=True, text=True,
    )
    datos = json.loads(Path("coverage_base.json").read_text())
    return round(datos["totals"]["percent_covered"], 2)


def ejecutar_agente_sobre_historia(historia: str) -> dict:
    """Ejecuta el agente completo sobre una historia y retorna métricas."""
    from agente.grafo import ejecutar_sobre_historia
    inicio = time.time()
    estado = ejecutar_sobre_historia(historia)
    duracion = round(time.time() - inicio, 1)
    return {
        "cobertura": estado.get("cobertura", 0),
        "iteraciones": estado.get("iteracion", 0),
        "lineas_no_cubiertas": len(estado.get("lineas_no_cubiertas", [])),
        "duracion_seg": duracion,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeticiones", type=int, default=3)
    args = parser.parse_args()

    Path("resultados").mkdir(exist_ok=True)

    print("\n=== Evaluación comparativa del agente ===\n")
    print(f"Repeticiones por historia: {args.repeticiones}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    # 1. Línea base manual
    print("--- Midiendo línea base manual ---")
    cobertura_manual = medir_cobertura_base()
    print(f"Cobertura manual: {cobertura_manual}%\n")

    # 2. Agente sobre cada historia
    resultados = {
        "fecha": datetime.now().isoformat(),
        "repeticiones": args.repeticiones,
        "cobertura_manual": cobertura_manual,
        "historias": {},
    }

    for hu_id, historia in HISTORIAS.items():
        print(f"\n--- {hu_id} ---")
        repeticiones_hu = []
        for rep in range(1, args.repeticiones + 1):
            print(f"  Repetición {rep}/{args.repeticiones}")
            try:
                metricas = ejecutar_agente_sobre_historia(historia)
                repeticiones_hu.append(metricas)
                print(f"  → Cobertura: {metricas['cobertura']}% en {metricas['iteraciones']} iter.")
            except Exception as e:
                print(f"  → Error: {e}")
                repeticiones_hu.append({"error": str(e)})

        coberturas = [r["cobertura"] for r in repeticiones_hu if "cobertura" in r]
        resultados["historias"][hu_id] = {
            "repeticiones": repeticiones_hu,
            "cobertura_min": min(coberturas) if coberturas else None,
            "cobertura_max": max(coberturas) if coberturas else None,
            "cobertura_media": round(sum(coberturas) / len(coberturas), 2) if coberturas else None,
        }

    # Guardar resultados
    ruta = Path("resultados") / "comparacion.json"
    ruta.write_text(json.dumps(resultados, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nResultados guardados en {ruta}")

    # Resumen final
    print("\n=== Resumen ===")
    print(f"Cobertura manual (línea base): {cobertura_manual}%")
    for hu_id, datos in resultados["historias"].items():
        media = datos.get("cobertura_media")
        rango = f"{datos.get('cobertura_min')}%–{datos.get('cobertura_max')}%"
        print(f"  {hu_id}: media {media}%  rango {rango}")


if __name__ == "__main__":
    main()

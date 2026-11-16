"""Nodo 4: ejecuta pytest con cobertura y devuelve las líneas no cubiertas."""
import json
import subprocess
import sys
import tempfile
import os
from pathlib import Path


def ejecutar_y_medir(estado: dict) -> dict:
    """
    Escribe las pruebas generadas en archivos temporales, ejecuta pytest midiendo
    cobertura de gestor_tareas, y actualiza el estado con cobertura y líneas no cubiertas.
    """
    pruebas_unitarias = estado.get("pruebas_unitarias", "")
    pruebas_funcionales = estado.get("pruebas_funcionales", "")
    iteracion = estado.get("iteracion", 0)

    archivos_temp = []

    # Al empezar una historia se borran las pruebas de corridas anteriores,
    # para que no contaminen la cobertura ni el conteo de pruebas.
    if iteracion == 0:
        for anterior in Path("tests").glob("test_agente_unitario_iter*.py"):
            anterior.unlink()

    # Escribir pruebas unitarias generadas en un archivo temporal dentro de tests/
    if pruebas_unitarias.strip():
        ruta = Path("tests") / f"test_agente_unitario_iter{iteracion}.py"
        ruta.write_text(pruebas_unitarias, encoding="utf-8")
        archivos_temp.append(ruta)
        print(f"[Nodo 4] Escrito: {ruta}")

    # Solo las pruebas generadas para esta historia (no las manuales ni las del nodo 5)
    pruebas_historia = sorted(str(p) for p in Path("tests").glob("test_agente_unitario_iter*.py"))
    if not pruebas_historia:
        print("[Nodo 4] No hay pruebas generadas que ejecutar — retornando 0%")
        return {**estado, "cobertura": 0.0, "lineas_no_cubiertas": [], "iteracion": iteracion + 1}

    resultado = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            *pruebas_historia,
            "--cov=gestor_tareas",
            "--cov-report=json:coverage.json",
            "--cov-report=term-missing",
            "-q",
            "--tb=no",  # sin traceback para mantener la salida limpia
        ],
        capture_output=True,
        text=True,
    )

    print(resultado.stdout[-2000:] if len(resultado.stdout) > 2000 else resultado.stdout)
    if resultado.returncode not in (0, 1):
        # returncode 1 = pruebas fallaron (normal), distinto de errores de sintaxis
        print(f"[Nodo 4] Advertencia: pytest retornó código {resultado.returncode}")
        print(resultado.stderr[-1000:])

    # Leer el JSON generado por coverage.py
    cobertura_path = Path("coverage.json")
    if not cobertura_path.exists():
        print("[Nodo 4] No se encontró coverage.json — retornando 0%")
        return {**estado, "cobertura": 0.0, "lineas_no_cubiertas": [], "iteracion": iteracion + 1}

    with open(cobertura_path, encoding="utf-8") as f:
        datos = json.load(f)

    porcentaje = datos["totals"]["percent_covered"]

    lineas_no_cubiertas = []
    for archivo in datos["files"].values():
        lineas_no_cubiertas.extend(archivo["missing_lines"])

    print(f"\n[Nodo 4] Iteración {iteracion + 1} — Cobertura: {porcentaje:.1f}%")
    print(f"[Nodo 4] Líneas no cubiertas ({len(lineas_no_cubiertas)}): {lineas_no_cubiertas}")

    return {
        **estado,
        "cobertura": round(porcentaje, 2),
        "lineas_no_cubiertas": sorted(set(lineas_no_cubiertas)),
        "iteracion": iteracion + 1,
    }

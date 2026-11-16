"""
Genera casos de prueba para las historias de usuario de la carpeta historias/.

Uso:
    python -m src.generar_casos                 # procesa historias/*.txt
    python -m src.generar_casos carpeta_otra    # procesa otra carpeta

Por cada historia crea casos_generados/<HU>/ con:
    criterios.txt         criterios de aceptación extraídos (nodo 1)
    plan_casos.txt        casos planeados (nodo 2)
    escenarios.feature    escenarios Gherkin (nodo 3a)
    pruebas_unitarias.py  pruebas pytest (nodo 3b, última iteración)
    resumen.txt           cobertura, iteraciones y pruebas que pasan o fallan

Y en casos_generados/ dos archivos para revisar en Excel:
    matriz_casos.csv      una fila por caso planeado
    resumen_general.csv   una fila por historia
"""
import csv
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "casos_generados"
sys.path.insert(0, str(RAIZ / "src"))


def contar_resultados(ruta_pruebas: Path) -> tuple[int, int]:
    """Ejecuta pytest sobre el archivo generado y devuelve (pasan, fallan)."""
    if not ruta_pruebas.exists() or not ruta_pruebas.read_text(encoding="utf-8").strip():
        return 0, 0
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", str(ruta_pruebas), "-q", "-p", "no:cacheprovider"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=RAIZ,
    )
    lineas = [l for l in proc.stdout.splitlines() if l.strip()]
    ultima = lineas[-1] if lineas else ""
    pasan = re.search(r"(\d+) passed", ultima)
    fallan = re.search(r"(\d+) failed", ultima)
    errores = re.search(r"(\d+) error", ultima)
    total_fallos = (int(fallan.group(1)) if fallan else 0) + (int(errores.group(1)) if errores else 0)
    return (int(pasan.group(1)) if pasan else 0), total_fallos


def guardar_caso(hu_id: str, estado: dict) -> dict:
    """Escribe los artefactos de una historia y devuelve su fila de resumen."""
    carpeta = SALIDA / hu_id
    carpeta.mkdir(parents=True, exist_ok=True)

    criterios = estado.get("criterios", [])
    plan = estado.get("plan", [])
    (carpeta / "criterios.txt").write_text("\n".join(criterios) + "\n", encoding="utf-8")
    (carpeta / "plan_casos.txt").write_text(
        "\n".join(f"{i}. {c}" for i, c in enumerate(plan, 1)) + "\n", encoding="utf-8"
    )
    (carpeta / "escenarios.feature").write_text(
        estado.get("pruebas_funcionales", "") + "\n", encoding="utf-8"
    )
    ruta_py = carpeta / "pruebas_unitarias.py"
    ruta_py.write_text(estado.get("pruebas_unitarias", ""), encoding="utf-8")

    pasan, fallan = contar_resultados(ruta_py)
    cobertura = float(estado.get("cobertura") or 0.0)
    iteraciones = estado.get("iteracion", 0)
    (carpeta / "resumen.txt").write_text(
        f"Historia: {hu_id}\n"
        f"Criterios de aceptación: {len(criterios)}\n"
        f"Casos planeados: {len(plan)}\n"
        f"Iteraciones: {iteraciones}\n"
        f"Cobertura de líneas: {cobertura:.1f}%\n"
        f"Pruebas unitarias que pasan: {pasan}\n"
        f"Pruebas unitarias que fallan: {fallan}\n"
        "Nota: las pruebas que fallan deben revisarse manualmente; "
        "pueden reflejar un comportamiento que el sistema no implementa.\n",
        encoding="utf-8",
    )
    return {
        "historia": hu_id,
        "criterios": len(criterios),
        "casos_planeados": len(plan),
        "iteraciones": iteraciones,
        "cobertura_%": round(cobertura, 1),
        "pruebas_pasan": pasan,
        "pruebas_fallan": fallan,
    }


def escribir_csv(ruta: Path, filas: list[dict]) -> None:
    if not filas:
        return
    # utf-8-sig para que Excel muestre bien las tildes
    with ruta.open("w", encoding="utf-8-sig", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        escritor.writeheader()
        escritor.writerows(filas)


def main():
    from agente.grafo import ejecutar_sobre_historia

    entrada = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "historias"
    archivos = sorted(entrada.glob("*.txt"))
    if not archivos:
        print(f"No hay archivos .txt en {entrada}. Coloca ahí una historia por archivo.")
        sys.exit(1)

    SALIDA.mkdir(exist_ok=True)
    resumenes, matriz = [], []
    for archivo in archivos:
        hu_id = archivo.stem
        historia = archivo.read_text(encoding="utf-8").strip()
        print(f"\n########## Procesando {hu_id} ##########")
        estado = ejecutar_sobre_historia(historia)
        resumenes.append(guardar_caso(hu_id, estado))
        for i, caso in enumerate(estado.get("plan", []), 1):
            matriz.append({"id": f"{hu_id}-CP{i:02d}", "historia": hu_id, "caso_planeado": caso})

    escribir_csv(SALIDA / "matriz_casos.csv", matriz)
    escribir_csv(SALIDA / "resumen_general.csv", resumenes)
    print(f"\nListo. Resultados en {SALIDA}")


if __name__ == "__main__":
    main()

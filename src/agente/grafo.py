"""Grafo principal del agente en LangGraph."""
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional

from .nodo_interpretar import interpretar_historia
from .nodo_planear import planear_casos
from .nodo_generar_funcional import generar_pruebas_funcionales
from .nodo_generar_unitario import generar_pruebas_unitarias
from .nodo_ejecutar import ejecutar_y_medir
from .decision import decidir


# LangGraph requiere un TypedDict para el estado
class EstadoGrafo(TypedDict, total=False):
    historia: str
    criterios: list
    plan: list
    pruebas_funcionales: str
    pruebas_unitarias: str
    cobertura: Optional[float]
    lineas_no_cubiertas: list
    iteracion: int


def construir_grafo() -> StateGraph:
    """
    Construye y compila el grafo de estados del agente.

    Flujo:
        interpretar → planear → generar_funcional → generar_unitario
            → ejecutar → [decidir] → terminar o volver a planear
    """
    grafo = StateGraph(EstadoGrafo)

    # Registrar nodos
    grafo.add_node("interpretar", interpretar_historia)
    grafo.add_node("planear", planear_casos)
    grafo.add_node("generar_funcional", generar_pruebas_funcionales)
    grafo.add_node("generar_unitario", generar_pruebas_unitarias)
    grafo.add_node("ejecutar", ejecutar_y_medir)

    # Aristas fijas
    grafo.set_entry_point("interpretar")
    grafo.add_edge("interpretar", "planear")
    grafo.add_edge("planear", "generar_funcional")
    grafo.add_edge("generar_funcional", "generar_unitario")
    grafo.add_edge("generar_unitario", "ejecutar")

    # Arista condicional del nodo 5
    grafo.add_conditional_edges(
        "ejecutar",
        decidir,
        {
            "continuar": "planear",   # regresa al nodo 2 con líneas no cubiertas
            "terminar": END,
        },
    )

    return grafo.compile()


def ejecutar_sobre_historia(historia: str) -> dict:
    """
    Punto de entrada principal. Ejecuta el agente completo sobre una historia
    de usuario y retorna el estado final con la cobertura alcanzada.
    """
    agente = construir_grafo()

    estado_inicial = {
        "historia": historia,
        "criterios": [],
        "plan": [],
        "pruebas_funcionales": "",
        "pruebas_unitarias": "",
        "cobertura": None,
        "lineas_no_cubiertas": [],
        "iteracion": 0,
    }

    print(f"\n{'='*60}")
    print(f"Agente iniciado para historia:")
    print(f"  {historia[:100]}{'...' if len(historia) > 100 else ''}")
    print(f"{'='*60}")

    estado_final = agente.invoke(estado_inicial)

    print(f"\n{'='*60}")
    print(f"Agente finalizado.")
    print(f"  Cobertura final: {estado_final.get('cobertura', 0):.1f}%")
    print(f"  Iteraciones: {estado_final.get('iteracion', 0)}")
    print(f"  Líneas sin cubrir: {len(estado_final.get('lineas_no_cubiertas', []))}")
    print(f"{'='*60}\n")

    return estado_final

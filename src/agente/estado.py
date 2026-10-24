"""Estado que viaja entre los nodos del agente."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class EstadoAgente:
    historia: str
    criterios: list[str] = field(default_factory=list)
    plan: list[str] = field(default_factory=list)
    pruebas_funcionales: str = ""
    pruebas_unitarias: str = ""
    cobertura: Optional[float] = None
    lineas_no_cubiertas: list[int] = field(default_factory=list)
    iteracion: int = 0

"""Sistema de gestión de tareas en memoria — caso de estudio del trabajo de grado."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Callable, Optional

from .excepciones import ErrorValidacion, TareaNoEncontrada, OperacionNoPermitida

TITULO_MAX = 100

TRANSICIONES_VALIDAS = {
    "pendiente": {"en_progreso"},
    "en_progreso": {"terminada", "pendiente"},
    "terminada": set(),
}


class EstadoTarea(str, Enum):
    PENDIENTE = "pendiente"
    EN_PROGRESO = "en_progreso"
    TERMINADA = "terminada"


@dataclass
class Tarea:
    id: int
    titulo: str
    descripcion: str = ""
    fecha_limite: Optional[date] = None
    estado: EstadoTarea = EstadoTarea.PENDIENTE
    responsable: Optional[str] = None


class GestorTareas:
    """Gestiona tareas en memoria. `hoy` es un callable que retorna la fecha actual
    (inyección de dependencia para facilitar las pruebas)."""

    def __init__(self, hoy: Callable[[], date] = date.today):
        self._tareas: dict[int, Tarea] = {}
        self._siguiente_id: int = 1
        self._hoy = hoy

    # ------------------------------------------------------------------ crear
    def crear_tarea(
        self,
        titulo: str,
        descripcion: str = "",
        fecha_limite: Optional[date] = None,
    ) -> Tarea:
        """HU-01: crea una tarea nueva con estado pendiente."""
        self._validar_titulo(titulo)
        self._validar_fecha(fecha_limite)

        tarea = Tarea(
            id=self._siguiente_id,
            titulo=titulo.strip(),
            descripcion=descripcion,
            fecha_limite=fecha_limite,
        )
        self._tareas[self._siguiente_id] = tarea
        self._siguiente_id += 1
        return tarea

    # ------------------------------------------------------------------ editar
    def editar_tarea(
        self,
        id_tarea: int,
        titulo: Optional[str] = None,
        descripcion: Optional[str] = None,
        fecha_limite: Optional[date] = None,
    ) -> Tarea:
        """HU-02: edita el título, descripción o fecha límite de una tarea."""
        tarea = self._obtener_o_lanzar(id_tarea)
        if tarea.estado == EstadoTarea.TERMINADA:
            raise OperacionNoPermitida("No se puede editar una tarea terminada.")

        if titulo is not None:
            self._validar_titulo(titulo)
            tarea.titulo = titulo.strip()
        if descripcion is not None:
            tarea.descripcion = descripcion
        if fecha_limite is not None:
            self._validar_fecha(fecha_limite)
            tarea.fecha_limite = fecha_limite

        return tarea

    # ------------------------------------------------------------------ eliminar
    def eliminar_tarea(self, id_tarea: int) -> None:
        """HU-03: elimina la tarea; lanza TareaNoEncontrada si no existe."""
        self._obtener_o_lanzar(id_tarea)
        del self._tareas[id_tarea]

    # ------------------------------------------------------------------ responsable
    def asignar_responsable(self, id_tarea: int, nombre: str) -> Tarea:
        """HU-04: asigna un responsable a la tarea."""
        tarea = self._obtener_o_lanzar(id_tarea)
        if tarea.estado == EstadoTarea.TERMINADA:
            raise OperacionNoPermitida("No se puede asignar responsable a una tarea terminada.")
        if not nombre or not nombre.strip():
            raise ErrorValidacion("El nombre del responsable no puede estar vacío.")
        tarea.responsable = nombre.strip()
        return tarea

    # ------------------------------------------------------------------ estado
    def cambiar_estado(self, id_tarea: int, nuevo_estado: str) -> Tarea:
        """HU-05: cambia el estado de la tarea según las transiciones permitidas."""
        tarea = self._obtener_o_lanzar(id_tarea)

        estados_validos = {e.value for e in EstadoTarea}
        if nuevo_estado not in estados_validos:
            raise ErrorValidacion(f"Estado desconocido: '{nuevo_estado}'.")

        estado_actual = tarea.estado.value
        if nuevo_estado not in TRANSICIONES_VALIDAS.get(estado_actual, set()):
            raise OperacionNoPermitida(
                f"No se puede pasar de '{estado_actual}' a '{nuevo_estado}'."
            )

        if nuevo_estado == EstadoTarea.EN_PROGRESO.value and not tarea.responsable:
            raise OperacionNoPermitida(
                "Para pasar a 'en progreso' la tarea debe tener responsable."
            )

        tarea.estado = EstadoTarea(nuevo_estado)
        return tarea

    # ------------------------------------------------------------------ filtrar
    def filtrar_por_estado(self, estado: str) -> list[Tarea]:
        """HU-06: retorna las tareas con el estado indicado."""
        estados_validos = {e.value for e in EstadoTarea}
        if estado not in estados_validos:
            raise ErrorValidacion(f"Estado desconocido: '{estado}'.")
        return [t for t in self._tareas.values() if t.estado.value == estado]

    def filtrar_por_fecha(self, desde: date, hasta: date) -> list[Tarea]:
        """HU-07: retorna las tareas cuya fecha límite cae dentro del rango."""
        if desde > hasta:
            raise ErrorValidacion(
                f"La fecha inicial ({desde}) no puede ser posterior a la final ({hasta})."
            )
        return [
            t for t in self._tareas.values()
            if t.fecha_limite is not None and desde <= t.fecha_limite <= hasta
        ]

    # ------------------------------------------------------------------ consulta
    def obtener_tarea(self, id_tarea: int) -> Tarea:
        """Retorna la tarea o lanza TareaNoEncontrada."""
        return self._obtener_o_lanzar(id_tarea)

    def listar_tareas(self) -> list[Tarea]:
        """Retorna todas las tareas."""
        return list(self._tareas.values())

    # ------------------------------------------------------------------ privados
    def _obtener_o_lanzar(self, id_tarea: int) -> Tarea:
        tarea = self._tareas.get(id_tarea)
        if tarea is None:
            raise TareaNoEncontrada(f"No existe la tarea con id {id_tarea}.")
        return tarea

    def _validar_titulo(self, titulo: str) -> None:
        if not titulo or not titulo.strip():
            raise ErrorValidacion("El título no puede estar vacío.")
        if len(titulo.strip()) > TITULO_MAX:
            raise ErrorValidacion(
                f"El título supera los {TITULO_MAX} caracteres permitidos."
            )

    def _validar_fecha(self, fecha: Optional[date]) -> None:
        if fecha is not None and fecha < self._hoy():
            raise ErrorValidacion(
                f"La fecha límite ({fecha}) no puede ser anterior a hoy ({self._hoy()})."
            )

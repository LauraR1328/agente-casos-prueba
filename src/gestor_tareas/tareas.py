"""Sistema de gestión de tareas usado como caso de estudio.

Las reglas de negocio de este módulo están descritas en las historias de
usuario HU-01 a HU-07 del documento. El agente de generación de pruebas toma
esas historias como insumo; este código es el sistema bajo prueba.
"""
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Callable, Optional, Union

LONGITUD_MAXIMA_TITULO = 100


class EstadoTarea(str, Enum):
    PENDIENTE = "pendiente"
    EN_PROGRESO = "en_progreso"
    TERMINADA = "terminada"


class ErrorTareas(Exception):
    """Error base del sistema de tareas."""


class ErrorValidacion(ErrorTareas):
    """Un dato de entrada no cumple las reglas de validación."""


class TareaNoEncontrada(ErrorTareas):
    """No existe una tarea con el identificador indicado."""


class OperacionNoPermitida(ErrorTareas):
    """La operación no es válida para el estado actual de la tarea."""


@dataclass
class Tarea:
    id: int
    titulo: str
    descripcion: str = ""
    fecha_limite: Optional[date] = None
    responsable: Optional[str] = None
    estado: EstadoTarea = EstadoTarea.PENDIENTE


# Transiciones de estado permitidas
_TRANSICIONES = {
    EstadoTarea.PENDIENTE: {EstadoTarea.EN_PROGRESO},
    EstadoTarea.EN_PROGRESO: {EstadoTarea.PENDIENTE, EstadoTarea.TERMINADA},
    EstadoTarea.TERMINADA: set(),
}


class GestorTareas:
    """Administra tareas en memoria.

    El parámetro ``hoy`` permite inyectar la fecha actual, de modo que las
    pruebas no dependan del reloj del sistema.
    """

    def __init__(self, hoy: Callable[[], date] = date.today):
        self._hoy = hoy
        self._tareas: dict[int, Tarea] = {}
        self._siguiente_id = 1

    # ---------- validaciones internas ----------
    def _validar_titulo(self, titulo: str) -> str:
        if titulo is None or not titulo.strip():
            raise ErrorValidacion("El título no puede estar vacío")
        titulo = titulo.strip()
        if len(titulo) > LONGITUD_MAXIMA_TITULO:
            raise ErrorValidacion(
                f"El título no puede superar {LONGITUD_MAXIMA_TITULO} caracteres"
            )
        return titulo

    def _validar_fecha_limite(self, fecha_limite: Optional[date]) -> None:
        if fecha_limite is not None and fecha_limite < self._hoy():
            raise ErrorValidacion("La fecha límite no puede ser anterior a hoy")

    def _convertir_estado(self, estado: Union[str, EstadoTarea]) -> EstadoTarea:
        try:
            return EstadoTarea(estado)
        except ValueError:
            raise ErrorValidacion(f"Estado desconocido: {estado!r}")

    # ---------- HU-01 ----------
    def crear_tarea(
        self,
        titulo: str,
        descripcion: str = "",
        fecha_limite: Optional[date] = None,
    ) -> Tarea:
        titulo = self._validar_titulo(titulo)
        self._validar_fecha_limite(fecha_limite)
        tarea = Tarea(
            id=self._siguiente_id,
            titulo=titulo,
            descripcion=descripcion,
            fecha_limite=fecha_limite,
        )
        self._tareas[tarea.id] = tarea
        self._siguiente_id += 1
        return tarea

    def obtener_tarea(self, id_tarea: int) -> Tarea:
        if id_tarea not in self._tareas:
            raise TareaNoEncontrada(f"No existe la tarea {id_tarea}")
        return self._tareas[id_tarea]

    # ---------- HU-02 ----------
    def editar_tarea(
        self,
        id_tarea: int,
        titulo: Optional[str] = None,
        descripcion: Optional[str] = None,
        fecha_limite: Optional[date] = None,
    ) -> Tarea:
        """Edita los campos recibidos; los que llegan como None no cambian."""
        tarea = self.obtener_tarea(id_tarea)
        if tarea.estado == EstadoTarea.TERMINADA:
            raise OperacionNoPermitida("Una tarea terminada no se puede editar")
        # Se valida todo antes de modificar, para no dejar cambios a medias
        if titulo is not None:
            titulo = self._validar_titulo(titulo)
        self._validar_fecha_limite(fecha_limite)
        if titulo is not None:
            tarea.titulo = titulo
        if descripcion is not None:
            tarea.descripcion = descripcion
        if fecha_limite is not None:
            tarea.fecha_limite = fecha_limite
        return tarea

    # ---------- HU-03 ----------
    def eliminar_tarea(self, id_tarea: int) -> None:
        self.obtener_tarea(id_tarea)
        del self._tareas[id_tarea]

    # ---------- HU-04 ----------
    def asignar_responsable(self, id_tarea: int, responsable: str) -> Tarea:
        tarea = self.obtener_tarea(id_tarea)
        if tarea.estado == EstadoTarea.TERMINADA:
            raise OperacionNoPermitida(
                "No se puede asignar responsable a una tarea terminada"
            )
        if responsable is None or not responsable.strip():
            raise ErrorValidacion("El responsable no puede estar vacío")
        tarea.responsable = responsable.strip()
        return tarea

    # ---------- HU-05 ----------
    def cambiar_estado(
        self, id_tarea: int, nuevo_estado: Union[str, EstadoTarea]
    ) -> Tarea:
        tarea = self.obtener_tarea(id_tarea)
        nuevo_estado = self._convertir_estado(nuevo_estado)
        if nuevo_estado not in _TRANSICIONES[tarea.estado]:
            raise OperacionNoPermitida(
                f"No se puede pasar de {tarea.estado.value} a {nuevo_estado.value}"
            )
        if nuevo_estado == EstadoTarea.EN_PROGRESO and not tarea.responsable:
            raise OperacionNoPermitida(
                "Para iniciar una tarea debe tener un responsable asignado"
            )
        tarea.estado = nuevo_estado
        return tarea

    # ---------- HU-06 ----------
    def filtrar_por_estado(self, estado: Union[str, EstadoTarea]) -> list[Tarea]:
        estado = self._convertir_estado(estado)
        return [t for t in self._tareas.values() if t.estado == estado]

    # ---------- HU-07 ----------
    def filtrar_por_fecha(self, desde: date, hasta: date) -> list[Tarea]:
        """Tareas cuya fecha límite está entre ``desde`` y ``hasta`` (inclusive)."""
        if desde > hasta:
            raise ErrorValidacion("La fecha inicial no puede ser posterior a la final")
        return [
            t
            for t in self._tareas.values()
            if t.fecha_limite is not None and desde <= t.fecha_limite <= hasta
        ]

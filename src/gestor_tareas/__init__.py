"""Gestor de tareas en memoria — sistema bajo prueba del trabajo de grado."""
from .tareas import GestorTareas, Tarea, EstadoTarea
from .excepciones import ErrorValidacion, TareaNoEncontrada, OperacionNoPermitida

__all__ = [
    "GestorTareas",
    "Tarea",
    "EstadoTarea",
    "ErrorValidacion",
    "TareaNoEncontrada",
    "OperacionNoPermitida",
]

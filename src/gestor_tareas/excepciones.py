"""Excepciones del gestor de tareas."""


class ErrorValidacion(Exception):
    """Se lanza cuando una entrada no cumple las reglas de negocio."""


class TareaNoEncontrada(Exception):
    """Se lanza cuando se referencia una tarea que no existe."""


class OperacionNoPermitida(Exception):
    """Se lanza cuando la transición de estado o la operación no está permitida."""

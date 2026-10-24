"""Pruebas escritas a mano: punto de partida de la línea base.

Cubren solo parte de los criterios de aceptación a propósito. Sirven para
medir la cobertura inicial y para comparar después con lo que genere el agente.
"""
from datetime import date

import pytest

from gestor_tareas import (
    GestorTareas,
    EstadoTarea,
    ErrorValidacion,
    TareaNoEncontrada,
    OperacionNoPermitida,
)

HOY = date(2026, 10, 20)


@pytest.fixture
def gestor():
    return GestorTareas(hoy=lambda: HOY)


def test_crear_tarea_queda_pendiente(gestor):
    tarea = gestor.crear_tarea("Preparar entrega")
    assert tarea.estado == EstadoTarea.PENDIENTE
    assert tarea.id == 1


def test_crear_tarea_con_titulo_vacio_se_rechaza(gestor):
    with pytest.raises(ErrorValidacion):
        gestor.crear_tarea("   ")


def test_crear_tarea_con_fecha_pasada_se_rechaza(gestor):
    with pytest.raises(ErrorValidacion):
        gestor.crear_tarea("Informe", fecha_limite=date(2026, 10, 19))


def test_eliminar_tarea_inexistente_falla(gestor):
    with pytest.raises(TareaNoEncontrada):
        gestor.eliminar_tarea(99)


def test_asignar_responsable(gestor):
    tarea = gestor.crear_tarea("Revisar código")
    gestor.asignar_responsable(tarea.id, "Laura")
    assert gestor.obtener_tarea(tarea.id).responsable == "Laura"


def test_no_se_puede_pasar_de_pendiente_a_terminada(gestor):
    tarea = gestor.crear_tarea("Desplegar")
    with pytest.raises(OperacionNoPermitida):
        gestor.cambiar_estado(tarea.id, "terminada")


def test_filtrar_por_estado_devuelve_solo_las_del_estado(gestor):
    a = gestor.crear_tarea("A")
    gestor.crear_tarea("B")
    gestor.asignar_responsable(a.id, "Laura")
    gestor.cambiar_estado(a.id, "en_progreso")
    resultado = gestor.filtrar_por_estado("en_progreso")
    assert [t.id for t in resultado] == [a.id]

"""Pruebas del nodo 5: regla de decisión del ciclo (no requiere API)."""
import pytest
from agente.decision import decidir


def test_cobertura_sobre_umbral_termina():
    assert decidir({"cobertura": 85.0, "iteracion": 1}) == "terminar"


def test_cobertura_igual_al_umbral_termina():
    assert decidir({"cobertura": 80.0, "iteracion": 1}) == "terminar"


def test_cobertura_bajo_umbral_con_iteraciones_continua():
    assert decidir({"cobertura": 72.0, "iteracion": 1}) == "continuar"


def test_iteraciones_agotadas_termina():
    assert decidir({"cobertura": 72.0, "iteracion": 3}) == "terminar"


def test_sin_cobertura_lanza_error():
    with pytest.raises(ValueError):
        decidir({"iteracion": 0})


def test_cobertura_invalida_lanza_error():
    with pytest.raises(ValueError):
        decidir({"cobertura": "alto", "iteracion": 0})

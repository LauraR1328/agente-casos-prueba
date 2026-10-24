import pytest

from agente.decision import CONTINUAR, TERMINAR, decidir_siguiente_paso


def test_termina_si_la_cobertura_alcanza_el_umbral():
    assert decidir_siguiente_paso(cobertura=85, iteracion=1) == TERMINAR


def test_termina_justo_en_el_umbral():
    assert decidir_siguiente_paso(cobertura=80, iteracion=1) == TERMINAR


def test_continua_si_esta_bajo_el_umbral_y_quedan_iteraciones():
    assert decidir_siguiente_paso(cobertura=60, iteracion=1) == CONTINUAR


def test_termina_si_se_agotan_las_iteraciones_aunque_no_llegue_al_umbral():
    assert decidir_siguiente_paso(cobertura=60, iteracion=3) == TERMINAR


def test_rechaza_cobertura_fuera_de_rango():
    with pytest.raises(ValueError):
        decidir_siguiente_paso(cobertura=120, iteracion=1)


def test_rechaza_iteracion_negativa():
    with pytest.raises(ValueError):
        decidir_siguiente_paso(cobertura=50, iteracion=-1)

"""Parámetros del ciclo de retroalimentación por cobertura."""

# Cobertura de líneas (en porcentaje) a partir de la cual el agente se detiene.
UMBRAL_COBERTURA = 80.0

# Máximo de ciclos de generación por historia de usuario. Limita el costo de
# las llamadas al modelo y evita ciclos indefinidos.
MAX_ITERACIONES = 3

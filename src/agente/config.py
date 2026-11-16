"""Parámetros del ciclo de retroalimentación por cobertura."""
from pathlib import Path
from dotenv import load_dotenv

# Carga la API key desde el archivo .env de la raíz del proyecto.
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

# Cobertura de líneas (en porcentaje) a partir de la cual el agente se detiene.
UMBRAL_COBERTURA = 80.0

# Máximo de ciclos de generación por historia de usuario. Limita el costo de
# las llamadas al modelo y evita ciclos indefinidos.
MAX_ITERACIONES = 3

# Modelo de Anthropic que usan los nodos con LLM.
# claude-haiku-5-5 es rápido y económico; suficiente para generar pruebas.
MODELO = "claude-haiku-5-5"

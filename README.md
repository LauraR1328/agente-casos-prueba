# Agente de IA para la Generación Híbrida de Casos de Prueba

Trabajo de grado — Ingeniería de Software  
Politécnico Grancolombiano — Grupo E-TIC  
Autora: Laura Natalia Ruiz Jimenez  
Asesor: Wilson Eduardo Soto Forero

---

## Qué hace este proyecto

Un agente de inteligencia artificial que recibe una historia de usuario en lenguaje natural y genera casos de prueba funcionales (Gherkin/BDD) y unitarios (pytest). El agente mide la cobertura de código después de cada ronda de generación y repite el ciclo si no alcanzó el 80%, hasta un máximo de 3 iteraciones.

## Estructura del proyecto

```
agente-casos-prueba/
├── src/
│   ├── agente/
│   │   ├── config.py               # Parámetros del ciclo (umbral, iteraciones, modelo)
│   │   ├── estado.py               # Dataclass con los campos del estado del agente
│   │   ├── grafo.py                # Grafo LangGraph con los 5 nodos y el ciclo
│   │   ├── nodo_interpretar.py     # Nodo 1: extrae criterios de aceptación
│   │   ├── nodo_planear.py         # Nodo 2: planea casos de prueba
│   │   ├── nodo_generar_funcional.py  # Nodo 3a: genera escenarios Gherkin
│   │   ├── nodo_generar_unitario.py   # Nodo 3b: genera funciones pytest
│   │   ├── nodo_ejecutar.py        # Nodo 4: ejecuta pytest y mide cobertura
│   │   └── decision.py             # Nodo 5: decide si continuar o terminar
│   ├── gestor_tareas/
│   │   ├── tareas.py               # Sistema bajo prueba (caso de estudio)
│   │   ├── excepciones.py          # Excepciones del dominio
│   │   └── __init__.py
│   ├── ejecutar_hu.py              # Ejecuta el agente sobre una historia específica
│   └── evaluar.py                  # Evaluación comparativa de las 3 configuraciones
├── tests/
│   ├── test_tareas_manual.py       # Pruebas manuales (línea base)
│   └── agente/
│       └── test_decision.py        # Pruebas del nodo 5 (sin API)
├── docs/                           # Documentos del trabajo de grado
├── resultados/                     # Archivos JSON con métricas de cada corrida
├── .env                            # API key (NO se sube a GitHub)
├── .gitignore
├── pytest.ini
└── requirements.txt
```

## Requisitos

- Python 3.11 o superior
- Cuenta en Anthropic con crédito (console.anthropic.com)

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/LauraR1328/agente-casos-prueba.git
cd agente-casos-prueba

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Crear el archivo .env con la API key
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

## Uso

### Ejecutar el agente sobre una historia

```bash
# Desde la raíz del proyecto
python -m src.ejecutar_hu HU-01
python -m src.ejecutar_hu HU-03
```

### Correr solo las pruebas manuales (línea base)

```bash
pytest tests/test_tareas_manual.py --cov=gestor_tareas --cov-report=term-missing
```

### Correr todas las pruebas incluyendo las del agente

```bash
pytest
```

### Evaluación comparativa completa (3 repeticiones por historia)

```bash
python -m src.evaluar --repeticiones 3
```

Los resultados se guardan en `resultados/comparacion.json`.

## Parámetros configurables

Todos están en `src/agente/config.py`:

| Parámetro | Valor por defecto | Descripción |
|-----------|------------------|-------------|
| `UMBRAL_COBERTURA` | 80.0 | Porcentaje mínimo para detener el ciclo |
| `MAX_ITERACIONES` | 3 | Máximo de rondas de generación por historia |
| `MODELO` | claude-3-5-haiku-20241022 | Modelo de Anthropic que usan los nodos con LLM |

## Metodología

El trabajo sigue Design Science Research (Peffers et al., 2007). El agente se modela como un grafo de estados de 5 nodos implementado con LangGraph:

1. **Interpretar** — extrae criterios de aceptación de la historia
2. **Planear** — define casos de prueba concretos
3a. **Generar funcional** — produce escenarios Gherkin
3b. **Generar unitario** — produce funciones pytest
4. **Ejecutar** — corre pytest y mide cobertura con coverage.py
5. **Decidir** — termina si cobertura ≥ umbral o iteraciones agotadas; si no, regresa al nodo 2

Los nodos 1, 2, 3a y 3b usan el modelo de lenguaje. Los nodos 4 y 5 son deterministas.

## Versiones

- `v0.1` — Entrega 1 (24 oct 2026): arquitectura, caso de estudio, línea base manual
- `v0.2` — Entrega 2 (11 nov 2026): agente completo con los 5 nodos

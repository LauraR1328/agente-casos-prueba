# Agente de IA para la generación híbrida de casos de prueba

Trabajo de grado de Ingeniería de Software, Politécnico Grancolombiano (grupo E-TIC).

El objetivo es un agente que reciba historias de usuario en lenguaje natural y genere pruebas funcionales (Gherkin) y unitarias (pytest), usando la cobertura de código como retroalimentación para decidir si debe seguir generando.

## Estado del proyecto (Entrega 1)

| Componente | Estado |
|---|---|
| Caso de estudio: gestor de tareas (`src/gestor_tareas`) | Listo |
| Historias de usuario con criterios de aceptación (`docs/historias_de_usuario.md`) | Listas |
| Arquitectura del agente (`docs/arquitectura_agente.png`) | Diseñada |
| Línea base: 7 pruebas manuales (`tests/test_tareas_manual.py`) | Cobertura inicial 68% (líneas y ramas) |
| Configuración, estado y regla de decisión del agente (`src/agente`) | Listos y con pruebas |
| Nodos que usan el modelo de lenguaje | Pendiente (Entrega 2) |

## Estructura

```
src/gestor_tareas/   sistema bajo prueba
src/agente/          configuración, estado y nodo de decisión del agente
tests/               pruebas manuales (línea base) y pruebas del agente
docs/                historias de usuario y diagrama de la arquitectura
```

## Cómo correrlo (Windows, PowerShell)

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest --cov=gestor_tareas --cov-branch --cov-report=term-missing
```

La cobertura se mide solo sobre `gestor_tareas`. Las pruebas del agente se ejecutan en la misma corrida y no cambian ese porcentaje.

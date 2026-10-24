# Historias de usuario del caso de estudio

Sistema de gestión de tareas. Estas historias son la especificación de
`src/gestor_tareas/tareas.py` y el insumo del agente generador de pruebas.

## HU-01 Crear tarea
Como usuario, quiero crear una tarea con título, descripción opcional y fecha límite opcional, para organizar mi trabajo.

- CA1. La tarea se crea con estado pendiente y un identificador único.
- CA2. Si el título está vacío o solo tiene espacios, se rechaza la creación.
- CA3. Si el título supera 100 caracteres, se rechaza.
- CA4. Si la fecha límite es anterior a hoy, se rechaza.
- CA5. Una fecha límite igual a hoy o posterior, o la ausencia de fecha, es válida.

## HU-02 Editar tarea
Como usuario, quiero editar el título, la descripción o la fecha límite de una tarea, para mantener su información al día.

- CA1. Los cambios quedan reflejados en la tarea.
- CA2. Se aplican las mismas validaciones de título y fecha que al crear.
- CA3. Si una validación falla, la tarea no cambia.
- CA4. Si la tarea no existe, se informa el error.
- CA5. Una tarea terminada no se puede editar.

## HU-03 Eliminar tarea
Como usuario, quiero eliminar una tarea, para quitar lo que ya no es necesario.

- CA1. La tarea deja de existir y no aparece en ninguna consulta.
- CA2. Las demás tareas no se ven afectadas.
- CA3. Si la tarea no existe, se informa el error.

## HU-04 Asignar responsable
Como usuario, quiero asignar un responsable a una tarea, para saber quién se encarga de ella.

- CA1. El nombre queda guardado sin espacios sobrantes.
- CA2. Un nombre vacío o de solo espacios se rechaza.
- CA3. Reasignar reemplaza al responsable anterior.
- CA4. Si la tarea no existe, se informa el error.
- CA5. No se puede asignar responsable a una tarea terminada.

## HU-05 Cambiar estado
Como usuario, quiero cambiar el estado de una tarea, para reflejar su avance.

- CA1. Se permiten las transiciones pendiente a en progreso, en progreso a terminada y en progreso a pendiente.
- CA2. No se puede pasar de pendiente a terminada.
- CA3. Una tarea terminada no cambia de estado.
- CA4. Para pasar a en progreso, la tarea debe tener responsable.
- CA5. Un estado desconocido se rechaza.
- CA6. Si la tarea no existe, se informa el error.

## HU-06 Filtrar por estado
Como usuario, quiero filtrar las tareas por estado, para ver en qué punto está cada una.

- CA1. Devuelve solo las tareas que tienen ese estado.
- CA2. Si ninguna coincide, devuelve una lista vacía.
- CA3. Un estado desconocido se rechaza.

## HU-07 Filtrar por fecha límite
Como usuario, quiero ver las tareas cuya fecha límite cae dentro de un rango, para planear mi semana.

- CA1. Devuelve las tareas con fecha dentro del rango, incluidos los extremos.
- CA2. Las tareas sin fecha límite no aparecen.
- CA3. Si la fecha inicial es posterior a la final, se rechaza.
- CA4. Si ninguna coincide, devuelve una lista vacía.

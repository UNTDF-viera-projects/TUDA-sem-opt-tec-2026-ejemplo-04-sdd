# Research: Cancelar inscripción propia

**Fecha**: 2026-10-16 | **Feature**: `specs/001-cancelar-inscripcion/spec.md`

Todas las incógnitas del Technical Context quedaron resueltas con el código
existente (`activities/services.py`, `views.py`, `models.py`,
`tests/test_base.py`) y la sesión de clarificación del 2026-10-16. Sin
`NEEDS CLARIFICATION` pendientes.

## Decisión 1: Modelado de la cancelación con estado en Registration

- **Decision**: Agregar a `Registration` el estado (activa / cancelada) y el
  momento de cancelación (nulo mientras está activa). La disponibilidad cuenta
  solo inscripciones activas; la unicidad (estudiante, actividad) se mantiene
  intacta.
- **Rationale**: Conserva el registro (FR-003) sin borrar nada, libera el cupo
  con un filtro en el conteo existente (FR-004) y bloquea la reinscripción sin
  código extra: la restricción de unicidad ya rechaza el duplicado (FR-005).
  La migración declara todo lo existente como activo.
- **Alternatives considered**:
  - Borrado físico del registro: rechazado, viola FR-003 y la trazabilidad.
  - Tabla separada de cancelaciones: rechazado por YAGNI; dispersa la regla de
    disponibilidad en joins y complica el conteo.

## Decisión 2: Disciplina de concurrencia idéntica a register()

- **Decision**: El nuevo servicio `cancel()` abre transacción `IMMEDIATE`
  antes de leer, evalúa el corte de 24h con el reloj real obtenido tras el
  lock, mapea solo contención "locked" a `busy` reintentable y propaga el
  resto. Doble cancelación concurrente: la primera gana, la segunda ve estado
  cancelado y no libera cupo de nuevo.
- **Rationale**: Constitución III + simetría con `register()`: evita TOCTOU en
  el borde de 24h (una solicitud que esperó el lock y cruzó el límite se
  deniega en vez de cancelar tarde) y garantiza "liberar exactamente una vez"
  (FR-009).
- **Alternatives considered**:
  - Evaluar el reloj antes del lock: rechazado, reintroduce la carrera que el
    proyecto ya corrigió en inscripción (checkpoint v2).
  - `select_for_update()`: rechazado, no protege en SQLite (README y
    constitución).

## Decisión 3: Confirmación en página dedicada (sesión clarify Q1)

- **Decision**: Ruta de confirmación (GET, pantalla con resumen: actividad,
  fecha, límite de 24h) + ejecución por POST en la misma ruta, con mensajes
  vía `messages` y redirección a "mis inscripciones".
- **Rationale**: Respuesta explícita del usuario (opción A); evita
  cancelaciones accidentales (FR-007), no requiere JavaScript y se prueba con
  el cliente de tests existente, coherente con el estilo clásico
  (alta/baja por POST como `salir` y `enroll`).
- **Alternatives considered**:
  - Diálogo inline en "mis inscripciones": rechazado, exige JS y es menos
    testeable con el stack actual.
  - Acción directa sin confirmación: rechazado, viola FR-007.

## Decisión 4: Actividad deshabilitada futura (sesión clarify Q2)

- **Decision**: Aplica la misma regla de 24h que las habilitadas (opción B);
  solo la actividad ya iniciada deniega siempre.
- **Rationale**: Retener al estudiante en una actividad que no se dictará no
  aporta nada; el cupo de una deshabilitada no es escaso pero el historial
  queda limpio y consistente.
- **Alternatives considered**:
  - Denegar siempre en deshabilitada: rechazado por el usuario en clarify.

## Decisión 5: Disponibilidad y validación sobre activas

- **Decision**: `with_availability()` resta solo inscripciones activas; el
  `clean()` de capacidad valida contra activas.
- **Rationale**: Un único punto de verdad para el cupo; las vistas
  (`catalog`, `detail`, `mine`) heredan el comportamiento sin cambios de
  lógica.
- **Alternatives considered**:
  - Recalcular en cada vista: rechazado, dispersa la regla y habilita
    divergencias.

## Decisión 6: Admin de solo consulta extendido

- **Decision**: `RegistrationAdmin` muestra estado y momento de cancelación
  (listado + readonly); mantiene sin altas ni bajas.
- **Rationale**: Trazabilidad administrativa (historia 3) sin crear atajos que
  eludan reglas (constitución, flujo Docker: admin de consulta).
- **Alternatives considered**:
  - Acción de admin para cancelar ajenas: rechazado, fuera de alcance
    (Assumptions: solo el propio estudiante cancela).

## Decisión 7: Estrategia de tests

- **Decision**: Extender `activities/tests/test_base.py` con el estilo
  existente: reloj fijo `NOW`, fábrica `activity()` con `starts_at` relativos
  (+48h, +12h, borde exacto inicio−24h permitido / −24h+1s denegado),
  `TransactionTestCase` + barrera para doble cancelación concurrente, y tests
  de vista (GET confirmación, POST ejecuta, mensajes, redirección, aislamiento
  por usuario).
- **Rationale**: Reutiliza fixtures y patrones probados; el borde inclusivo y
  la concurrencia son los riesgos reales de esta feature.
- **Alternatives considered**:
  - Nuevo archivo de tests separado: rechazado, fragmenta fixtures
    compartidas (`NOW`, `activity()`, usuarios).

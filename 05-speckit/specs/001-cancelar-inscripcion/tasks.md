# Tasks: Cancelar inscripción propia

**Input**: Design documents from `specs/001-cancelar-inscripcion/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: La constitución exige TDD (principio IV): los tests se escriben primero y DEBEN fallar antes de implementar. Cada historia incluye sus tareas de test.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Levantar el stack canónico Docker y fijar la línea base en verde antes de tocar código.

- [X] T001 Levantar stack y seed reproducible con `docker compose up --build` + `seed_demo --reference-time '2030-10-01T09:00:00-03:00'` vía `docker compose exec web`
- [X] T002 Verificar línea base en verde (`manage.py test --noinput`, `manage.py check`) vía `docker compose exec web`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Extensión del modelo y disponibilidad sobre la que dependen las tres historias.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T003 Extender `Registration` en `activities/models.py` con estado (activa/cancelada, default activa) y momento de cancelación (nulo si activa; con valor si y solo si cancelada)
- [X] T004 Crear y verificar la migración en `activities/migrations/` (`makemigrations`, filas existentes quedan activas)
- [X] T005 Contar solo inscripciones activas en `with_availability()` (`activities/services.py`) y en la guarda de capacidad de `Activity.clean()` (`activities/models.py`)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Cancelar inscripción propia a tiempo (Priority: P1) 🎯 MVP

**Goal**: El estudiante cancela desde "mis inscripciones" vía pantalla de confirmación dedicada; el cupo se libera.

**Independent Test**: Con inscripción activa a actividad +48h, confirmar cancelación y verificar estado cancelado, mensaje, redirección a "mis inscripciones" y cupo +1 (ver `quickstart.md` escenario 1).

### Tests for User Story 1 (TDD: escribir primero, verificar que FALLAN)

- [X] T006 [US1] Tests de servicio `cancel()` a tiempo en `activities/tests/test_base.py` (camino feliz, borde exacto inicio−24h permitido, registro conservado con momento, disponibilidad +1)
- [X] T007 [US1] Tests de vista en `activities/tests/test_base.py` (GET confirmación muestra resumen sin mutar, POST ejecuta con mensaje y redirige a `mine`, solo inscripciones propias accionables)

### Implementation for User Story 1

- [X] T008 [US1] Agregar claves de mensajes de cancelación al dict `MESSAGES` en `activities/services.py` (ver tabla en `contracts/cancelacion.md`)
- [X] T009 [US1] Implementar `cancel()` camino feliz en `activities/services.py` (transacción `IMMEDIATE` antes de leer, reloj real tras el lock, transición a cancelada con momento, libera un cupo; contención "locked" → `busy`, resto propaga; las denegaciones van en T015)
- [X] T010 [US1] Implementar vistas de confirmación (GET) y ejecución (POST) en `activities/views.py` (GET con resumen, POST ejecuta vía `cancel()`, mensaje del servicio + redirección a `mine`)
- [X] T011 [US1] Agregar rutas `activities/<pk>/cancel/` (GET confirmación, POST ejecución) en `activities/urls.py`
- [X] T012 [P] [US1] Crear plantilla de confirmación dedicada en `templates/activities/cancel_confirm.html` (resumen: actividad, fecha, límite 24h, botón confirmar)
- [X] T013 [US1] Mostrar botón "Cancelar" (solo si permitida) en `templates/activities/mine.html`

---

## Phase 4: User Story 2 - Cancelación bloqueada dentro de las 24 horas (Priority: P2)

**Goal**: Intentos fuera de plazo o con actividad iniciada se deniegan sin modificar inscripción ni cupo.

**Independent Test**: Con inscripción activa a actividad +12h, intentar cancelar y verificar que sigue activa, mensaje claro y cupo intacto (ver `quickstart.md` escenario 2).

### Tests for User Story 2 (TDD: escribir primero, verificar que FALLAN)

- [X] T014 [US2] Tests de denegación en `activities/tests/test_base.py` (+12h denegada, ya iniciada denegada, borde inicio−24h+1s denegado, deshabilitada dentro del plazo denegada)

### Implementation for User Story 2

- [X] T015 [US2] Agregar ramas de denegación en `cancel()` en `activities/services.py` (corte 24h inclusivo evaluado con el reloj tras el lock: `fuera_de_plazo`, `ya_iniciada`; deshabilitada futura aplica la misma regla 24h; si deniega, sin cambios)
- [X] T016 [US2] Verificar en vistas de `activities/views.py` el mensaje específico + redirección para cada denegación (`fuera_de_plazo`, `ya_iniciada`, deshabilitada en plazo)

---

## Phase 5: User Story 3 - Historial conservado y sin reinscripción (Priority: P3)

**Goal**: La cancelada sigue visible con fecha, la reinscripción se rechaza y el cupo liberado sirve a otros.

**Independent Test**: Tras cancelar, verificar badge "Cancelada" con fecha, rechazo de reinscripción con mensaje claro y que otro estudiante ocupa el cupo (ver `quickstart.md` escenarios 3–6).

### Tests for User Story 3 (TDD: escribir primero, verificar que FALLAN)

- [X] T017 [US3] Tests de historial y no-reinscripción en `activities/tests/test_base.py` (registro visible como cancelado, reintento rechazado, otro estudiante confirma, doble cancelación sin mover cupo)

### Implementation for User Story 3

- [X] T018 [P] [US3] Rechazar reinscripción con mensaje claro en `register()` en `activities/services.py` cuando existe inscripción cancelada (mantener unicidad por par)
- [X] T019 [P] [US3] Mostrar badge "Cancelada" con fecha en `templates/activities/mine.html` y reflejar estado cancelado en `templates/activities/detail.html`
- [X] T020 [P] [US3] Exponer estado y momento de cancelación como solo-lectura en `RegistrationAdmin` en `activities/admin.py` (sin altas ni bajas)

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Gates finales y validación end-to-end en el flujo Docker canónico.

- [X] T021 Ejecutar gates en contenedor vía `docker compose exec web` (`test --noinput`, `check`, `makemigrations --check --dry-run`)
- [X] T022 Recorrer los 6 escenarios de `specs/001-cancelar-inscripcion/quickstart.md` y verificar resultados esperados
- [X] T023 Revisar consistencia de mensajes en español y cerrar con `docker compose stop` (sin `down -v`)

---

## Phase 7: Correcciones post-análisis (incidente 2026-10-23)

**Origen**: re-ejecución de `/speckit.analyze` sobre la implementación terminada. 1 CRITICAL (C1), 2 MEDIUM (I1, I2) y 4 LOW. El código funciona; estas tareas cierran la brecha entre artefactos, constitución y código.

**Gates**: Phase 7 no se considera cerrada hasta que T030 corra en verde en el contenedor.

- [X] T024 [US1] Test concurrente de cancelación (FR-009) en `activities/tests/test_base.py`: `TransactionTestCase` + `Barrier` espejando `race()` (línea ~149); dos `cancel()` simultáneos sobre la misma inscripción deben dar `{"cancelled", "already_cancelled"}` y `available` debe subir exactamente 1
- [X] T025 [US1] Extraer la regla del corte a `activities/services.py`: `cancel_deadline(activity)` devuelve `starts_at - timedelta(hours=24)` y `can_cancel(registration, now)` devuelve True solo si estado activo, `starts_at > now` y `now <= cancel_deadline(activity)`
- [X] T026 [US1] Refactorizar `activities/views.py`: `mine()` y el GET de `cancel_request` usan `can_cancel()`; quitar `with_availability()` del camino de cancelación; el POST delega siempre en `cancel()` y muestra `MESSAGES[result]` (elimina la duplicación de I1)
- [X] T027 [US2] Test de vista en `activities/tests/test_base.py`: cancelar dos veces (segundo intento con `POST`) devuelve `200`/redirección a `mine` con mensaje `already_cancelled`, no `404` (FR-008: "ya cancelada" alcanzable por HTTP)
- [X] T028 [P] Alinear vocabulario de mensajes en `specs/001-cancelar-inscripcion/contracts/cancelacion.md`: tabla cerrada con `cancelled`, `too_late`, `started`, `already_cancelled`, `no_resubscribe`, `not_available`, `busy`; eliminar la cláusula "los identificadores exactos los fija la implementación" (I2)
- [X] T029 [P] Corregir `specs/001-cancelar-inscripcion/plan.md`: Constitution Check IV con la nota de cobertura concurrente, y reemplazar "las vistas solo orquestan" por la descripción real tras T025/T026 (I1)
- [X] T030 Ejecutar gates en contenedor vía `docker compose exec web` (`test --noinput`, `check`, `makemigrations --check --dry-run`) y actualizar `spec.md` Status de `Draft` a `Implemented`

---

## Dependencies

```text
Setup (T001→T002)
  └─▶ Foundational (T003→T004→T005)
        ├─▶ US1 (T006,T007 tests → T008→T009→T010→T011→T013; T012 en paralelo) 🎯 MVP
        ├─▶ US2 (T014 tests → T015→T016) — requiere cancel() de US1
        └─▶ US3 (T017 tests → T018,T019,T020 en paralelo) — requiere US1
              └─▶ Polish (T021→T022→T023)
                    └─▶ Phase 7 (T024→T025→T026→T027→T030; T028,T029 en paralelo)
```

Orden de completitud sugerido: Setup → Foundational → US1 → US2 → US3 → Polish. US2 y US3 requieren `cancel()` de US1; entre sí son independientes una vez que US1 existe.

## Parallel Execution Examples

```text
# US1: la plantilla de confirmación no depende del servicio ni las vistas
T012 (templates/activities/cancel_confirm.html)

# US3: tres archivos distintos sin dependencias entre sí
T018 (activities/services.py) + T019 (templates) + T020 (activities/admin.py)

# Phase 7: documentación en paralelo al código (archivos distintos)
T028 (contracts/cancelacion.md) + T029 (plan.md)
```

Nota: todas las tareas de test viven en `activities/tests/test_base.py` (decisión research 7), por lo que los tests corren secuenciales; el marcador [P] se reserva a archivos distintos.

## Implementation Strategy

**MVP primero**: entregar Setup + Foundational + US1 como incremento mínimo viable (cancelar a tiempo end-to-end con tests en verde). Luego US2 (denegaciones) y US3 (historial + no-reinscripción) como incrementos independientes. Estrategia TDD estricta por historia: tests primero en rojo, implementación mínima hasta verde, sin saltar gates Docker entre fases.

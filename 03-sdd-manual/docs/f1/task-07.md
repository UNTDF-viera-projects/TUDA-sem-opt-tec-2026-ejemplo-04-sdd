# Tarea 07 · Seed ampliado + `reset_demo` sin cambios (etapa 5)

- [x] **T07 · Dos inscripciones demo (deshabilitada + iniciada) idempotentes que conservan cancelaciones**
- **Estado:** `cerrada`

## Resultado concreto

`seed_demo.py` crea con `Registration.objects.create(...)` dentro del `@transaction.atomic` existente: Bruno en la actividad deshabilitada y Ana en la iniciada (E-17), ambas con la misma guarda de existencia por `(student, activity)` que el resto del seed (si la fila existe —confirmada o cancelada— se omite, sin reescribir `cancelled_at`/`created_at`). Las cuatro altas vía `register()` no cambian. `reset_demo.py` no cambia (F1-R28): borra las 5 actividades por `seed_key` y la cascada borra sus inscripciones, incluidas canceladas.

## Archivos / componentes afectados

- `activities/management/commands/seed_demo.py` (dos altas directas + guarda)
- `activities/management/commands/reset_demo.py` (sin cambios; solo verificación)
- `activities/tests/test_cancel_views.py` (tests `SeedTests`/`ResetTests` de esta etapa)

## Requisitos y escenarios que cubre

- D5, F-02 (corrección: son dos altas, ninguna pasa por `register()` — `disabled`/`started` las rechazarían), P-04 opción (a), F1-R28, S-02/S-08.
- Escenarios E-17 (E-06 aplicable a mano en deshabilitada, E-08 en iniciada), E-06, E-08 a nivel demo.

## Dependencias

- Depende de: T02 (modelo), T03 (sabe que `register()` rechazaría ambas y que `not_reenrollable` no debe dispararse en el seed).
- Bloquea a: T09 (recorrido README demuestra E-06/E-08 sin datos a mano).

## Condición de cierre comprobable

- Tras `seed_demo`: existen las dos inscripciones, confirmadas, y el recorrido manual puede cancelar la de Bruno (E-06) y recibe `window_closed` en la de Ana (E-08).
- Segunda corrida tras cancelar una de ellas: no duplica ni reescribe `cancelled_at`; `reset_demo --confirm` tras cancelaciones reconstruye todo confirmado.

## Prueba / evidencia para cerrarla

- `uv run --locked python manage.py test activities.tests.test_cancel_views.SeedResetTests --noinput` (adjuntar salida).
- Evidencia manual: `uv run --locked python manage.py seed_demo` dos veces con una cancelación intermedia + `SELECT student, activity, cancelled_at` antes/después; `reset_demo --confirm` + `seed_demo` reconstruye.

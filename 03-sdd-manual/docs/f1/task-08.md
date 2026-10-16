# Tarea 08 · Concurrencia y reloj tras el bloqueo (etapa 6)

- [x] **T08 · Probar doble cancelación simultánea, decisión con reloj post-espera y `busy`**
- **Estado:** `cerrada` (aprobada por reviewer F1 2026-10-08: 3 corridas verdes 6 tests OK; E-13 ⊆{cancelled,already,busy} sin doble cancelled + available 0→1; escritura condicional + reloj `assert_called_once` en `atomic` + `busy` selectivo verificados)

## Resultado concreto

Pruebas `TransactionTestCase` (archivo real `data/test.sqlite3`, dos hilos + `Barrier`, `close_old_connections`, patrón de `ConcurrencyTests`) que fijan: a lo sumo una transición, defensa estructural aislada, reloj leído una sola vez dentro del `atomic`, `busy` solo ante `locked` y propagación del resto.

## Archivos / componentes afectados

- `activities/tests/test_cancel_concurrency.py` (nuevo; único archivo de esta etapa)
- `activities/services.py` (solo si un test revela que falta la escritura condicional o el orden reloj/bloqueo; si no, sin cambios)

## Requisitos y escenarios que cubre

- F1-R06 (reloj dentro del `IMMEDIATE`; espera → `window_closed` si el plazo se cerró), F1-R16 (IMMEDIATE + `WHERE cancelled_at IS NULL`), F1-R17 (`busy` sin efecto parcial; otros `OperationalError` se propagan).
- Escenarios E-13; límites L-23, L-28, L-29.

## Dependencias

- Depende de: T03 (implementación de `cancel()` a probar). Independiente de T04…T07 (puede ir en paralelo tras T03).
- Bloquea a: T09 (suite completa exige 3 corridas verdes seguidas).

## Condición de cierre comprobable

- 3 corridas consecutivas en verde (flakiness de hilos bajo control).
- E-13: resultados ⊆ `{cancelled, already_cancelled, busy}`, nunca dos `cancelled`; una sola fila cancelada, un único `cancelled_at`, `available` −1 (no −2).
- Reloj: `assert_called_once` + `in_atomic_block`; post-espera fuera de plazo → `window_closed` intacto; dentro → `cancelled`.

## Prueba / evidencia para cerrarla

- `for i in 1 2 3; do uv run --locked python manage.py test activities.tests.test_cancel_concurrency --noinput; done` (adjuntar las 3 salidas).
- Tests exigidos: `test_E13_concurrent_pair_single_transition`, `test_conditional_write_alone_returns_already`, `test_clock_after_lock_outside_window_rejects` (espejo de `test_default_clock_after_lock_rejects_activity_that_started`), `test_L28_locked_returns_busy_without_effect`, `test_L29_other_operational_error_propagates`.

# Tarea 03 · Servicios: `WINDOW`, helpers, `cancel()`, cupo filtrado, `register()`, `MESSAGES` (etapa 2)

- [x] **T03 · Implementar toda la regla de dominio en `activities/services.py`**
- **Estado:** `cerrada`

## Resultado concreto

`activities/services.py` contiene: `WINDOW = timedelta(hours=24)`, `cancellation_deadline()` / `can_cancel()`, `cancel(student, activity_id, now=None)` con el orden §4 del plan, `with_availability()` y cupo lleno de `register()` contando solo confirmadas, rama `not_reenrollable` en la posición del duplicado, y las cinco claves de `MESSAGES` (corrección F-01 con los textos del plan §1).

## Archivos / componentes afectados

- `activities/services.py` (único archivo de producción de esta tarea)
- `activities/tests/test_cancel_service.py` (reloj fijo `NOW`, 1 test por fila L-01…L-07)
- `activities/tests/test_base.py` se conserva intacto como red de seguridad (no editar)

## Requisitos y escenarios que cubre

- F1-R03…R07 (rama genérica única; `WINDOW` 24 h; borde inclusivo sin redondeo; reloj dentro del `IMMEDIATE`; ancla a `starts_at` vigente), F1-R09/R10/R11 (update condicional, exactamente 1 cupo, 3 puntos juntos — X-01), F1-R13/R14/R15 (repetición antes que plazo, sin reloj), F1-R17 (solo `locked` → `busy`), F1-R18/R19 (sin guarda `is_active`), F1-R20…R23 (D3, precedencia de reinscripción), F1-R04/R26 parcial (helpers compartidos; consumo en T04/T05).
- Escenarios E-01, E-02, E-03, E-04, E-06, E-07, E-08, E-09, E-10, E-11, E-12, E-15; límites L-01…L-23 (L-24…L-30 en T04/T08), L-28/L-29 parcial servicio (`busy`/propagación, hilos en T08).
- Decisiones DD-03/DD-04/DD-05/DD-06. Tensión X-02/X-03 resueltas por precedencia.

## Dependencias

- Depende de: T01, T02 (modelo + 0002 aplicados).
- Bloquea a: T04 (vista llama a `cancel()`), T05 (templates usan `can_cancel`), T07 (seed respeta `not_reenrollable`), T08 (concurrencia), T09 (suite).

## Condición de cierre comprobable

- `test_cancel_service.py` en verde + `test_base.py` (22 pruebas) intacto y en verde: ningún test de precedencia existente se movió.
- E-15 pasa (llena → cancela → otro se inscribe → `registered`, `available == 0`); falla si solo se cambió `with_availability()`.
- `already_cancelled` antes que `window_closed` (E-10) y sin leer el reloj (reloj parcheado que falla si se invoca).

## Prueba / evidencia para cerrarla

- `uv run --locked python manage.py test activities.tests.test_cancel_service activities.tests.test_base --noinput` (adjuntar salida).
- Convención de nombres `test_E09_*`, `test_L04_*`, `test_R26_*` para trazabilidad.
- Casos mínimos exigidos: L-01…L-08, L-09…L-16, L-17…L-23, E-09/E-10 (fecha byte a byte idéntica), E-11/E-12 (mensaje ≠ `already_registered`), reprogramación de `starts_at` reabre/cierra plazo (F1-R07/S-02), asimetría `register` exclusivo vs `cancel` inclusivo.

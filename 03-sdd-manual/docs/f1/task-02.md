# Tarea 02 · Modelo `cancelled_at` + migración 0002 (etapa 1 del plan)

- [x] **T02 · Agregar `cancelled_at`, `is_cancelled` y piso de capacidad sobre confirmadas + migración aditiva**
- **Estado:** `cerrada`

## Resultado concreto

`Registration` tiene `cancelled_at = DateTimeField(null=True, blank=True)`, propiedad `is_cancelled`, y `Activity.clean()` cuenta solo confirmadas. Migración `activities/migrations/0002_*.py` (`AddField`, aditiva, sin backfill) generada y aplicada; filas previas quedan confirmadas y `available` no cambia en la migración.

## Archivos / componentes afectados

- `activities/models.py` (`cancelled_at`, `is_cancelled`, `Activity.clean()`)
- `activities/migrations/0002_*.py` (nuevo, generado con `makemigrations`)
- `activities/tests/test_cancel_service.py` (solo tests de modelo/migración de esta etapa; resto en T03)

## Requisitos y escenarios que cubre

- F1-R08 (misma fila, conserva `created_at`), F1-R12 (único campo, sin estado redundante), F1-R29 (propiedad derivada única).
- F1-R11 parcial (punto 3/3: `Activity.clean()` con `filter(cancelled_at__isnull=True)`; puntos 1-2 en T03, mismo commit según X-01).
- D1. Límites L-20/L-21/L-22 (base de modelo). Supuestos S-04/S-05.

## Dependencias

- Depende de: T01 (etapa 0 aprobada).
- Bloquea a: T03 (servicios), T06 (admin usa el campo).

## Condición de cierre comprobable

- `python manage.py check` sin avisos.
- `python manage.py makemigrations --check --dry-run` sin cambios pendientes.
- Una `Registration` creada sin `cancelled_at` tiene `is_cancelled is False` y cuenta en el cupo.

## Prueba / evidencia para cerrarla

- Ejecutar y adjuntar salida:
  `uv run --locked python manage.py migrate`
  `uv run --locked python manage.py check`
  `uv run --locked python manage.py makemigrations --check --dry-run`
  `uv run --locked python manage.py test activities.tests.test_cancel_service.RegistrationModelTests --noinput`
  (tests: `is_cancelled False/True`, `clean()` acepta capacidad == confirmadas con canceladas presentes, rechaza por debajo con texto vigente).
- Evidencia manual sobre **copia** de `data/db.sqlite3` (nunca la base de trabajo): migrar a `0002`, `SELECT COUNT(*) = COUNT(*) WHERE cancelled_at IS NULL` y `available` idéntico al previo.

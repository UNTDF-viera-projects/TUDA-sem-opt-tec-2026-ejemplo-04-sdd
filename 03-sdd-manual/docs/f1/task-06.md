# Tarea 06 · Admin: `cancelled_at` visible y de solo lectura (etapa 4)

- [x] **T06 · Exponer `cancelled_at` en el admin sin abrir escrituras**
- **Estado:** `cerrada`

## Resultado concreto

`RegistrationAdmin` tiene `list_display` con `cancelled_at` (M-08) y `readonly_fields = ["student", "activity", "created_at", "cancelled_at"]`, manteniendo sin alta (`has_add_permission False`) y sin baja (`has_delete_permission False`). `ActivityAdmin` no cambia; su `changeform_view` atómico + `clean()` sobre confirmadas (T02) permite bajar capacidad hasta el nº de confirmadas.

## Archivos / componentes afectados

- `activities/admin.py` (`RegistrationAdmin`; `ActivityAdmin` sin cambios)
- `activities/tests/test_cancel_views.py` (tests de admin de esta etapa; extiende `test_admin_rejects_capacity_and_read_only_registration`)

## Requisitos y escenarios que cubre

- F1-R27 (solo lectura, listado, sin eludir reglas; `README.md:74`), F1-R11 parcial (piso de capacidad sobre confirmadas), M-08 (adoptado por D2).
- Escenarios E-16; límites L-21 (reduce a nº de confirmadas → guarda), L-22 (por debajo → `ValidationError` con texto vigente).

## Dependencias

- Depende de: T02 (campo + `clean()` filtrado).
- Independiente de T03/T04/T05 (puede ir en paralelo tras T02). Bloquea a T09 (suite completa).

## Condición de cierre comprobable

- El docente reduce capacidad a 3 con 3 confirmadas + 1 cancelada → guarda (E-16/L-21).
- Por debajo de confirmadas → `ValidationError` «No puede reducir…» (L-22).
- `cancelled_at` ignorada en POST de edición (no se escribe) y presente en el listado.

## Prueba / evidencia para cerrarla

- `uv run --locked python manage.py test activities.tests.test_cancel_views.AdminTests --noinput` (adjuntar salida).
- Verificación manual: `/admin/` muestra la columna `cancelled_at`; intentar editarla no persiste.

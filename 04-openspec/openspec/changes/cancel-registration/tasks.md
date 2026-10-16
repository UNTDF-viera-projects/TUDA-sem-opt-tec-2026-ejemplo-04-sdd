# Tasks

## 1. Modelo y migración

- [ ] 1.1 Crear modelo `Cancellation` (`student`, `activity`, `cancelled_at=auto_now_add`, unique por par, `CASCADE`) y verificar con `docker compose exec web uv run --locked python manage.py makemigrations activities` que genera una migración
- [ ] 1.2 Registrar `CancellationAdmin` read-only (sin add/delete) y verificar en `/admin/` que la vista de cancelaciones es de consulta
- [ ] 1.3 Verificar `reset_demo --confirm` sigue limpiando tombstones de actividades demo vía `CASCADE`, con test o corrida manual documentada

## 2. Servicios (`register` + `cancel`)

- [ ] 2.1 Implementar `cancel(student, activity_id, now=None)` con `IMMEDIATE`, chequeo de existencia, `now` post-lock, ventana `starts_at - now >= 24h`, `DELETE + INSERT` atómico, `locked → busy`, y verificar con tests de éxito, ventana exacta (24h ok / 23:59:59 no), e `is_active` ignorado
- [ ] 2.2 Agregar chequeo de tombstone en `register()` que rechaza con el instante original, más helper de mensaje `Ya cancelaste tu inscripción el DD/MM/YYYY a las HH:mm` (zona `America/Argentina/Ushuaia`, `%d/%m/%Y %H:%M`), y verificar con tests de reintento bloqueado y doble-cancel idempotente
- [ ] 2.3 Agregar tests de concurrencia (doble-cancel simultáneo, cancel-vs-register al último cupo con `Barrier` sobre `test.sqlite3`) y verificar con `docker compose exec web uv run --locked python manage.py test --noinput`

## 3. Vistas, rutas y templates

- [ ] 3.1 Agregar ruta POST `activities/<pk>/cancel/` y vista `cancel` (`login_required + require_POST`, identidad de sesión, mensajes), y verificar con tests de 405 en GET, 403 sin CSRF y que un `student` ajeno en el POST es ignorado
- [ ] 3.2 Actualizar `detail` para mostrar el mensaje con fecha al cancelado (sin botón) y `mine` con sección de canceladas con fecha, y verificar con tests de render (`assertContains` de fecha formateada, p. ej. `03/10/2030 a las 14:05`)
- [ ] 3.3 Verificar suite completa en Docker (`docker compose up --build`, luego `docker compose exec web uv run --locked python manage.py test --noinput`, `check` y `makemigrations --check --dry-run`)

## Workflow follow-up

- Implementar con `/opsx-apply cancel-registration` una vez aprobada la propuesta.
- Archivar con `/opsx-archive cancel-registration` tras la revisión.

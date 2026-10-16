# Tarea 04 · Vista `cancel_registration` + URL `cancel` + contexto (etapa 3a)

- [x] **T04 · Exponer la cancelación por POST con destino único y contexto de elegibilidad**
- **Estado:** `cerrada` (aprobada por reviewer F1 2026-10-08: `CancelViewTests` 12/12 OK; 5 resultados 302 a `/my-registrations/` con clave; E-03/E-04/E-05 idénticos sin 404; GET 405 / sin-CSRF 403 / anónimo a `/accounts/login/`; `now` único por petición; `cancel` solo con `request.user`)

## Resultado concreto

`POST activities/<int:pk>/cancel/` (nombre `cancel`) cancela solo con identidad de `request.user`, responde `302` a `/my-registrations/` en los cinco resultados, `GET` → `405`, anónimo → login, sin CSRF → `403`. `detail` expone `can_cancel` y `mine` expone `cancellable_ids`, ambos con un único `now` por petición vía el helper compartido (sin duplicar la fórmula).

## Archivos / componentes afectados

- `activities/views.py` (`cancel_registration` con `login_required` + `require_POST`, contexto en `detail` y `mine`)
- `activities/urls.py` (`path("activities/<int:pk>/cancel/", …, name="cancel")`)
- `activities/tests/test_cancel_views.py` (tests de vista/URL/sesión de esta etapa)

## Requisitos y escenarios que cubre

- F1-R01 (identidad solo de `request.user`), F1-R02 (POST exclusivo + sesión + CSRF), F1-R24 (302 único a `mine`, sin `get_object_or_404` — X-04), F1-R26 parcial (misma regla servicio/vista vía `can_cancel`, corrección F-03).
- D6, P-03 opción (a) (ruta por actividad).
- Escenarios E-01 (302), E-03/E-04/E-05 (identidad de respuesta), E-14; límites L-24/L-25/L-26, L-30 (actividad borrada → `not_cancellable`, sin `404`).

## Dependencias

- Depende de: T02 (modelo), T03 (servicio `cancel()` + `can_cancel()` + `MESSAGES`).
- Bloquea a: T05 (templates consumen `can_cancel`/`cancellable_ids`), T09 (recorrido manual).

## Condición de cierre comprobable

- Los cinco resultados (`cancelled`, `already_cancelled`, `window_closed`, `not_cancellable`, `busy` simulado) devuelven `302` a `/my-registrations/` con su clave de mensaje (`extra_tags=result`).
- E-03 vs E-04 vs E-05 idénticos en clave/texto/status/destino (helper de comparación campo a campo).
- `GET` → `405` sin efecto; `POST` sin token → `403`; anónimo → login (`config/settings.py:23`).

## Prueba / evidencia para cerrarla

- `uv run --locked python manage.py test activities.tests.test_cancel_views.CancelViewTests --noinput` (adjuntar salida).
- Tests exigidos: identidad de respuesta E-03/E-04/E-05, actividad inexistente sin `404`, `L-30` (actividad eliminada entre render y POST → `not_cancellable`), E-14/L-24…L-26, doble POST (cancelled → already_cancelled, L-27 a nivel vista).

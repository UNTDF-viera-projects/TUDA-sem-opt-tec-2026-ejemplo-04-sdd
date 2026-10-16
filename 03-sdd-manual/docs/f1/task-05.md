# Tarea 05 · Plantillas `detail.html` y `mine.html` (etapa 3b)

- [x] **T05 · Distinguir confirmada/cancelada y ofrecer el botón solo dentro de plazo**
- **Estado:** `cerrada` (aprobada por reviewer F1 2026-10-08: `TemplateTests` 4/4 OK; botón⇔`cancel()` con mismo `now` parchado; `assertNotContains` confirmada en cancelada + `cancelled_at` visible en `detail`/`mine`; L-27 una sola fecha `count=1`)

## Resultado concreto

`detail.html` y `mine.html` muestran badge `Confirmada`/`Cancelada`, fecha `cancelled_at` en la cancelada, botón POST con CSRF a `{% url 'cancel' %}` solo cuando `can_cancel`/`cancellable_ids` lo permite; la cancelada no afirma «confirmada», no ofrece alta ni reinscripción, e informa que la reinscripción no está habilitada. Fuera de plazo se muestra la regla en texto (P-01 propuesta (c)), sin botón.

## Archivos / componentes afectados

- `templates/activities/detail.html`
- `templates/activities/mine.html`
- `activities/tests/test_cancel_views.py` (tests de plantilla de esta etapa)
- No cambia `static/` (mensajes heredan `.message` de `base.html`) ni `activities/forms.py`

## Requisitos y escenarios que cubre

- F1-R25 (distinguir estado + mostrar `cancelled_at`; nunca «confirmada» sobre cancelada), F1-R26 (botón ⇔ concesión del servicio, mismo helper — M-02/F-03).
- P-01 (propuesta (c): regla en texto, sin instante derivado; L-31 no es prueba sino decisión de display).
- Límites L-27 (doble clic → `cancelled` + `already_cancelled`, una sola fecha) a nivel interfaz.

## Dependencias

- Depende de: T03 (helper `can_cancel`), T04 (`can_cancel`/`cancellable_ids` en contexto + URL `cancel`).
- Bloquea a: T09 (recorrido manual y README).

## Condición de cierre comprobable

- Con reloj parchado en la misma posición que el servicio: el botón aparece exactamente cuando `cancel()` concedería y se oculta cuando devolvería `window_closed`.
- `assertNotContains` «Tu inscripción está confirmada» sobre fila cancelada; `cancelled_at` visible en ambas plantillas.

## Prueba / evidencia para cerrarla

- `uv run --locked python manage.py test activities.tests.test_cancel_views.TemplateTests --noinput` (adjuntar salida).
- Tests exigidos: `test_R25_cancelled_shows_date_not_confirmed`, `test_R26_button_hidden_outside_window`, `test_R26_button_matches_service_decision`, `test_L27_double_click_single_date`.

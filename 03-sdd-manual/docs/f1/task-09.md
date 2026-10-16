# Tarea 09 · Suite completa + README y recorrido demo (etapa 7)

- [x] **T09 · Dejar la suite en verde con uv y Docker y documentar la cancelación**
- **Estado:** `cerrada`

## Resultado concreto

`README.md` documenta el recorrido con cancelación, la tabla de resultados con las cinco claves nuevas, los dos casos nuevos del seed y la alineación con `compose.yaml` (observación §8.2: `README:38/:48` nombra un volumen que el compose vigente no declara). Criterios §6.6 de la spec cumplidos en ambos entornos.

## Archivos / componentes afectados

- `README.md` (recorrido, tabla de resultados, seed, compose)
- Toda la suite (`test_base.py` + `test_cancel_service/views/concurrency.py`) como verificación, sin código nuevo salvo ajustes de docs

## Requisitos y escenarios que cubre

- Criterio de terminado §6.6: suite §4+§5, `check`, `makemigrations --check`, P-01/P-03/P-04 respondidas (P-01 cambia lo visible), E-06 y E-08 demostrables sin datos a mano.
- Riesgos R-9 (README vs compose) y R-7 (L-31/P-01) cerrados aquí.

## Dependencias

- Depende de: T01…T08 (acumula todo).
- No bloquea a nadie; es el cierre de implementación antes de T10 (revisión).

## Condición de cierre comprobable

- En verde con uv **y** con Docker: `test --noinput`, `check`, `makemigrations --check --dry-run`.
- El recorrido escrito del README permite a un tercero demostrar E-06 (deshabilitada cancelable) y E-08 (plazo vencido) sin preparar datos a mano.

## Prueba / evidencia para cerrarla

- Adjuntar salidas:
  `uv sync --locked && uv run --locked python manage.py migrate`
  `uv run --locked python manage.py test --noinput`
  `uv run --locked python manage.py check`
  `uv run --locked python manage.py makemigrations --check --dry-run`
  `docker compose up --build` + `docker compose exec web uv run --locked python manage.py test --noinput`
- Recorrido manual firmado: pasos + capturas/URLs (`/`, detalle, `/my-registrations/`) para E-06 y E-08.

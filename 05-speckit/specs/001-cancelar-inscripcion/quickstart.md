# Quickstart: Validar cancelación de inscripción propia

**Fecha**: 2026-10-16 | Flujo canónico Docker según constitución I.

## Prerrequisitos

- Docker y Compose instalados; puerto 8000 libre.
- Credenciales demo: `ana`, `bruno`, `docente` (ver README).

## Puesta en marcha

```sh
docker compose up --build
# En otra terminal, seed reproducible y apertura:
docker compose exec web uv run --locked python manage.py seed_demo --reference-time '2030-10-01T09:00:00-03:00'
```

Abrir http://localhost:8000/ . Estado inicial esperado: taller (+48h, con
cupo), clínica (+12h), laboratorio completo, deshabilitada (+96h) e
iniciada (−2h); Ana inscripta en taller/clínica.

## Escenarios de validación

1. **Cancelar a tiempo**: ingresar como `ana` → Mis inscripciones → Cancelar
   el taller → pantalla de confirmación con resumen → Confirmar.
   Esperado: mensaje de cancelación, badge "Cancelada" con fecha, y el taller
   muestra un cupo más disponible.
2. **Bloqueo dentro de 24h**: como `ana`, intentar cancelar la clínica.
   Esperado: denegación con mensaje claro; la inscripción sigue activa y el
   cupo no cambia.
3. **Deshabilitada futura**: la actividad deshabilitada (+96h) acepta
   cancelación con la misma regla de 24h; una ya iniciada la deniega.
4. **Sin reinscripción**: como `ana`, intentar reinscribirse al taller
   cancelado. Esperado: rechazo con mensaje claro.
5. **Cupo liberado para otros**: ingresar como `bruno` e inscribirse al
   taller. Esperado: inscripción confirmada normalmente.
6. **Doble cancelación**: reintentar cancelar el taller ya cancelado.
   Esperado: denegación sin mover el cupo.

## Gates (dentro del contenedor)

```sh
docker compose exec web uv run --locked python manage.py test --noinput
docker compose exec web uv run --locked python manage.py check
docker compose exec web uv run --locked python manage.py makemigrations --check --dry-run
```

Esperado: suite en verde, `check` sin issues, sin migraciones pendientes.
Cerrar con `docker compose stop` (conserva datos; no usar `down -v`).

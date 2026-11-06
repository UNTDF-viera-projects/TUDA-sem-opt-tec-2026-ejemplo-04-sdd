# Implementation Plan: Cancelar inscripción propia

**Branch**: `001-cancelar-inscripcion` | **Date**: 2026-10-16 | **Spec**: `specs/001-cancelar-inscripcion/spec.md`

**Input**: Feature specification from `/specs/001-cancelar-inscripcion/spec.md`

## Summary

El estudiante cancela sus propias inscripciones desde "mis inscripciones" con
límite de 24h antes del inicio (inclusivo), pasando por una pantalla de
confirmación dedicada. El registro se conserva como cancelado (con momento de
cancelación), el cupo se libera de inmediato y la reinscripción queda
bloqueada (guarda explícita `no_resubscribe` en `register()`, respaldada por la
unicidad por par). Enfoque técnico (ver `research.md`):
estado en `Registration` + servicio `cancel()` con la misma disciplina de
concurrencia que `register()` (IMMEDIATE, reloj real tras el lock), conteo de
disponibilidad solo sobre activas, y tests espejando `test_base.py`.

## Technical Context

**Language/Version**: Python 3.12.14

**Primary Dependencies**: Django 5.2.x (sin dependencias nuevas)

**Storage**: SQLite (`data/db.sqlite3` local; volumen dedicado en Docker;
`data/test.sqlite3` aislada para tests)

**Testing**: Django test framework (`manage.py test --noinput`); estilos
existentes `TestCase` + `TransactionTestCase` con relojes fijos en
`activities/tests/test_base.py`

**Target Platform**: Web local docente, solo loopback (`127.0.0.1:8000`),
zona de visualización America/Argentina/Ushuaia

**Project Type**: Web application (Django clásico server-rendered, proyecto
único)

**Performance Goals**: Uso local docente de baja concurrencia; sin metas de
throughput (la constitución excluye explícitamente alta carga)

**Constraints**: Transacción SQLite `IMMEDIATE` antes de leer cupo o reloj;
reloj efectivo evaluado tras adquirir el lock; solo contención "locked" es
reintentable (`busy`); resto de errores propaga; sin autocarga de `.env`;
servicio solo en loopback

**Scale/Scope**: 5 actividades demo, decenas de usuarios ficticios; 1 feature:
~4 archivos fuente (`models`, `services`, `views`/`urls`, plantillas) +
migración + tests

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Docker-Primero**: la verificación se ejecuta vía
  `docker compose exec web ...`; el plan no agrega servicios ni puertos. PASS.
- **II. Simplicidad Django Clásico**: vistas clásicas + plantillas + SQLite;
  cero dependencias nuevas; sin SPAs, colas ni servicios. PASS.
- **III. Corrección bajo Concurrencia**: `cancel()` replica la disciplina de
  `register()` (IMMEDIATE antes de leer, reloj real tras el lock, corte de 24h
  con ese reloj, `busy` solo para contención conocida). PASS.
- **IV. Tests-Primero**: tests nuevos con relojes fijos y aislamiento
  existentes; gates `test`, `check`, `makemigrations --check --dry-run`.
  Cobertura concurrente de FR-009 en `CancelConcurrencyTests`
  (`TransactionTestCase` + barrera, T024). PASS.
- **V. Seguridad Explícita de los Datos**: ninguna eliminación de registros;
  migración con default "activa" para filas existentes; admin sigue sin
  altas/bajas. PASS.
- **VI. Sin Configuración Oculta**: sin nuevas variables de entorno ni
  secretos; sin cambios a exports/checkpoints. PASS.

Reevaluación post-fase 1: el diseño (`data-model.md`, `contracts/`,
`quickstart.md`) no introduce dependencias, servicios ni atajos
administrativos; todos los gates siguen en PASS.

## Project Structure

### Documentation (this feature)

```text
specs/001-cancelar-inscripcion/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
activities/
├── models.py            # Registration: estado + momento de cancelación
├── services.py          # cancel() + MESSAGES + conteo solo de activas
├── views.py             # confirmación (GET) + ejecución (POST) + mine
├── urls.py              # rutas de confirmación y cancelación
├── forms.py             # sin cambios (identidad desde sesión)
├── admin.py             # mostrar estado/momento, seguir solo-lectura
├── migrations/          # migración de nuevos campos (default: activa)
└── tests/
    └── test_base.py     # tests de cancelación (mismo estilo existente)

templates/activities/
├── mine.html            # badge Cancelada + botón Cancelar cuando aplique
├── cancel_confirm.html  # nueva: pantalla de confirmación dedicada
└── detail.html          # reflejar estado cancelado si aplica

config/                  # sin cambios
```

**Structure Decision**: Proyecto único Django existente. Toda la feature vive
en `activities/` + `templates/activities/`; sin nuevos paquetes ni capas. La
lógica de negocio va en `services.py`: `cancel()` decide y muta bajo
`IMMEDIATE`, `cancel_block_reason()` / `can_cancel()` son la única fuente de
verdad del corte de 24h. Las vistas solo consultan esos predicados, muestran
mensajes y redirigen; no re-evalúan reglas.

## Complexity Tracking

Sin violaciones a la constitución: no se agregan dependencias, servicios,
capas ni patrones nuevos. Sección sin filas.

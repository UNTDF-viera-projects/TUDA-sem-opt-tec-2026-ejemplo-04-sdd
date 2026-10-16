# Ejemplos de trabajo con agentes · SDD · UNTDF 2026

Material del Seminario Tecnológico Optativo. Cada carpeta resuelve **la misma funcionalidad** sobre **la misma base de código** con una forma distinta de trabajar con un agente de programación, para poder comparar procesos y resultados.

## La base común

Todos los ejemplos parten del commit `feat: demo base`: una demo de inscripciones a actividades hecha con Django clásico (templates, sesiones y SQLite), que se ejecuta con uv o Docker. Uso local docente con datos ficticios.

## La funcionalidad: cancelar una inscripción (F1)

Las reglas acordadas son las mismas en todos los ejemplos:

- Solo el titular cancela su inscripción.
- Se puede cancelar hasta 24 horas antes del inicio, inclusive y sin redondear.
- La inscripción no se borra: queda cancelada, con su fecha de cancelación.
- Cancelar libera exactamente un cupo.
- Repetir la cancelación conserva la fecha original y no libera otro cupo, incluso fuera de plazo.
- Una actividad deshabilitada se puede cancelar si se cumple el plazo.
- Hay una confirmación previa, y la ejecución usa POST, sesión autenticada y CSRF.
- Una inscripción ajena o inexistente recibe la misma respuesta genérica, sin revelar datos.
- Dos cancelaciones simultáneas producen una sola transición.
- La reinscripción queda fuera de F1 y se rechaza de forma comprensible.

## Ejemplos

| Carpeta | Enfoque | Qué mirar |
|---|---|---|
| [`01-simple-plan`](01-simple-plan/) | **Plan mode + implement**: el agente arma un plan y lo ejecuta en una sola pasada. | El diff del commit de implementación. |
| [`02-rpi`](02-rpi/) | **Research → Plan → Implement**: tres fases separadas, cada una con su prompt. | [`PROMPT-RESEARCH.md`](02-rpi/PROMPT-RESEARCH.md), [`PROMPT-PLAN.md`](02-rpi/PROMPT-PLAN.md), [`PROMPT-IMPLEMENT.md`](02-rpi/PROMPT-IMPLEMENT.md) |
| [`03-sdd-manual`](03-sdd-manual/) | **SDD manual**: especificación, plan y tareas como documentos versionados que se revisan antes de implementar. | [`PROMPT-SPEC.md`](03-sdd-manual/PROMPT-SPEC.md), [`PROMPT-PLAN.md`](03-sdd-manual/PROMPT-PLAN.md), [`PROMPT-TASKS.md`](03-sdd-manual/PROMPT-TASKS.md) y [`docs/f1/`](03-sdd-manual/docs/f1/) |
| `04-openspec` | **SDD con OpenSpec**. | *Pendiente de importar.* |
| `05-speckit` | **SDD con Spec Kit**. | *Pendiente de importar.* |

## Cómo ejecutar un ejemplo

Cada ejemplo es un proyecto independiente con su propio README. Desde la carpeta del ejemplo:

```sh
cd 01-simple-plan
uv sync --locked
uv run --locked python manage.py migrate
uv run --locked python manage.py seed_demo
uv run --locked python manage.py runserver 127.0.0.1:8000
```

Abrir http://localhost:8000/. Las cuentas ficticias son `ana`, `bruno` y `docente`, con la contraseña `untdf-demo-2026`. El README de cada ejemplo explica también cómo usar Docker, reiniciar los datos y correr las pruebas.

## Recorrer la historia

Cada ejemplo se importó con su historia original, así que se puede ver cómo evolucionó:

```sh
git log --oneline -- 02-rpi            # commits de un ejemplo
git diff <commit-base> <commit-final> -- 03-sdd-manual   # qué cambió la implementación
```

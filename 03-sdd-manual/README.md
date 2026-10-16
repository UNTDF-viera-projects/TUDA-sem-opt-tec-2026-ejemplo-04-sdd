# Demo de inscripciones · UNTDF

Punto de partida del alumno: Django clásico, sesiones, templates y SQLite. Todas las inscripciones están confirmadas. Uso local docente, datos ficticios; no es una configuración de producción.

## Arranque con uv

Requiere uv 0.12.19 (o compatible); uv prepara Python 3.12.14 si falta. Primera instalación requiere Internet.

```sh
uv sync --locked
uv run --locked python manage.py migrate
uv run --locked python manage.py seed_demo
uv run --locked python manage.py runserver 127.0.0.1:8000
```

Abrir http://localhost:8000/ . Cuentas ficticias: `ana`, `bruno`, `docente`; contraseña inicial `untdf-demo-2026`. Docente entra en `/admin/`. Las cuentas existentes conservan su contraseña y permisos al repetir seed. Recorrido: ingresar → catálogo → actividad → inscribirme → mis inscripciones → salir (POST). Todos los horarios se muestran en America/Argentina/Ushuaia.

## Recorrido con cancelación

Desde `/my-registrations/` (o el detalle de la actividad) cada inscripción confirmada dentro del plazo muestra el botón «Cancelar inscripción» (`POST activities/<id>/cancel/`); tras cancelar, la vista redirige a `/my-registrations/` con el mensaje correspondiente y la fila pasa a «Cancelada» sin botón de alta (la reinscripción no está habilitada). Fuera del plazo se muestra la regla «Cancelación disponible hasta 24 h antes del inicio», sin botón. El plazo es `inicio − 24 h` (borde inclusivo); la repetición responde «ya estaba cancelada» sin leer el reloj.

Casos demostrables sin preparar datos a mano (basta `seed_demo`):

1. **E-06 · deshabilitada cancelable:** ingresar como `bruno` → abrir el detalle de «Encuentro deshabilitado» (actividad deshabilitada con inscripción de Bruno) → el botón de cancelación está visible pese a `Habilitada: No` → `POST activities/<id>/cancel/` → 302 a `/my-registrations/` con «Inscripción cancelada. Se liberó un cupo.» y la tarjeta queda «Cancelada».
2. **E-08 · plazo vencido:** ingresar como `ana` → abrir el detalle de «Actividad ya iniciada» (inscripción de Ana, inicio a −2 h) → no hay botón, solo la regla de 24 h → `POST activities/<id>/cancel/` directo responde 302 a `/my-registrations/` con «No podés cancelar: el plazo venció 24 h antes del inicio.» y la fila sigue confirmada.

```sh
uv run --locked python manage.py test --noinput
uv run --locked python manage.py check
uv run --locked python manage.py makemigrations --check --dry-run
```

Las pruebas usan `data/test.sqlite3`, aislada de `data/db.sqlite3`, y eliminan únicamente la base de pruebas. Las pruebas concurrentes usan conexiones independientes y un archivo real, con barrera de inicio. No ejecutar dos suites sobre la misma carpeta al mismo tiempo.

## Docker

Requiere Docker y Compose; no requiere Python/uv en el host. Python 3.12.14 y uv 0.12.19 están fijados en Dockerfile, y Django 5.2.17 en uv.lock.

```sh
docker compose up --build
# En otra terminal:
docker compose exec web uv run --locked python manage.py test --noinput
docker compose stop
docker compose start
```

El servicio `web` sirve http://localhost:8000/ solo en loopback. Las migraciones y seed iniciales son automáticos; reconstruir o reiniciar conserva las inscripciones. Los datos viven en `data/db.sqlite3` del repositorio mediante el bind mount `.:/app` (con `DEMO_DATA_DIR=/app/data`), no en un volumen nombrado: `stop`/`start` y `up --build` conservan el archivo. `.venv` del host se excluye; las dependencias del contenedor viven en `/opt/venv`. El código se monta para recarga; cambiar uv.lock requiere reconstruir.

Para una práctica independiente, usar una **copia de código nueva**, puerto y nombre diferentes:

```sh
DEMO_PORT=8016 COMPOSE_PROJECT_NAME=sdd-practica docker compose up --build
```

El puerto8016 es un ejemplo para la copia restaurada: comprobar que esté libre y elegir otro puerto y nombre de proyecto si existe otra práctica simultánea.

No usar `down` para reinicios cotidianos. Stop/start conserva datos; como los datos están en el bind mount del repositorio, `down -v` tampoco los borra (no hay volumen nombrado que eliminar).

## Datos repetibles y reinicio explícito

Seed crea cinco actividades: taller a +48h, clínica a +12h, laboratorio completo a +72h, deshabilitada a +96h e iniciada a −2h. Ana está en taller/clínica/iniciada; Bruno en taller/laboratorio/deshabilitada. Las dos últimas son altas directas (el servicio las rechazaría por `disabled`/`started`) con guarda de existencia por `(student, activity)`: si la fila ya existe —confirmada o cancelada— se omite y no se reescribe, así que repetir seed conserva cancelaciones. La primera carga persiste su ancla; cargas siguientes no desplazan fechas, duplican registros ni reescriben usuarios o ediciones. Si falta una inscripción inicial y ya no se cumplen condiciones, seed informa el resultado y preserva lo existente.

## Resultados de cancelación

`POST activities/<id>/cancel/` siempre redirige a `/my-registrations/` con una de estas claves:

| Clave | Texto | Cuándo |
| --- | --- | --- |
| `cancelled` | `Inscripción cancelada. Se liberó un cupo.` | Confirmada dentro del plazo; guarda `cancelled_at` y libera un cupo |
| `already_cancelled` | `Esta inscripción ya estaba cancelada.` | Repetición (antes que el plazo, sin leer el reloj); no reescribe la fecha |
| `window_closed` | `No podés cancelar: el plazo venció 24 h antes del inicio.` | `now` posterior a `inicio − 24 h` (borde inclusivo) |
| `not_cancellable` | `No se pudo cancelar esta inscripción.` | Genérico: ajena, inexistente o actividad borrada/inexistente (respuesta idéntica en clave, texto, estado y destino) |
| `not_reenrollable` | `Tu inscripción fue cancelada; la reinscripción no está habilitada.` | `register()` sobre una fila cancelada (gana a `disabled`/`started`/`full`); no crea fila nueva |

Para reproducir una referencia exacta en una base nueva:

```sh
uv run --locked python manage.py seed_demo --reference-time '2030-10-01T09:00:00-03:00'
```

**Reset elimina las cinco actividades identificadas de la demo y todas sus inscripciones, incluso las creadas manualmente sobre ellas. Conserva usuarios, sus contraseñas, actividades ajenas y registros asociados a las actividades ajenas.** Recalcula el ancla para una nueva clase; el comando muestra primero la base destino y sus efectos. Sin `--confirm` no modifica nada.

```sh
uv run --locked python manage.py reset_demo --confirm
# O dentro del volumen Docker:
docker compose exec web uv run --locked python manage.py reset_demo --confirm
# Para reloj reproducible:
uv run --locked python manage.py reset_demo --confirm --reference-time '2030-10-01T09:00:00-03:00'
```

## Configuración y límites

Django lee variables de entorno; **no carga `.env` automáticamente**. `.env.example` es una referencia; Compose sí utiliza `.env` para sus propias variables. `DEMO_DATA_DIR` cambia la ubicación de SQLite, `DJANGO_DEBUG`/`DJANGO_SECRET_KEY` configuran Django. Hay defaults docentes para arrancar sin pasos ocultos.

La disponibilidad se calcula desde registros. Las transacciones de inscripción y edición administrativa empiezan en SQLite `IMMEDIATE`; timeout 10s. Así se adquiere la reserva de escritura antes de leer el cupo. SQLite serializa escritores: es adecuado para esta demo local, no para alta carga. Un timeout devuelve `busy`, sin efecto parcial, y permite reintentar. Otros errores no se ocultan. `select_for_update()` no protege este caso en SQLite. La administración de inscripciones es de consulta, sin altas/bajas que eludan las reglas.

## Recuperar punto de partida

La exportación `../material-docente/checkpoints/base.tar.gz` contiene solo código, migraciones y lockfile, con raíz `demo-inscripciones/`. Su manifiesto registra checksum. Restaurar a **una carpeta nueva**, nunca encima del original:

```sh
mkdir -p /tmp/sdd-clase
 tar -xzf ../material-docente/checkpoints/base.tar.gz -C /tmp/sdd-clase
cd /tmp/sdd-clase/demo-inscripciones
uv sync --locked
uv run --locked python manage.py migrate
uv run --locked python manage.py seed_demo
uv run --locked python manage.py runserver 127.0.0.1:8016
```

La exportación excluye bases SQLite, entornos, caches y secretos. Las soluciones docentes se entregan fuera de esta carpeta.

## Revisión técnica del checkpoint actual

La base actual (v2,22 pruebas) evalúa el reloj real de inscripción dentro de IMMEDIATE inmediatamente antes de verificar el inicio. Así, una solicitud que espera un escritor y llega a una actividad ya iniciada devuelve `started` sin ocupar cupo. El parámetro `now` conserva el reloj fijo de pruebas; los duplicados se reconocen primero. La versión anterior se preserva como `base-v1.tar.gz` para reproducir los recorridos históricos; no se reescribe su procedencia.

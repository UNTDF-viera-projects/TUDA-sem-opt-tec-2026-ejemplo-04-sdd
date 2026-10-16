# Demo de inscripciones · UNTDF

Punto de partida del alumno: Django clásico, sesiones, templates y SQLite. Las inscripciones se conservan como canceladas, con su fecha, y una cancelación libera su cupo. Uso local docente, datos ficticios; no es una configuración de producción.

## Arranque con uv

Requiere uv 0.12.19 (o compatible); uv prepara Python 3.12.14 si falta. Primera instalación requiere Internet.

```sh
uv sync --locked
uv run --locked python manage.py migrate
uv run --locked python manage.py seed_demo
uv run --locked python manage.py runserver 127.0.0.1:8000
```

Abrir http://localhost:8000/ . Cuentas ficticias: `ana`, `bruno`, `docente`; contraseña inicial `untdf-demo-2026`. Docente entra en `/admin/`. Las cuentas existentes conservan su contraseña y permisos al repetir seed. Recorrido: ingresar → catálogo → actividad → inscribirme → mis inscripciones → cancelar (confirmación) → salir (POST). Todos los horarios se muestran en America/Argentina/Ushuaia.

## Cancelación de la inscripción (F1)

Solo el titular cancela, desde **mis inscripciones**: un GET muestra la confirmación con inicio y límite, y el POST con CSRF y sesión ejecuta. La ventana es de 24 horas completas antes del inicio, inclusiva y sin redondear; pasada la ventana no hay acción. La fila **no se borra**: queda con `cancelled_at` y deja de ocupar cupo, así que otra persona puede ocupar ese lugar. Repetir la cancelación es consultivo: conserva la fecha original y no libera otro cupo, incluso fuera de plazo. Una actividad deshabilitada también se puede cancelar dentro del plazo.

La reinscripción queda fuera de F1: tras cancelar, la actividad no muestra el formulario de inscripción y un intento directo responde `reinscription_unavailable` sin crear nada. Una inscripción ajena o inexistente recibe la misma respuesta genérica y el mismo destino que cualquier otra, sin revelar datos; el admin es de consulta y no puede dar de alta ni borrar filas.

Si el ancla de la demo quedó en el pasado, `reset_demo --confirm --reference-time '2030-10-01T09:00:00-03:00'` deja actividades con plazo abierto para practicar el recorrido.

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

El servicio `web` sirve http://localhost:8000/ solo en loopback. Las migraciones y seed iniciales son automáticos; reconstruir o reiniciar conserva las inscripciones. El volumen `sdd-base_sqlite-data` está separado de la base local. `.venv` del host se excluye; las dependencias del contenedor viven en `/opt/venv`. El código se monta para recarga; cambiar uv.lock requiere reconstruir.

Para una práctica independiente, usar una **copia de código nueva**, puerto y nombre diferentes:

```sh
DEMO_PORT=8016 COMPOSE_PROJECT_NAME=sdd-practica docker compose up --build
```

El puerto8016 es un ejemplo para la copia restaurada: comprobar que esté libre y elegir otro puerto y nombre de proyecto si existe otra práctica simultánea.

No usar `down -v` para reinicios cotidianos. Stop/start conserva datos.

## Datos repetibles y reinicio explícito

Seed crea cinco actividades: taller a +48h, clínica a +12h, laboratorio completo a +72h, deshabilitada a +96h e iniciada a −2h. Ana está en taller/clínica; Bruno en taller/laboratorio. La primera carga persiste su ancla; cargas siguientes no desplazan fechas, duplican registros ni reescriben usuarios o ediciones. Si falta una inscripción inicial y ya no se cumplen condiciones, seed informa el resultado y preserva lo existente.

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

La disponibilidad se calcula desde registros, y una inscripción cancelada no cuenta para ella ni para el piso de capacidad de la edición administrativa. Las transacciones de inscripción, cancelación y edición administrativa empiezan en SQLite `IMMEDIATE`; timeout 10s. Así se adquiere la reserva de escritura antes de leer el cupo. SQLite serializa escritores: es adecuado para esta demo local, no para alta carga. Un timeout devuelve `busy`, sin efecto parcial, y permite reintentar. Otros errores no se ocultan. `select_for_update()` no protege este caso en SQLite. La administración de inscripciones es de consulta, sin altas/bajas que eludan las reglas.

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

El checkpoint actual agrega F1 (59 pruebas: 22 de la base v2 + 37 de cancelación). El servicio de cancelación toma la misma reserva `IMMEDIATE` que la inscripción y evalúa el reloj real dentro de la transacción: una solicitud que esperó a un escritor y llega pasado el plazo devuelve `window_closed` sin tocar la fila. El orden de los chequeos importa y es el que sostiene las reglas: primero el titular (ajena e inexistente comparten respuesta), después `already_cancelled` —por eso repetir es consultivo aunque el plazo haya vencido—, y recién entonces la ventana de 24 horas. Dos cancelaciones simultáneas producen una sola transición porque la segunda transacción solo lee `cancelled_at` después de adquirir la reserva.

La base v2 evalúa el reloj real de inscripción dentro de IMMEDIATE inmediatamente antes de verificar el inicio. Así, una solicitud que espera un escritor y llega a una actividad ya iniciada devuelve `started` sin ocupar cupo. El parámetro `now` conserva el reloj fijo de pruebas; los duplicados se reconocen primero. La versión anterior se preserva como `base-v1.tar.gz` para reproducir los recorridos históricos; no se reescribe su procedencia.

Las pruebas de cancelación fijan el reloj en 2030 mientras las sesiones del backend nacen en el reloj real; por eso `CancelViewTests.login` extiende el vencimiento de la sesión, igual que ya hacía `test_base.py`. Es una adaptación del arnés de pruebas, no una regla del producto: con el reloj real ninguna sesión expira.

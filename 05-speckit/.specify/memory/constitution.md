<!---
Informe de Impacto de Sincronización (temporal, eliminar antes de commitear):
- Cambio de versión: 1.0.0 → 1.1.0 (MINOR: traducción completa al español +
  guía de flujo Docker materialmente ampliada y elevada a principio I)
- Principios modificados:
  - I. Simplicity-First, Django Classic → I. Docker-Primero, Flujo Reproducible
    (nuevo principio canónico; contenido de simplicidad Django movido a II)
  - II.–V. anteriores → II.–VI. traducidos y reordenados sin pérdida de reglas
- Secciones agregadas/ampliadas:
  - Flujo de Desarrollo con Docker (comandos canónicos, volúmenes, puertos,
    reconstrucción, prohibición de `down -v` rutinario)
  - Stack Tecnológico y Límites de Despliegue (traducido, Docker como referencia)
- Secciones eliminadas: ninguna
- TODOs pendientes: ninguno; todos los marcadores resueltos
--->

# Constitución de Demo de Inscripciones

## Principios Fundamentales

### I. Docker-Primero, Flujo Reproducible (NO NEGOCIABLE)

El flujo canónico de desarrollo, verificación y demo DEBE ser Docker Compose:
`docker compose up --build` para levantar, `docker compose exec web uv run
--locked python manage.py test --noinput` para probar, y `docker compose
stop` / `docker compose start` para reinicios cotidianos que conservan datos.
El servicio `web` DEBE atar solo loopback (`127.0.0.1:${DEMO_PORT:-8000}:8000`)
y persistir SQLite en el volumen dedicado, separado de la base local. Cambiar
`uv.lock` REQUIERE reconstruir la imagen; el código se monta para recarga sin
reconstruir. `down -v` NO DEBE usarse en reinicios rutinarios. Cada práctica
paralela DEBE usar copia de código nueva, puerto distinto (`DEMO_PORT`) y
nombre de proyecto distinto (`COMPOSE_PROJECT_NAME`), verificando antes que el
puerto esté libre. El flujo local con `uv` queda como alternativa documentada,
no como vía principal.

### II. Simplicidad Django Clásico

Cada funcionalidad DEBE usar Django clásico (plantillas renderizadas en
servidor, sesiones, SQLite) con el mínimo de dependencias declarado en
`pyproject.toml`/`uv.lock`. Nuevos frameworks, SPAs, ORMs, colas o servicios
NO DEBEN introducirse sin una enmienda que justifique por qué Django solo no
alcanza. Aplica YAGNI: empezar con la implementación correcta más simple.

### III. Corrección bajo Concurrencia (NO NEGOCIABLE)

Las inscripciones y ediciones administrativas que verifican cupo DEBEN abrir
una transacción SQLite `IMMEDIATE` antes de leer cupos o el reloj de inicio.
El `now` efectivo DEBE evaluarse después de adquirir la reserva de escritura;
una solicitud que esperó y llega con la actividad ya iniciada DEBE devolver
`started` sin ocupar cupo. Solo la contención conocida (`OperationalError` con
"locked") PUEDE mapearse a `busy` reintentable sin efecto parcial; cualquier
otro error DEBE propagarse, nunca ocultarse. NO DEBE confiarse en
`select_for_update()` para protección en SQLite.

### IV. Tests-Primero con Fixtures Deterministas

TDD es obligatorio: tests escritos → verificados en fallo → luego implementar
(Rojo-Verde-Refactor). Cada regla de cupo, duplicado, deshabilitado/iniciado y
concurrencia DEBE tener cobertura automatizada en `activities/tests/`. Los
tests DEBEN correr aislados contra `data/test.sqlite3`, usar relojes fijos
(`now` / `--reference-time`) donde el tiempo importe, y NO DEBEN exigir dos
suites compartiendo un mismo directorio de datos a la vez. `manage.py check` y
`makemigrations --check --dry-run` DEBEN pasar, en local o vía `exec` en el
contenedor.

### V. Seguridad Explícita de los Datos

El seed (`seed_demo`) DEBE ser idempotente: NO DEBE desplazar el ancla,
duplicar registros ni reescribir usuarios o ediciones en ejecuciones
repetidas, y DEBE informar lo omitido en lugar de sobrescribir. Los comandos
destructivos (`reset_demo`) REQUIEREN `--confirm` explícito, DEBEN anunciar
primero la base destino y sus efectos, y DEBEN preservar usuarios, contraseñas,
actividades ajenas y sus inscripciones. Ningún comando elimina datos por
defecto.

### VI. Sin Configuración Oculta

Toda configuración DEBE ser variables de entorno explícitas con valores
docentes por defecto (`DEMO_DATA_DIR`, `DJANGO_DEBUG`, `DJANGO_SECRET_KEY`);
Django NO DEBE autocargar `.env`. Ambas vías (`uv` local y Docker Compose)
DEBEN estar documentadas en `README.md`, atar loopback por defecto y tratar
esta demo como uso local no productivo con datos ficticios. Secretos y bases
SQLite NO DEBEN incluirse en exportaciones ni checkpoints.

## Stack Tecnológico y Límites de Despliegue

Stack fijo: Python 3.12.14, uv 0.12.19, Django 5.2.x, SQLite. La referencia es
Docker: imágenes fijadas en `Dockerfile`, `/opt/venv` aislado del `.venv` del
host (excluido del montaje). La vía local (`uv sync --locked` + `migrate` +
`seed_demo`) es alternativa válida con idénticos gates. SQLite serializa
escritores con timeout de 10s: adecuado para docencia local, explícitamente NO
para alta carga. Zona horaria de visualización: America/Argentina/Ushuaia.
Puertos por defecto en 8000 loopback; el puerto 8016 es solo ejemplo para
copias restauradas.

## Flujo de Desarrollo con Docker

El ciclo diario DEBE ser: `docker compose up --build`, trabajar con recarga,
`docker compose exec web uv run --locked python manage.py test --noinput`
para verificar, `docker compose stop` / `start` para pausar y continuar. Los
gates previos a merge DEBEN ejecutarse dentro del contenedor cuando se
trabaja en Docker: `test --noinput`, `check`, `makemigrations --check
--dry-run`. Las migraciones DEBEN acompañar cambios de modelos; los
guardarraíles (`one_registration_per_student_activity`, `positive_capacity`)
NO DEBEN debilitarse sin enmienda. La administración de inscripciones sigue
siendo de consulta: NO DEBE crear atajos que eludan las reglas de inscripción.
Todo cambio DEBE pasar revisión que verifique cumplimiento constitucional, con
la complejidad justificada en el PR.

## Gobernanza

Esta constitución prevalece sobre cualquier otra práctica del proyecto. Las
enmiendas requieren propuesta documentada, aprobación y plan de migración para
código y tests afectados. Versionado semántico: MAJOR para eliminaciones o
redefiniciones incompatibles de gobernanza o principios, MINOR para principios
nuevos o guía materialmente ampliada, PATCH para aclaraciones y redacción. La
revisión de cumplimiento es obligatoria en cada PR: quien revisa DEBE confirmar
la adhesión o registrar una excepción explícita y justificada con un issue de
enmienda de seguimiento.

**Versión**: 1.1.0 | **Ratificada**: 2026-10-16 | **Última enmienda**: 2026-10-16

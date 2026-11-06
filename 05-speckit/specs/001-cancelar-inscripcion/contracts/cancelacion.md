# Contrato UI: Cancelación de inscripción propia

**Fecha**: 2026-10-16 | Fuente: `spec.md` historias 1–3, FR-001–FR-010

El proyecto expone vistas server-rendered (sin API externa); este contrato
describe rutas, métodos, visibilidad y mensajes de la feature.

## Rutas

### `my-registrations/` (existente, extendida)

- Muestra las inscripciones del usuario autenticado: activas y canceladas.
- Cada tarjeta indica estado con insignia ("Confirmada" / "Cancelada"); las
  canceladas exhiben además su fecha de cancelación.
- El botón "Cancelar" aparece solo cuando la cancelación sería permitida:
  inscripción activa, actividad no iniciada y solicitud dentro del plazo de
  24h (aplica igual a deshabilitadas futuras).
- Solo inscripciones propias: nunca se listan ni accionan las de otros.

### `activities/<pk>/cancel/` (nueva)

- **GET**: pantalla de confirmación dedicada con resumen (actividad, fecha de
  inicio, límite de 24h) y botón de confirmación. Si la cancelación no es
  permitida (fuera de plazo, ya iniciada, ya cancelada, ajena o inexistente),
  muestra el mensaje correspondiente y redirige a "mis inscripciones".
- **POST**: ejecuta la cancelación, emite el mensaje de resultado y redirige
  a "mis inscripciones". Mutación solo por POST (coherente con `enroll` y
  `salir`); GET nunca muta.

## Regla de inscripción con cancelada previa (actualización)

- Intentar inscribirse a una actividad donde el estudiante tiene una
  inscripción cancelada es rechazado con mensaje claro de no-reinscripción
  (la unicidad por par lo respalda).

## Mensajes (español, vía MESSAGES + messages framework)

Vocabulario cerrado: estas son las claves exactas de `MESSAGES` en
`activities/services.py`. No se agregan alias ni traducciones de clave.

| Clave              | Cuándo se emite                              |
|--------------------|----------------------------------------------|
| `cancelled`        | cancelación confirmada y aplicada            |
| `too_late`         | solicitud dentro de las 24h previas          |
| `started`          | actividad con inicio alcanzado o pasado      |
| `already_cancelled`| intento sobre una inscripción ya cancelada   |
| `no_resubscribe`   | intento de reinscripción tras cancelar       |
| `not_available`    | actividad o inscripción no encontrada        |
| `busy`             | contención transitoria (reintentable)        |

La misma clave se usa como `extra_tags` del mensaje. `cancel_block_reason()`
es la única función que decide entre `too_late`, `started` y
`already_cancelled`; las vistas solo la consumen.

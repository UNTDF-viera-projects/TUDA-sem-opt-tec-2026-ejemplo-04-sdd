# Proposal

## Why

Los usuarios inscriptos no pueden cancelar su inscripción. Se necesita una cancelación que libere el cupo pero impida la re-inscripción (por ahora), con ventana de 24 horas previas al inicio.

## What Changes

- Nueva capacidad de cancelación de inscripción con memoria persistente (tombstone).
- Nuevo modelo `Cancellation` (`student`, `activity`, `cancelled_at` con `auto_now_add`, unique por par, `CASCADE`).
- Nuevo servicio `cancel()` con transacción `IMMEDIATE`: verifica existencia, evalúa `now` después del lock, exige `starts_at - now >= 24h`, ignora `is_active`, ejecuta `DELETE` de `Registration` + `INSERT` de `Cancellation` en forma atómica.
- `register()` agrega chequeo de tombstone: si existe `Cancellation`, rechaza con el mismo mensaje de cancelación (sin re-inscripción).
- Nueva ruta POST `activities/<pk>/cancel/` con `login_required` + `require_POST`, identidad desde la sesión.
- Vistas `detail` y `mine` consultan el tombstone: el cancelado ve su fecha en lugar del botón de inscripción.
- `mine` muestra sección de canceladas con fecha `DD/MM/YYYY` y hora `HH:mm` (24h, cero adelante, sin lugar).
- Mensaje único parametrizado: `Ya cancelaste tu inscripción el DD/MM/YYYY a las HH:mm`, usado tanto para doble cancelación (idempotente) como para intento de re-inscripción.
- `CancellationAdmin` read-only, igual que `RegistrationAdmin`.

## Capabilities

### New Capabilities

- `registration`: ciclo de vida de la inscripción (inscribir, cancelar con ventana de 24h, bloqueo de re-inscripción con fecha visible).

### Modified Capabilities

- Ninguna (no existen specs previas).

## Impact

- Afecta: `activities/models.py`, `activities/services.py`, `activities/views.py`, `activities/urls.py`, `templates/activities/mine.html`, `templates/activities/detail.html`, `activities/admin.py`.
- `MESSAGES` deja de ser estático para el caso de cancelación (requiere interpolación de fecha en zona `America/Argentina/Ushuaia`).
- `seed_demo`: si un usuario seed cancela, el próximo seed preserva la cancelación y emite warning (no restaura).
- `reset_demo`: sin cambios (el `CASCADE` limpia tombstones de actividades demo).
- Tests: éxito, ventana exacta de 24h, deshabilitada que sí cancela, doble-cancel idempotente, reintento bloqueado, concurrencia.

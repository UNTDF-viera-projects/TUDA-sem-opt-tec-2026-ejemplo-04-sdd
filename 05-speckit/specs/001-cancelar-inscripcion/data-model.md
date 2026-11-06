# Data Model: Cancelar inscripción propia

**Fecha**: 2026-10-16 | Fuente: `spec.md` (FR-001–FR-010, Key Entities)

## Entidades

### Inscripción (existente, extendida)

Vínculo entre un estudiante y una actividad. Campos actuales: `activity`,
`student`, `created_at`. Esta feature agrega:

- **estado**: activa o cancelada. Valor para registros existentes y nuevos:
  activa.
- **momento de cancelación**: nulo mientras está activa; se registra al
  cancelar y nunca cambia después.

Relaciones: sin cambios (FK a actividad con `related_name="registrations"`,
FK al usuario). Orden y unicidad por par (estudiante, actividad) sin cambios:
la unicidad vigente es la que bloquea la reinscripción en esta versión.

### Actividad (sin cambios)

Con inicio, capacidad y habilitada. Su disponibilidad = capacidad menos
inscripciones **activas** (las canceladas no ocupan cupo).

## Reglas de validación

- El momento de cancelación tiene valor si y solo si el estado es cancelada.
- No se puede reducir la capacidad por debajo de las inscripciones activas
  (la guarda existente se evalúa sobre activas, no sobre el total histórico).
- La unicidad por par (estudiante, actividad) se conserva: un segundo registro
  para el mismo par es inválido aunque el anterior esté cancelado.

## Transiciones de estado

```text
activa ──cancelar (a tiempo, confirmada)──▶ cancelada
activa ──intento fuera de plazo / ya iniciada──▶ activa (sin cambios)
cancelada ──nuevo intento de cancelar──▶ cancelada (denegado, sin cambios)
cancelada ──intento de reinscribirse──▶ cancelada (rechazado, sin cambios)
```

No existe transición de vuelta a activa en esta versión (la reinscripción es
alcance futuro). La transición es unidireccional y de una sola aplicación: una
doble ejecución concurrente libera el cupo exactamente una vez.

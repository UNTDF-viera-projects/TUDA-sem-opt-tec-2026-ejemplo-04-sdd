# Feature Specification: Cancelar inscripción propia

**Feature Branch**: `001-cancelar-inscripcion`

**Created**: 2026-10-16

**Status**: Implemented

**Input**: User description: "quiero implementar la funcionalidad de cancelar inscripciones propias, con una restricción de 24hs antes del inicio, quiero que se conserve el registro y que al cancelar se libere el cupo. De momento, la persona no se puede reinscribir, dejaremos esto para más adelante"

## Clarifications

### Session 2026-10-16

- Q: ¿Cómo debe confirmar el estudiante la cancelación de su inscripción? → A: Pantalla de confirmación dedicada con resumen y botón para confirmar (opción A).
- Q: ¿Debe poder cancelarse una inscripción a una actividad futura que fue deshabilitada por administración? → A: Permitir si faltan más de 24h, igual que en actividades habilitadas (opción B).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Cancelar inscripción propia a tiempo (Priority: P1)

Un estudiante autenticado entra a "mis inscripciones", elige una actividad que
comienza en más de 24 horas, ve una pantalla de confirmación con el resumen
(actividad, fecha, límite de 24h), confirma y deja de figurar como
inscripto activo en ella.

**Why this priority**: Es el valor central de la funcionalidad: da autonomía al
estudiante y libera el cupo para otros a tiempo.

**Independent Test**: Con una inscripción activa a una actividad que inicia en
+48h, cancelar desde "mis inscripciones" y verificar que la inscripción queda
cancelada y el cupo disponible de la actividad aumenta en uno.

**Acceptance Scenarios**:

1. **Given** una inscripción activa a una actividad que inicia en más de 24h,
   **When** el estudiante confirma la cancelación, **Then** la inscripción pasa
   a estado cancelada y el cupo queda liberado.
2. **Given** una cancelación exitosa, **When** el proceso termina, **Then** el
   estudiante ve un mensaje claro de confirmación.
3. **Given** una inscripción activa a una actividad deshabilitada que inicia en
   más de 24h, **When** el estudiante confirma la cancelación, **Then** la
   inscripción pasa a estado cancelada y el cupo queda liberado.

---

### User Story 2 - Cancelación bloqueada dentro de las 24 horas (Priority: P2)

Un estudiante intenta cancelar una inscripción a una actividad que comienza en
menos de 24 horas (o que ya comenzó): el sistema lo deniega con un mensaje
claro, la inscripción sigue activa y el cupo no cambia.

**Why this priority**: Protege la restricción de negocio de las 24h; sin ella,
la funcionalidad pierde su regla principal.

**Independent Test**: Con una inscripción activa a una actividad que inicia en
+12h, intentar cancelar y verificar que la inscripción sigue activa y el cupo
no cambia.

**Acceptance Scenarios**:

1. **Given** una inscripción activa a una actividad que inicia en menos de 24h,
   **When** el estudiante intenta cancelarla, **Then** el sistema deniega la
   operación con un mensaje claro y la inscripción permanece activa.
2. **Given** una actividad ya iniciada, **When** el estudiante intenta cancelar
   su inscripción, **Then** el sistema deniega la operación y nada cambia.

---

### User Story 3 - Historial conservado y sin reinscripción (Priority: P3)

La inscripción cancelada sigue visible como cancelada (con su fecha) en "mis
inscripciones" y para consulta administrativa; si el estudiante intenta
inscribirse de nuevo a esa misma actividad, el sistema lo rechaza con un
mensaje claro. El cupo liberado queda disponible para otros estudiantes.

**Why this priority**: Garantiza la trazabilidad pedida (conservar el registro)
y el comportamiento explícito de no-reinscripción de esta versión.

**Independent Test**: Tras cancelar, verificar que el registro sigue visible
como cancelado, que un intento de reinscripción a la misma actividad es
rechazado, y que otro estudiante puede ocupar el cupo liberado.

**Acceptance Scenarios**:

1. **Given** una inscripción cancelada, **When** el estudiante revisa "mis
   inscripciones", **Then** el registro sigue visible como cancelado con su
   fecha de cancelación.
2. **Given** una inscripción cancelada, **When** el mismo estudiante intenta
   inscribirse de nuevo a esa actividad, **Then** el sistema rechaza la
   reinscripción con un mensaje claro.
3. **Given** un cupo liberado por cancelación, **When** otro estudiante se
   inscribe a esa actividad, **Then** la inscripción del nuevo estudiante se
   confirma normalmente.

---

### Edge Cases

- Límite exacto de 24h: la cancelación es permitida si la solicitud ocurre en o
  antes de (inicio − 24h); denegada si ocurre después.
- Actividad deshabilitada pero futura: aplica la misma regla de 24h que las
  habilitadas (permitida a tiempo, denegada dentro del plazo). Actividad ya
  iniciada: la cancelación es denegada y el registro queda intacto.
- Inscripción ya cancelada: un segundo intento de cancelación es denegado sin
  modificar el cupo.
- Inscripción ajena: un estudiante nunca ve ni puede accionar cancelación sobre
  inscripciones de otros.
- Cancelaciones concurrentes sobre la misma inscripción: solo una tiene efecto
  y el cupo se libera exactamente una vez.
- Falla técnica a mitad del proceso: sin efecto parcial (la inscripción queda
  activa o queda cancelada, nunca en estado intermedio ni con cupo duplicado).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El estudiante autenticado DEBE poder cancelar sus propias
  inscripciones activas desde "mis inscripciones".
- **FR-002**: La cancelación DEBE permitirse solo si el momento efectivo de la
  solicitud —evaluado con el reloj real tras adquirir la reserva de
  escritura— es anterior o igual a (inicio de la actividad − 24 horas); fuera
  de ese plazo DEBE denegarse con un mensaje claro, sin modificar inscripción
  ni cupo.
- **FR-003**: La cancelación NO DEBE eliminar el registro; DEBE marcar la
  inscripción como cancelada registrando el momento de cancelación, y el
  registro DEBE seguir visible como cancelado.
- **FR-004**: La inscripción cancelada NO DEBE ocupar cupo; la disponibilidad de
  la actividad DEBE actualizarse de inmediato tras cancelar.
- **FR-005**: El intento de reinscribirse a una actividad con inscripción
  cancelada DEBE ser rechazado con un mensaje claro en esta versión.
- **FR-006**: El sistema NO DEBE ofrecer ni permitir la cancelación de
  inscripciones de otros estudiantes.
- **FR-007**: La cancelación DEBE requerir una confirmación explícita del
  estudiante en una pantalla de confirmación dedicada (con resumen de actividad,
  fecha y límite de 24h) antes de efectivizarse.
- **FR-008**: Cada resultado (confirmada, fuera de plazo, ya cancelada, no
  reinscribible, inscripción inexistente) DEBE comunicarse con un mensaje claro
  en español.
- **FR-009**: Ante solicitudes concurrentes sobre la misma inscripción, el cupo
  DEBE liberarse exactamente una vez y el resultado DEBE ser consistente.
- **FR-010**: Si la actividad ya inició, la cancelación DEBE denegarse y el
  registro DEBE quedar intacto. Si la actividad está deshabilitada pero aún no
  inició, aplica la misma regla de 24h que en las habilitadas (FR-002).

### Key Entities *(include if feature involves data)*

- **Inscripción**: Vínculo entre estudiante y actividad. Tiene estado
  (activa / cancelada) y conserva el momento de creación y el de cancelación.
  La unicidad por par estudiante–actividad se mantiene, lo que bloquea la
  reinscripción en esta versión.
- **Actividad**: Tiene inicio y capacidad. Su disponibilidad es la capacidad
  menos las inscripciones activas (las canceladas no ocupan cupo).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un estudiante completa una cancelación a tiempo en menos de 1
  minuto desde "mis inscripciones".
- **SC-002**: El 100 % de las cancelaciones conserva el registro visible como
  cancelado, con su fecha.
- **SC-003**: Cada cancelación libera exactamente un cupo, visible de inmediato
  para otros estudiantes.
- **SC-004**: El 0 % de los intentos dentro de las 24 horas previas al inicio
  modifica inscripciones o cupos.
- **SC-005**: El 100 % de los intentos de reinscripción a una actividad con
  inscripción cancelada es rechazado con un mensaje claro.

## Assumptions

- Límite inclusivo: cancelación permitida en o antes de (inicio − 24h).
- La hora de referencia es la misma zona de visualización del proyecto
  (America/Argentina/Ushuaia).
- Solo el propio estudiante cancela sus inscripciones; la vía docente /
  administrativa no cancela inscripciones ajenas en esta versión.
- La reinscripción queda explícitamente fuera de alcance y se retomará más
  adelante.
- La confirmación es una pantalla dedicada con resumen, para evitar
  cancelaciones accidentales, coherente con las vistas clásicas del proyecto.
- Los mensajes de usuario están en español, consistentes con los actuales.
- La verificación se hace en el flujo Docker canónico según la constitución
  vigente.

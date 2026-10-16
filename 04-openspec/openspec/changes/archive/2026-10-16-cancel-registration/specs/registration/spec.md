# Spec Delta

## Purpose

Permite a cada estudiante cancelar su propia inscripción hasta 24 horas antes del inicio, liberando el cupo e impidiendo la re-inscripción con un mensaje que muestra la fecha de cancelación.

## ADDED Requirements

### Requirement: Cancelación dentro de la ventana de 24 horas

El sistema DEBE (SHALL) permitir a un estudiante cancelar su propia inscripción solo cuando la actividad comience al menos 24 horas después del instante de cancelación, sin importar si la actividad está habilitada.

#### Scenario: Cancelación con más de 24 horas de anticipación

- **WHEN** un estudiante inscripto cancela una actividad habilitada que inicia en 48h
- **THEN** la inscripción se elimina, se crea un registro de cancelación y se informa el éxito

#### Scenario: Cancelación exactamente a las 24 horas permitida

- **WHEN** un estudiante inscripto cancela cuando `starts_at - now` es exactamente 24h
- **THEN** la cancelación tiene éxito

#### Scenario: Cancelación dentro de la ventana de 24 horas rechazada

- **WHEN** un estudiante inscripto cancela una actividad que inicia en 23:59:59 o menos
- **THEN** nada se elimina y se informa un mensaje de fuera de término

#### Scenario: Actividad deshabilitada sigue la misma ventana

- **WHEN** un estudiante inscripto cancela una actividad deshabilitada que inicia en 48h
- **THEN** la cancelación tiene éxito bajo la misma regla de 24h

#### Scenario: El reloj se evalúa después de adquirir el lock de escritura

- **WHEN** una cancelación espera al escritor y la actividad entra en la ventana de 24h mientras tanto
- **THEN** el sistema informa fuera de término y no elimina nada

### Requirement: La cancelación libera cupo

El sistema DEBE (SHALL) liberar exactamente un cupo cuando una cancelación tiene éxito, visible a través de la disponibilidad.

#### Scenario: El cupo queda disponible

- **WHEN** una cancelación tiene éxito en una actividad con 0 cupos disponibles
- **THEN** la disponibilidad aumenta en 1 y el catálogo lo refleja

### Requirement: Sin re-inscripción, con mensaje fechado

El sistema DEBE (SHALL) bloquear la re-inscripción de un par (estudiante, actividad) cancelado e informar `Ya cancelaste tu inscripción el DD/MM/YYYY a las HH:mm` usando el instante de cancelación guardado.

#### Scenario: Estudiante cancelado intenta reinscribirse

- **WHEN** un estudiante con registro de cancelación intenta inscribirse en la misma actividad
- **THEN** no se crea ninguna inscripción y se informa el mensaje fechado

#### Scenario: Doble cancelación idempotente con el mismo mensaje

- **WHEN** un estudiante cancela la misma actividad dos veces
- **THEN** el segundo pedido no cambia nada e informa el mismo mensaje fechado con el instante original

### Requirement: Visualización de la fecha de cancelación

El sistema DEBE (SHALL) mostrar el instante de cancelación como `DD/MM/YYYY` y `HH:mm` (con cero adelante, 24h), convertido a `America/Argentina/Ushuaia`, sin texto de lugar.

#### Scenario: El historial muestra la fecha formateada

- **WHEN** un estudiante ve sus inscripciones después de cancelar el 03/10/2030 a las 14:05 de Ushuaia
- **THEN** ve `el 03/10/2030 a las 14:05`

#### Scenario: El detalle informa en lugar de ofrecer inscripción

- **WHEN** un estudiante cancelado abre el detalle de la actividad
- **THEN** ve el mensaje de cancelación fechado y ningún botón de inscripción

### Requirement: Seguridad del endpoint de cancelación

El sistema DEBE (SHALL) exigir autenticación, método POST y CSRF para la cancelación, tomando la identidad exclusivamente de la sesión.

#### Scenario: Cancelación anónima o por GET rechazada

- **WHEN** un usuario anónimo abre la URL de cancelación o cualquiera hace GET
- **THEN** se exige login y nada cambia; el GET no muta estado

#### Scenario: La identidad del formulario se ignora

- **WHEN** un POST de cancelación incluye el id de otro estudiante
- **THEN** solo se ve afectada la inscripción del usuario de la sesión

### Requirement: El seed preserva las cancelaciones

El sistema DEBE (SHALL) preservar las cancelaciones existentes al repetir el seed, emitiendo un aviso en lugar de restaurar la inscripción.

#### Scenario: Re-seed después de cancelar

- **WHEN** `seed_demo` corre después de que un usuario seed canceló una actividad seed
- **THEN** la cancelación permanece y el comando informa el estado preservado

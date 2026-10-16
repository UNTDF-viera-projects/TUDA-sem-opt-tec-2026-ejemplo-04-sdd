# Spec Delta

## Purpose

Permite a cada estudiante cancelar su propia inscripción hasta 24 horas antes del inicio, liberando el cupo e impidiendo la re-inscripción con un mensaje que muestra la fecha de cancelación.

## ADDED Requirements

### Requirement: Cancel within 24-hour window

The system SHALL allow a student to cancel their own registration only when the activity starts at least 24 hours after the cancellation instant, ignoring whether the activity is enabled.

#### Scenario: Cancel more than 24 hours before start

- **WHEN** an enrolled student cancels an enabled activity starting in 48h
- **THEN** the registration is removed, a cancellation record is created, and success is reported

#### Scenario: Cancel exactly at 24 hours is allowed

- **WHEN** an enrolled student cancels when `starts_at - now` equals exactly 24h
- **THEN** the cancellation succeeds

#### Scenario: Cancel inside 24-hour window is rejected

- **WHEN** an enrolled student cancels an activity starting in 23:59:59 or less
- **THEN** nothing is deleted and a too-late message is reported

#### Scenario: Disabled activity follows the same window

- **WHEN** an enrolled student cancels a disabled activity starting in 48h
- **THEN** the cancellation succeeds under the same 24h rule

#### Scenario: Clock is evaluated after acquiring the write lock

- **WHEN** a cancel waits for the writer and the activity enters the 24h window meanwhile
- **THEN** the system reports too-late and deletes nothing

### Requirement: Cancellation frees capacity

The system SHALL free exactly one seat when a cancellation succeeds, visible through availability.

#### Scenario: Seat becomes available

- **WHEN** a cancellation succeeds on an activity with 0 seats available
- **THEN** availability increases by 1 and the catalog reflects it

### Requirement: No re-entry with dated message

The system SHALL block re-registration of a cancelled (student, activity) pair and report `Ya cancelaste tu inscripción el DD/MM/YYYY a las HH:mm` using the stored cancellation instant.

#### Scenario: Cancelled student tries to re-register

- **WHEN** a student with a cancellation record attempts to register for the same activity
- **THEN** no registration is created and the dated message is reported

#### Scenario: Double cancel is idempotent with the same message

- **WHEN** a student cancels the same activity twice
- **THEN** the second request changes nothing and reports the same dated message with the original instant

### Requirement: Cancellation date display

The system SHALL display the cancellation instant as `DD/MM/YYYY` and `HH:mm` (zero-padded, 24h), converted to `America/Argentina/Ushuaia`, without location text.

#### Scenario: History shows formatted date

- **WHEN** a student views their registrations after cancelling on 03/10/2030 at 14:05 Ushuaia
- **THEN** they see `el 03/10/2030 a las 14:05`

#### Scenario: Detail view informs instead of offering enrollment

- **WHEN** a cancelled student opens the activity detail
- **THEN** they see the dated cancellation message and no enrollment button

### Requirement: Cancel endpoint security

The system SHALL require authentication, POST method, and CSRF for cancellation, taking identity exclusively from the session.

#### Scenario: Anonymous or GET cancel is rejected

- **WHEN** an anonymous user opens the cancel URL or anyone issues GET
- **THEN** login is required and no state changes; GET does not mutate

#### Scenario: Form identity is ignored

- **WHEN** a cancel POST includes another student's id
- **THEN** only the session user's own registration is affected

### Requirement: Seed preserves cancellations

The system SHALL preserve existing cancellations on re-seed, emitting a warning instead of restoring the registration.

#### Scenario: Re-seed after cancel

- **WHEN** `seed_demo` runs after a seed user cancelled a seed activity
- **THEN** the cancellation remains and the command reports the preserved state

# Diseño

## Contexto

Ver `proposal.md` (Motivo). Estado actual: `register()` en `activities/services.py:19-41` corre en `atomic` con SQLite `IMMEDIATE` (`config/settings.py:14`), evalúa `now` después del lock y ordena los chequeos (duplicado primero). `Registration` tiene unique `(student, activity)` (`activities/models.py:27`). No existe baja: ver exploración en la conversación del change. `reset_demo.py:20` borra actividades seed con `CASCADE`.

## Objetivos / No objetivos

**Objetivos:**

- Cancelación con ventana de 24h, memoria permanente (tombstone) y mensaje con fecha.
- Radio de impacto mínimo: conteos, `available`, `clean()` y tests de concurrencia existentes intactos.
- Reversibilidad: habilitar re-inscripción a futuro sin migrar datos (solo dejar de chequear el tombstone).

**No objetivos:**

- Re-inscripción, lista de espera, baja administrativa, expiración del tombstone.
- Cambio de motor de BD o de estrategia de concurrencia.

## Decisiones

1. **Tombstone `Cancellation` en lugar de `status` en `Registration`.**
   Fundamento: `count()`, `with_availability()`, `clean()` y el unique parcial no se tocan; un solo `EXISTS` nuevo en `register()`. Alternativa A (flag + `Count(filter=active)` + unique parcial) se descartó por mayor radio de impacto y sutileza en SQLite.

2. **Modelo: `student FK + activity FK + cancelled_at auto_now_add`, unique por par, `CASCADE`.**
   Fundamento: fecha inmutable gratis para el mensaje y la UI; el `delete()` de actividades demo en `reset_demo` limpia tombstones sin código extra. Alternativa (timestamp seteado a mano) se descartó por mutabilidad innecesaria.

3. **`cancel()` espejo asimétrico de `register()`: `IMMEDIATE` → existe `Registration`? → `now` post-lock → ventana `starts_at - now >= 24h` → `DELETE + INSERT` atómico; `is_active` se ignora.**
   Fundamento: misma protección contra la race del reloj que motivó la v2 de `register()`; el límite inclusivo (`>= 24h`) es el más testeable con `timedelta(hours=24)`.

4. **Orden de chequeos: existencia primero, ventana después; tombstone consultado en `register()` después de `already_registered`.**
   Fundamento: preserva la prioridad existente (duplicado gana) y hace la ventana robusta bajo contención. `locked` → `busy` reintentable, igual que `register()`.

5. **Mensaje único parametrizado fuera del dict estático `MESSAGES`.**
   Fundamento: `MESSAGES` hoy es `str` fijo; la fecha exige interpolación (`%d/%m/%Y %H:%M` en `America/Argentina/Ushuaia`). Doble-cancel y reintento comparten el mismo texto con el instante original.

6. **Vistas finas, sin lógica en templates: `cancel` (`login_required + require_POST`, identidad de sesión) + `detail`/`mine` que leen el tombstone.**
   Fundamento: evita que un cancelado vea el botón de inscripción (TOCTOU visual ya conocido en `views.py:18`); `mine` agrega una query de `Cancellation` para la sección histórica.

7. **`CancellationAdmin` de solo lectura como `RegistrationAdmin`.**
   Fundamento: coherente con "administración de consulta" del README; evita altas/bajas que eludan la ventana.

## Riesgos / Compromisos

- [Race doble-cancel / cancel-vs-register al último cupo] → Mitigación: misma transacción `IMMEDIATE` + unique en `Cancellation`; un ganador, el otro ve mensaje idempotente o `full`.
- [Doble fuente de verdad temporal (`created_at` vs `cancelled_at`)] → Mitigación: `cancelled_at` es la única fecha mostrada; `created_at` original se pierde al borrar (aceptado en el alcance).
- [Seed que choca con tombstone] → Mitigación: comportamiento definido (warning, preserva cancelación); documentado en spec y mensaje de seed existente.
- [`now` naive vs aware en el borde de 24h] → Mitigación: reutilizar `timezone.now()` y el parámetro `now` inyectable de tests, igual que `register()`.
- [Mensaje con fecha fuera de `MESSAGES`] → Mitigación: helper de formateo con zona explícita; tests fijan `NOW` como en `test_base.py:15`.

## Plan de migración

- Una migración: crear `Cancellation` (sin backfill; no hay cancelaciones históricas).
- Deploy: migraciones Django normales; rollback = revertir código + `migrate` hacia atrás (la tabla nueva queda vacía en la ventana del change).
- Sin cambios en `reset_demo` ni en variables de entorno.

## Preguntas abiertas

- Ninguna que cambie specs, enfoque o tareas. Detalle menor diferible: texto exacto del mensaje `too_late` (propuesta: `El período de cancelación cerró (hasta 24 horas antes del inicio).`).

# F1 · Plan de implementación — Cancelación de inscripciones

Estado: **resuelto — verificado contra tasks T01…T10**. Este documento no modifica ningún archivo de la aplicación; el código queda igual que en la entrega de la spec.

- Spec de referencia: `docs/f1/spec.md` (versión revisada).
- Código base: commit `72a68f4` («feat: demo base»), 22 pruebas, sin cambios de aplicación en esta entrega.
- Stack que se conserva sin variaciones: **Django clásico con templates, autenticación por sesión, SQLite (`transaction_mode: IMMEDIATE`, `timeout: 10`), uv y Docker**. No se introduce API, ORM alternativo, framework JavaScript, otro SGBD ni cola de tareas.

---

## 1. Hallazgos en la spec y correcciones propuestas

Encontrados al contrastar `spec.md` con el código. Se informan antes de continuar; el plan los asume, pero **no se edita `spec.md`**: la corrección queda pendiente de aprobación docente.

### F-01 · Faltan cinco claves en `MESSAGES`, no cuatro

- **Dónde:** `§6.5`, fila `activities/services.py`: «cuatro claves nuevas en `MESSAGES`».
- **Qué pasa:** los códigos nuevos definidos en §2 que no existen en `MESSAGES` (`activities/services.py:6-14`) son **cinco**: `cancelled`, `already_cancelled`, `window_closed`, `not_cancellable` y `not_reenrollable`. `busy` ya existe.
- **Efecto si no se corrige:** `enroll` renderiza `MESSAGES[result]` (`activities/views.py:27`), sin `get`. Una reinscripción rechazada con `not_reenrollable` (`F1-R20`, `F1-R21`) lanza `KeyError` y la vista responde `500`. La spec además exige que ese mensaje sea comprensible para el estudiante, es decir que su texto tiene que vivir en algún lado.
- **Corrección propuesta:** reemplazar «cuatro claves nuevas en `MESSAGES`» por **«cinco claves nuevas en `MESSAGES`: `cancelled`, `already_cancelled`, `window_closed`, `not_cancellable`, `not_reenrollable`»**.
- **Texto mínimo que aporta el plan** (estilo de los existentes, rioplatense, se renderiza con `.message` sin CSS nuevo):

  | Clave | Texto propuesto |
  | --- | --- |
  | `cancelled` | `Inscripción cancelada. Se liberó un cupo.` |
  | `already_cancelled` | `Esta inscripción ya estaba cancelada.` |
  | `window_closed` | `No podés cancelar: el plazo venció 24 h antes del inicio.` |
  | `not_cancellable` | `No se pudo cancelar esta inscripción.` (genérico: ajena, inexistente o actividad borrada) |
  | `not_reenrollable` | `Tu inscripción fue cancelada; la reinscripción no está habilitada.` |

### F-02 · `P-04` cuenta un alto directo en el seed; son dos

- **Dónde:** `§6.4`, `P-04`: «crea la inscripción en la actividad ya iniciada con `Registration.objects.create` directo… ¿Se acepta **ese único alta** que no pasa por el servicio?».
- **Qué pasa:** `D5`/`E-17` exigen dos inscripciones nuevas: Bruno en la actividad **deshabilitada** y Ana en la **iniciada**. `register()` rechaza ambas: `disabled` (`activities/services.py:28-29`) y `started` (`activities/services.py:31-32`). Ninguna de las dos puede crearse pasando por el servicio. La spec tampoco fija la regla de idempotencia de esas altas directas, necesaria porque `seed_demo` es repetible y debe conservar cancelaciones.
- **Efecto si no se corrige:** o `E-17` queda sin demostrar (la semilla de la actividad deshabilitada se salta con aviso en cada corrida), o el implementador crea solo una de las dos y el recorrido manual de `E-06` falla.
- **Corrección propuesta:** en `P-04` reemplazar «ese único alta» por **«esas dos altas directas (deshabilitada e iniciada), ninguna de las cuales pasa por `register()`»**, y añadir: **«ambas se guardan con la misma guarda de existencia que el resto del seed: si la fila `(student, activity)` ya existe —confirmada o cancelada— se omite y no se reescribe»**.

### F-03 · `F1-R26` depende de `M-02`, declarado fuera de alcance

- **Dónde:** `F1-R26` («la misma regla que el servicio usa para conceder debe decidir qué se muestra») vs. `§6.3`, donde `M-02` («un único método que calcule el instante límite y la elegibilidad, reutilizado por el servicio y por las vistas») figura como mejora «fuera del alcance mínimo de F1».
- **Qué pasa:** sin helper compartido, `F1-R26` solo se puede cumplir duplicando la fórmula del plazo en vistas y servicio, que es exactamente la divergencia que el requisito prohíbe.
- **Corrección propuesta:** **promover `M-02` al alcance de F1** como mecanismo de cumplimiento de `F1-R26`, manteniendo `M-01`, `M-03` a `M-08` fuera de alcance salvo los que el plan adopte explícitamente (`M-08`, ver §5.4).

Ninguna otra contradicción bloqueante: los números de línea de la spec (`services.py:16`, `:33`, `models.py:19`, `:27`, `admin.py:19`, `views.py:21-28`, `settings.py:14` y `:23`, `test_base.py:33-37`, `README.md:21` y `:74`) coinciden con el código actual.

---

## 2. Diseño propuesto y decisiones técnicas

### DD-01 · Un único campo `cancelled_at` nullable (D1, `F1-R08`, `F1-R12`)

Se agrega `Registration.cancelled_at = DateTimeField(null=True, blank=True)`. Sin `status`, sin modelo aparte, sin campo booleano redundante: la fila es su propio historial y `cancelled IS NULL / NOT NULL` es el estado. Motivo: un estado derivado guardado se contradice con el origen; acá no hay contradicción posible porque no hay segunda fuente de verdad. Estado terminal en F1: nada escribe `cancelled_at` dos veces (ver DD-05).

### DD-02 · Una sola propiedad derivada en el modelo (`F1-R29`)

```python
@property
def is_cancelled(self):
    return self.cancelled_at is not None
```

Plantillas, vistas y pruebas usan `is_cancelled`; nadie reescribe `cancelled_at is None` por su cuenta. Se descarta un `state` con texto (`"confirmada"/"cancelada"`) porque duplicaría vocabulario: la traducción vive en las plantillas (§2), el dato en el campo.

### DD-03 · Helper único de plazo y elegibilidad (corrección F-03; `F1-R04`, `F1-R05`, `F1-R26`)

En `activities/services.py`:

```python
WINDOW = timedelta(hours=24)

def cancellation_deadline(activity):
    return activity.starts_at - WINDOW          # instante límite L, sin redondeo

def can_cancel(*, registration, now):
    return registration.cancelled_at is None and now <= cancellation_deadline(registration.activity)
```

- `cancel()` usa `cancellation_deadline()` para conceder (`now > L` → `window_closed`).
- `detail` y `mine` usan `can_cancel()` para decidir el botón.

Una sola fórmula, dos consumidores: es lo que hace verificable `F1-R26`. Motivo del borde inclusivo (`<=`): `F1-R05`/`L-03`; compara con `register`, que usa borde exclusivo (`starts_at <= now` → `started`), asimetría deliberada documentada en §5.1.

### DD-04 · Cupo: los tres puntos cambian en el mismo commit (X-01, `F1-R11`)

El recuento pasa de «filas» a «confirmadas» en los tres lugares que hoy cuentan filas, sin excepciones:

| Punto | Hoy | Después |
| --- | --- | --- |
| `with_availability()` (`services.py:16-17`) | `Count("registrations")` | `Count("registrations", filter=Q(registrations__cancelled_at__isnull=True))` |
| `register()` cupo lleno (`services.py:33`) | `activity.registrations.count()` | `activity.registrations.filter(cancelled_at__isnull=True).count()` |
| `Activity.clean()` (`models.py:19`) | `self.registrations.count()` | `self.registrations.filter(cancelled_at__isnull=True).count()` |

Se usa `Count` con `filter=` (no `exclude` ni un segundo `annotate`) para conservar la semántica de join y que `available = capacity - occupied` siga siendo una resta de dos escalares por fila. Nota: el mensaje de `ValidationError` ya dice «inscripciones **confirmadas**»; el cambio hace que el código cumpla su propio texto (`L-22`: el texto actual vale).

### DD-05 · `cancel()`: contrato, orden de decisiones y escritura condicional

Firma espejo de `register`: `cancel(*, student, activity_id, now=None)` → código de resultado. Misma estructura transaccional y mismo manejo de errores que `activities/services.py:19-41`.

```python
def cancel(*, student, activity_id, now=None):
    try:
        with transaction.atomic():                    # BEGIN IMMEDIATE: toma la reserva de escritura ANTES de leer
            registration = (Registration.objects
                            .select_related("activity")
                            .filter(student=student, activity_id=activity_id).first())
            if registration is None:                  # ajena · inexistente · actividad borrada → misma rama (F1-R03, S-08, L-30)
                return "not_cancellable"
            if registration.cancelled_at is not None: # repetición ANTES que plazo (F1-R14) y sin leer el reloj (F1-R15)
                return "already_cancelled"
            now = now or timezone.now()               # reloj dentro de la transacción, tras el bloqueo (F1-R06)
            if now > cancellation_deadline(registration.activity):   # borde inclusivo (F1-R05)
                return "window_closed"
            updated = Registration.objects.filter(
                pk=registration.pk, cancelled_at__isnull=True        # escritura condicional (F1-R16)
            ).update(cancelled_at=now)
            if not updated:                           # otra transición ya ocurrió → defensa estructural
                return "already_cancelled"
            return "cancelled"
    except OperationalError as error:                 # solo contención conocida es recuperable (F1-R17)
        if "locked" in str(error).lower():
            return "busy"
        raise
```

Decisiones y motivos, ligados a la spec:

1. **Una sola consulta filtra por titular** (`student=request.user` llega desde la vista): la rama genérica única cubre inscripción ajena, inscripción inexistente y actividad inexistente/borrada (`F1-R03`, `E-03`/`E-04`/`E-05`, `L-13` a `L-15`, `L-30`). Como `Activity` borra en cascada sus `Registration`, «la fila existe» implica «la actividad existe», por lo que `L-30` cae en la misma rama sin una comprobación extra ni un `404`.
2. **La repetición se decide antes que el plazo y sin reloj** (`F1-R14`, `F1-R15`, `E-10`, `L-09` a `L-12`): `already_cancelled` se devuelve antes de tocar `timezone.now()`, así que una inscripción ya cancelada nunca puede volver `window_closed` aunque la actividad haya comenzado.
3. **No se consulta `is_active` en ningún punto** (`F1-R18`, `F1-R19`, `E-06`, `L-11`): la asimetría con `register` es intencional.
4. **`now` se lee dentro del `atomic`** (`F1-R06`): el `BEGIN IMMEDIATE` ocurre al entrar al bloque, de modo que toda lectura posterior —fila, `starts_at`, reloj— es posterior a cualquier espera por un escritor. Detalle completo en §7.
5. **Escritura condicional `WHERE cancelled_at IS NULL`** (`F1-R16`): defensa estructural si el `IMMEDIATE` dejara de aplicar. `.update()` no dispara `save()` ni reescribe el campo si otra transición ya lo puso (`F1-R09`), y devuelve número de filas: `0` → `already_cancelled`. El único `UPDATE` posible por transición es el que libera el cupo: exactamente uno (`F1-R10`, `E-02`, `L-17`, `L-19`).
6. **`OperationalError` con «locked» → `busy`; el resto se propaga** (`F1-R17`, `L-28`, `L-29`), calco de `services.py:37-41`.

### DD-06 · `register()`: rama de reinscripción y cupo con solo confirmadas (D3, `F1-R20` a `F1-R23`)

Cambio mínimo en `activities/services.py:26`, **misma posición de precedencia que hoy** (antes de `disabled`, `started` y `full`):

```python
registration = Registration.objects.filter(student=student, activity=activity).first()
if registration is not None:
    return "not_reenrollable" if registration.cancelled_at is not None else "already_registered"
```

Y en `:33`, el cupo lleno pasa a contar confirmadas (DD-04). Motivo: sin esto, `register()` afirma «Ya estás inscripto» sobre una fila cancelada (`X-02`, `F1-R21`) y la precedencia `E-12` (`not_reenrollable` gana sobre `disabled`/`started`/`full`) se incumple. La restricción `one_registration_per_student_activity` (`models.py:27`) sigue impidiendo la fila nueva; F1 no ofrece ninguna operación que borre `cancelled_at` (`F1-R23`). El test existente `test_duplicate_even_when_now_full_or_started` (`test_base.py:33-37`) sigue pasando porque la precedencia del duplicado **confirmado** no cambia.

### DD-07 · Vista `cancel_registration` (`F1-R01`, `F1-R02`, `F1-R24`)

```python
@login_required
@require_POST
def cancel_registration(request, pk):
    result = cancel(student=request.user, activity_id=pk)   # identidad SOLO de request.user (F1-R01)
    messages.info(request, MESSAGES[result], extra_tags=result)
    return redirect("mine")                                  # 302 a /my-registrations/ en TODOS los casos (F1-R24)
```

- **Sin `get_object_or_404`**: la URL es `activities/<int:pk>/cancel/`, que acepta cualquier entero; una actividad inexistente llega al servicio y devuelve `not_cancellable` con la misma respuesta (`E-05`). Un 404 aquí rompería `F1-R03`.
- Destino único `mine` para los cinco resultados: un destino por caso reintroduciría la fuga de `X-04`.
- `login_required` envuelve a `require_POST` (como `enroll`, `views.py:21-28`): anónimo → login; `GET` autenticado → `405`; sin CSRF → `403` (`E-14`, `L-24` a `L-26`).
- El mensaje usa `extra_tags=result`, igual que `enroll`, así que las claves nuevas heredan el estilo `.message` sin tocar `static/` (§6.5, cierre).

### DD-08 · URLs (`F1-R24`)

`activities/urls.py`: `path("activities/<int:pk>/cancel/", views.cancel_registration, name="cancel")`, junto a los cuatro patrones existentes. Nombre corto `cancel` para `{% url 'cancel' activity.pk %}`. El prefijo `activities/<int:pk>/` es idéntico al de `detail`, por lo que la ruta es por actividad (**D6**, `P-03` opción (a)) y no expone la inscripción como identificador.

### DD-09 · Vistas y templates (`F1-R25`, `F1-R26`)

**`detail`** (`views.py:15-19`) agrega dos claves de contexto:

- `can_cancel`: `can_cancel(registration=registration, now=timezone.now())` cuando hay inscripción (un solo `now` por petición).
- El resto se mantiene: `can_register = open_for_registration and registration is None` ya impide el botón de alta tras cancelar (§6.5, fila `detail.html`), comportamiento que se fija con prueba.

**`mine`** (`views.py:31-33`) mantiene `select_related("activity")` y agrega `cancellable_ids`, el conjunto de pks elegibles, calculado con `can_cancel()` y un único `now`:

```python
now = timezone.now()
registrations = Registration.objects.filter(student=request.user).select_related("activity")
cancellable_ids = {r.pk for r in registrations if can_cancel(registration=r, now=now)}
```

Se prefiere `cancellable_ids` a envolver cada fila en un diccionario para no reescribir el `{% for %}` de `mine.html`.

**`templates/activities/detail.html`** — estructura propuesta (se conserva el estilo de archivo único de la plantilla):

1. `registration` nula → rama actual (formulario de alta o «no admite nuevas inscripciones»).
2. `registration.is_cancelled` → badge «Cancelada» + `cancelled_at` con segundos (`d/m/Y H:i:s`, es un dato auditado, no un borde que el estudiante compare) + nota «La reinscripción no está habilitada». **Sin** «Tu inscripción está confirmada» (`F1-R25`) y sin botón de alta (`§6.5`).
3. `registration` confirmada y `can_cancel` → badge «Confirmada» + formulario `method="post"` con `{% csrf_token %}` y `action="{% url 'cancel' activity.pk %}"`.
4. `registration` confirmada fuera de plazo → badge «Confirmada» + la regla en texto («Cancelación disponible hasta 24 h antes del inicio»), **sin botón** (`F1-R26`, decisión `P-01` propuesta (c), ver §14).

**`templates/activities/mine.html`** — por inscripción: badge `Confirmada`/`Cancelada` + `cancelled_at` cuando corresponda, y el botón de cancelación dentro del `{% if %}` que usa `cancellable_ids` (misma regla que el servicio, `F1-R25`/`F1-R26`).

### DD-10 · Admin (`F1-R27`, `M-08`)

`activities/admin.py`, `RegistrationAdmin`:

- `list_display = ["student", "activity", "created_at", "cancelled_at"]` — el docente ve las bajas de un vistazo (`M-08`, adoptado porque `D2` exige alcance completo).
- `readonly_fields = ["student", "activity", "created_at", "cancelled_at"]` — solo lectura, sin alta (`has_add_permission` → `False`) ni baja (`has_delete_permission` → `False`, `admin.py:19`).
- `ActivityAdmin` **no cambia**: su `changeform_view` ya es `@transaction.atomic` con el `IMMEDIATE` de fondo; con `clean()` contando solo confirmadas, el docente puede bajar la capacidad hasta el número de inscripciones confirmadas (`E-16`, `L-21`, `L-22`).

Ningún camino del admin permite crear, editar o borrar `cancelled_at`, de modo que ninguna regla de dominio se puede eludir desde el panel (`README.md:74`).

### DD-11 · Seed y reinicios (`D5`, `F1-R28`, `P-04` corregido)

Ver §8.

---

## 3. Modelos y migración de inscripciones existentes

**Cambio de modelo** (`activities/models.py`):

1. `Registration.cancelled_at = models.DateTimeField("cancelación", null=True, blank=True)`.
2. Propiedad `is_cancelled` (DD-02).
3. `Activity.clean()` contando solo confirmadas (DD-04).

**Migración** (`activities/migrations/0002_*.py`, generada con `makemigrations`): `AddField` de `cancelled_at` como `null=True`. Es **aditiva y sin transformación de datos**:

- Todas las inscripciones existentes reciben `NULL`, es decir quedan **confirmadas**: su significado antes y después de la migración es idéntico y **`available` no cambia en el instante de la migración**. No hay backfill, no se reescribe ni toca `created_at`, no se toca el `UniqueConstraint`.
- En SQLite, `ALTER TABLE ADD COLUMN ... NULL` es una operación de metadata sobre una tabla con pocas filas (la demo tiene 4); no hay bloqueo prolongado ni reescritura de la tabla.
- Orden seguro: la columna existe antes de que cualquier código la lea; `services`, `views` y `admin` se implementan contra la migración ya aplicada.
- `makemigrations --check --dry-run` debe quedar limpio (`README.md:21`, `§6.6`).
- Comprobación de «inscripciones previas migran como confirmadas»:
  1. Prueba unitaria: una `Registration` creada sin `cancelled_at` tiene `is_cancelled is False`, sigue contando en el cupo y `available` no se altera.
  2. Verificación manual sobre una **copia** de `data/db.sqlite3` (nunca sobre la base de trabajo): `migrate` a `0002`, verificar `SELECT COUNT(*) ... WHERE cancelled_at IS NULL` igual al total de filas y `available` idéntico al previo.
- **Riesgo de reversa** (documentado en §10): revertir `0002` elimina la columna y con ella las fechas de cancelación; el plan recomienda avance, no reversa, y un respaldo de `data/db.sqlite3` antes de cada corrida manual.

Fuera de la migración, y por tanto **fuera de F1**: `M-06` (`CheckConstraint` `cancelled_at >= created_at`) y `M-05` (índice sobre `cancelled_at`) quedan anotados como mejoras futuras; con cinco actividades el índice no aporta.

---

## 4. Servicios, consultas de cupo y precedencias

Resumen de `activities/services.py` tras el cambio:

| Elemento | Cambio | IDs |
| --- | --- | --- |
| `WINDOW = timedelta(hours=24)` | constante única; la ventana no se repite en vistas ni en plantillas | `F1-R04` (y `M-01` queda cubierto) |
| `cancellation_deadline()` / `can_cancel()` | helper compartido servicio ↔ vistas | `F1-R05`, `F1-R26` (F-03) |
| `with_availability()` | `Count(..., filter=Q(cancelled_at__isnull=True))` | `F1-R11`, `E-15`, `L-20` |
| `cancel()` | nuevo, §DD-05 | `F1-R03` a `F1-R19` |
| `register()` | rama `not_reenrollable` en la posición del duplicado; cupo lleno sobre confirmadas | `F1-R20` a `F1-R23`, `F1-R11` |
| `MESSAGES` | cinco claves nuevas (corrección F-01) | `F1-R21` y códigos de §2 |

**Orden de decisiones en `cancel()`** (la precedencia es el requisito, no un detalle):

```
1. ¿Existe la fila (titular, actividad)?   no → not_cancellable   [genérica: ajena/inexistente/borrada]
2. ¿Ya estaba cancelada?                  sí → already_cancelled  [sin leer el reloj]
3. ¿now <= starts_at - 24 h?              no → window_closed      [reloj leído dentro del IMMEDIATE]
4. UPDATE condicional                     0 filas → already_cancelled; 1 fila → cancelled
```

**Orden en `register()`** (sin cambios salvo la rama nueva):

```
1. actividad inexistente   → not_available
2. fila existente confirmada → already_registered | cancelada → not_reenrollable
3. deshabilitada → disabled · 4. iniciada → started · 5. sin cupo (solo confirmadas) → full → crear
```

Los cuatro tests de precedencia del código base (`test_duplicate_even_when_now_full_or_started`, `test_full`, `test_exact_start_rejected`, `test_disabled`) siguen siendo la red de seguridad de que el orden no se movió.

---

## 5. Verificación de titularidad, plazo y repetición

### 5.1 Titularidad (`F1-R01` a `F1-R03`)

- **Implementación:** la única fuente de identidad es `request.user`, pasado como `student=` al servicio; el servicio filtra por `(student, activity_id)` en una sola consulta; no hay campo de usuario en el formulario ni parámetro de usuario en la URL.
- **Comprobación:**
  - `E-03` (ajena → `not_cancellable`, sin efecto), `E-04` (inexistente → igual), `E-05` (actividad inexistente → igual, sin `404`).
  - Prueba de **identidad de respuesta**: helper de test que compara, para `E-03` vs `E-04` vs `E-05`, las cuatro dimensiones de `F1-R03`: clave de mensaje, texto, `status_code` y `redirect_url`. Si alguna difiere, el test falla.
  - `L-13` a `L-16`: ajena con actividad deshabilitada/iniciada (no se revela nada), actividad inexistente autenticada, y que cancelar A no toca B.
  - `E-14` / `L-24` a `L-26`: `GET` → `405`; sin CSRF → `403`; anónimo → login (`config/settings.py:23`).

### 5.2 Plazo (`F1-R04` a `F1-R07`)

- **Implementación:** `WINDOW` de 24 h exactas, comparación `now <= L` sin redondeo, reloj leído dentro de la transacción, ancla al `starts_at` vigente.
- **Comprobación con reloj fijo** (`now=NOW`, patrón de `test_base.py`), en `test_cancel_service.py`, una prueba por fila de §5.1: `L-01` a `L-07` mapeadas 1:1 (`test_L03_deadline_inclusive_allows`, `test_L04_one_microsecond_past_rejected`, …), con `starts_at` y `now` construidos a microsegundos. Se incluye la asimetría de §5.1: el mismo archivo afirma que `register` rechaza en `starts_at == now` (`test_exact_start_rejected` existente) mientras `cancel` concede en `now == starts_at - WINDOW`.
- `L-08` (actividad ya iniciada del seed) y `E-08`: `window_closed`.
- `F1-R07`/`S-02`: prueba de que mover `starts_at` más adelante reabre el plazo y moverlo antes lo cierra, porque el límite se calcula sobre el valor vigente.
- `F1-R15`: con una inscripción ya cancelada, se parchea `activities.services.timezone.now` con un side-effect que **falla** si se le llama; `cancel()` sin `now` devuelve `already_cancelled` sin tocar el reloj.

### 5.3 Repetición (`F1-R13`, `F1-R14`)

- **Implementación:** rama `already_cancelled` antes de leer el reloj y antes de cualquier escritura; `.update()` condicional que no reescribe.
- **Comprobación:** `E-09` (dentro de plazo → conserva la fecha original, cupo intacto), `E-10` (fuera de plazo → `already_cancelled`, no `window_closed`), `L-09` a `L-12` (cancelada con plazo vencido, actividad deshabilitada, actividad iniciada), `L-16` (dos actividades del mismo titular), `L-19` (repetir no libera un segundo cupo). En todos: `cancelled_at` byte a byte idéntico al original y `available` sin cambios.

---

## 6. Protección de las operaciones concurrentes

Cuatro capas, ninguna sustituye a la anterior:

1. **`BEGIN IMMEDIATE` por transacción** (`config/settings.py:14`, `transaction_mode: IMMEDIATE`, `timeout: 10`): al entrar a `with transaction.atomic()` se adquiere la reserva de escritura de SQLite **antes** de la primera lectura. Dos cancelaciones simultáneas se serializan: la segunda espera y al continuar **ya ve** el `cancelled_at` de la primera. Es la misma base que usa `register` (`services.py:22`) y `ActivityAdmin.changeform_view` (`admin.py:9-11`); F1 no redefine el modelo transaccional (§1.1).
2. **Escritura condicional** `filter(pk=..., cancelled_at__isnull=True).update(...)`: defensa estructural exigida por `F1-R16`; aunque el `IMMEDIATE` no aplicara, la segunda transición no puede escribir y devuelve `already_cancelled`. `.update()` además garantiza que `F1-R09` (no reescribir la fecha) se cumple por construcción.
3. **Unicidad `(student, activity)`** (`models.py:27`): sostiene `F1-R10`/`S-05` — no hay multiplicidad que ajustar.
4. **`timeout` de 10 s → `busy`** (`F1-R17`): solo la contención conocida se vuelve recuperable y sin efecto parcial (la transacción revierte completa); cualquier otro `OperationalError` se propaga (`L-29`), sin enmascarar.

**Pruebas** (`test_cancel_concurrency.py`, `TransactionTestCase`, con el patrón ya probado de `ConcurrencyTests`: dos hilos, `Barrier`, archivo real `data/test.sqlite3`, conexiones cerradas al final):

- `E-13` / `L-23`: dos hilos cancelan la misma inscripción → resultados ⊆ `{cancelled, already_cancelled, busy}` con **a lo sumo un** `cancelled`; exactamente una fila cancelada; un único valor de `cancelled_at`; `available` baja 1, no 2.
- **Defensa estructural aislada**: dentro de una transacción se lee la fila confirmada, se escribe `cancelled_at` por otro camino (side-effect en el reloj, mismo patrón de parcheo que ya usa la suite) y se invoca la escritura condicional → 0 filas afectadas → `already_cancelled`, fecha original intacta.
- `L-28`: `OperationalError("database is locked")` simulado en `Registration.objects.filter` → `busy`, y verificación de que no quedó ningún efecto (la fila sigue confirmada). `L-29`: `OperationalError("broken schema")` → se propaga.

---

## 7. Decisión temporal correcta tras una espera por bloqueo

El punto crítico de `F1-R06`. Secuencia que la implementación garantiza y que la prueba verifica:

1. La petición entra a `cancel()` y ejecuta `with transaction.atomic()`. Con `transaction_mode: IMMEDIATE`, Django emite `BEGIN IMMEDIATE` **ahí**: si otro escritor (un `register`, una edición del admin, otra cancelación) tiene la reserva, esta petición **espera aquí**, antes de leer nada.
2. Recién después de la espera se lee la fila (posiblemente ya cancelada por quien esperábamos → `already_cancelled`, precedencia de `F1-R14`), se lee `starts_at` vigente (`F1-R07`, `S-02`: si el docente reprogramó mientras esperábamos, manda el valor nuevo) y **entonces** se hace `now = now or timezone.now()`.
3. Por eso el resultado se decide con el reloj **posterior** a la espera: si el plazo se cerró mientras esperábamos, devuelve `window_closed`, no `cancelled`. El parámetro `now` sigue siendo el reloj fijo de pruebas (`F1-R06`).
4. **Comprobación** (espejo exacto de `test_default_clock_after_lock_rejects_activity_that_started`, `test_base.py:137-147`):
   - `patch("activities.services.timezone.now", side_effect=after_lock)` donde `after_lock` **asserta** `connections["default"].in_atomic_block` (estamos dentro de la transacción) y devuelve un instante posterior al límite.
   - `clock.assert_called_once()` — el reloj se lee una única vez y solo en esa posición.
   - Resultado esperado: `window_closed`, fila intacta, `available` sin cambios.
   - Variante espejo: el side-effect devuelve un instante dentro del plazo → `cancelled`.
5. **Casca de errores:** si el `BEGIN IMMEDIATE` en sí agota el timeout, la excepción sale del `with` y el `try/except` externo (mismo orden que en `register`) la convierte en `busy` (`F1-R17`).

Ninguna lectura de reloj se hace en la vista ni fuera del `atomic`: mover `timezone.now()` a `cancel_registration` rompería esta garantía aunque el servicio siguiera correcto.

---

## 8. Seed, reinicios y conservación de cancelaciones

### 8.1 `seed_demo`

- **Conservación por construcción:** la guarda del seed es `if Registration.objects.filter(student=..., activity=...).exists(): continue` (`seed_demo.py:51-52`), es decir, comprueba **existencia de fila, no estado**. Una inscripción cancelada sigue existiendo → el seed la salta y **no reescribe `cancelled_at`, ni `created_at`, ni el cupo**. Es la misma razón por la que hoy no duplica registros (`README.md:52`).
- **Altas nuevas (corrección F-02):** se agregan dos filas al listado de escenarios —Bruno en `deshabilitada` y Ana en `iniciada` (`E-17`) — creadas con `Registration.objects.create(...)` **dentro del `@transaction.atomic` del comando** y con la misma guarda de existencia previa. Ninguna pasa por `register()`: `disabled` y `started` las rechazarían (`services.py:28`, `:31`). Si la fila ya existe (confirmada o cancelada) se omite; así el seed sigue siendo idempotente y **no revive cancelaciones**.
- **Las cuatro altas que sí pasan por `register()`** no cambian. Si una de ellas fue cancelada, el `exists()` de arriba la salta antes de llegar a `register()`, por lo que tampoco hay intento de `not_reenrollable` ni aviso espurio en cada corrida.
- **`reset_demo` no cambia** (`F1-R28`): elimina las cinco actividades por `seed_key` y la cascada borra sus inscripciones, **incluidas las canceladas**, y también el ancla; luego re-crea todo confirmado para la nueva clase. El mensaje del comando ya anuncia «elimina las 5 actividades ficticias y sus inscripciones» (`reset_demo.py:16`), comportamiento documentado en `README.md:60`.

### 8.2 Reinicios y migración automática

- **`docker compose stop` / `start` y `up --build` conservan las cancelaciones**, porque el estado vive en `data/db.sqlite3` y el contenedor solo lo lee. Con el `compose.yaml` vigente, `DEMO_DATA_DIR=/app/data` sobre el bind mount `.:/app`, así que el archivo pertenece al repositorio y sobrevive reconstrucciones de imagen. El `entrypoint` ejecuta `migrate` al arrancar (`README.md:38`), de modo que el arranque posterior a F1 aplica `0002` solo y las inscripciones previas quedan confirmadas (§3).
- **`seed_demo` en cada arranque** no altera cancelaciones (8.1).
- Solo dos caminos pierden cancelaciones, ambos documentados: `reset_demo --confirm` (`F1-R28`) y borrar/restaurar la base.
- **Observación fuera de la spec:** `README.md:38` y `:48` siguen nombrando el volumen `sdd-base_sqlite-data`, que el `compose.yaml` actual ya no declara. Convendrá alinear el README con el compose (o revertir el compose) en la tarea de documentación; no afecta las reglas de F1.

### 8.3 Respaldos

Antes de cada corrida manual de demostración: copia de `data/db.sqlite3` (por ejemplo `cp data/db.sqlite3 data/db.sqlite3.bak`). Es la única recuperación posible de cancelaciones reales una vez aplicado `reset_demo`.

---

## 9. Estrategia de pruebas, ejecución y recuperación

### 9.1 Organización de las pruebas

Se conserva `activities/tests/test_base.py` (22 pruebas) intacto como red de seguridad de la base. Los tests nuevos van en tres módulos nuevos, importando `NOW` y el factory `activity()` de `test_base` para no duplicarlos:

| Módulo | Contenido | IDs cubiertos |
| --- | --- | --- |
| `activities/tests/test_cancel_service.py` | `cancel()` y helper de plazo, con reloj fijo | `E-01` a `E-12`, `E-15`, `E-16`, `L-01` a `L-22`, `F1-R07`, `F1-R15` |
| `activities/tests/test_cancel_views.py` | vista, URL, sesión/CSRF/método, identidad de respuesta, templates, admin, seed/reset | `E-03` a `E-05`, `E-14`, `E-17`, `L-24` a `L-27`, `L-30`, `F1-R24` a `F1-R29` |
| `activities/tests/test_cancel_concurrency.py` | `TransactionTestCase`, hilos + barrera, reloj tras el bloqueo, `busy` | `E-13`, `L-23`, `L-28`, `L-29`, `F1-R06`, `F1-R16`, `F1-R17` |

**Convención de trazabilidad:** cada test nuevo se nombra con el identificador que verifica (`test_E09_repetition_keeps_original_date`, `test_L04_one_microsecond_past_deadline`, `test_R26_button_hidden_outside_window`), de modo que la cobertura sea legible en el propio código y `tasks.md` pueda enlazar tarea → test sin ambigüedad. `L-31` no es prueba sino decisión de display (§14).

Coberturas transversales que requieren prueba propia:

- **Coherencia de cupo (`E-15`)**: la que detecta `X-01` — actividad llena, cancelación, inscripción de otro estudiante → `registered` y `available == 0` de nuevo. Falla si solo se cambia `with_availability()`.
- **Respuesta idéntica (`F1-R03`)**: comparación campo a campo entre `E-03`, `E-04` y `E-05`.
- **Interfaz no ofrece lo que el servicio rechaza (`F1-R26`)**: con el reloj parchado en la misma posición que usa el servicio, el detalle/`mine` muestran el botón justo cuando `cancel()` concedería.
- **Admin (`E-16`, `L-21`, `L-22`)**: extiende `test_admin_rejects_capacity_and_read_only_registration` — reducir capacidad al número de confirmadas guarda; por debajo, `ValidationError` con el texto actual; `cancelled_at` ignorada en el POST de edición y presente en el listado.
- **Seed (`E-17`, `F1-R28`)**: las dos altas existen y confirmadas; segunda corrida tras una cancelación no duplica ni reescribe; `reset_demo` tras cancelaciones funciona y reconstruye confirmadas.
- **Migración**: `makemigrations --check --dry-run` limpio y la verificación de filas previas de §3.

### 9.2 Ejecución

```sh
uv sync --locked
uv run --locked python manage.py migrate
uv run --locked python manage.py test --noinput
uv run --locked python manage.py check
uv run --locked python manage.py makemigrations --check --dry-run
uv run --locked python manage.py seed_demo
uv run --locked python manage.py runserver 127.0.0.1:8000

# Equivalente sin Python/uv en el host:
docker compose up --build
docker compose exec web uv run --locked python manage.py test --noinput
```

Condiciones ya establecidas que se respetan: las pruebas corren sobre `data/test.sqlite3`, aislada de `data/db.sqlite3`; las pruebas concurrentes usan archivo real y conexiones independientes; no se lanzan dos suites sobre la misma carpeta a la vez (`README.md:24`).

**Criterio de terminado** (idéntico a `§6.6` de la spec):

- [ ] `python manage.py test --noinput` en verde, con los casos de `§4` y `§5` de la spec.
- [ ] `python manage.py check` sin avisos.
- [ ] `python manage.py makemigrations --check --dry-run` sin cambios pendientes.
- [ ] `P-01`, `P-03`, `P-04` respondidas (§14) — `P-01` es la única que cambia lo que ve el estudiante.
- [ ] Recorrido del README permite demostrar `E-06` y `E-08` sin preparar datos a mano.

### 9.3 Recuperación

| Situación | Recuperación |
| --- | --- |
| `busy` durante una cancelación | El usuario reintenta; la transacción revirtió completo, no hay efecto parcial (`F1-R17`). |
| Prueba concurrente colgada o base de pruebas sucia | Re-ejecutar la suite; si hiciera falta, borrar `data/test.sqlite3` (las pruebas solo eliminan la base de pruebas). |
| Migración `0002` aplicada y hay que volver atrás | Revertir `migrate activities 0001` **pierde las fechas de cancelación**; se recomienda avance + respaldo de `data/db.sqlite3`, no reversa. |
| Demo desordenada | `reset_demo --confirm` (borra cancelaciones de las cinco actividades por diseño, `F1-R28`) y `seed_demo`. |
| Código base a cero | Restauración del checkpoint `../material-docente/checkpoints/base.tar.gz` en una carpeta **nueva** (`README.md:76-90`). |
| Fallo en Docker | `docker compose stop/start` conserva datos; `down -v` no se usa en el día a día (`README.md:48`). |

---

## 10. Riesgos y alternativas consideradas

### 10.1 Riesgos

| # | Riesgo | Mitigación | IDs |
| --- | --- | --- | --- |
| R-1 | Cambiar solo `with_availability()` y no los otros dos puntos: la UI anuncia un cupo que `register()` niega | Los tres cambios en la misma etapa de trabajo; test `E-15` como guardián | `X-01`, `F1-R11` |
| R-2 | Duplicar la fórmula del plazo en vistas y servicio y que el botón prometa lo que el servicio rechaza | Helper único `cancellation_deadline`/`can_cancel` (corrección F-03) + test `F1-R26` | `F1-R26`, `M-02` |
| R-3 | Leer `timezone.now()` fuera del `atomic` y decidir con un reloj anterior a la espera | Lectura del reloj dentro del bloque, verificada con `assert_called_once` + `in_atomic_block` | `F1-R06` |
| R-4 | Olvidar la rama `not_reenrollable` y romper `enroll` con `KeyError` (spec incompleta) | Corrección F-01: cinco claves en `MESSAGES` | `F1-R20`, `F1-R21` |
| R-5 | Seed que duplica o revive filas al re-ejecutarse | Guarda de existencia en las dos altas nuevas; test de idempotencia con cancelación previa | `F-02`, `F1-R28` |
| R-6 | Reversa de `0002` pierde fechas de cancelación | Documentado; avance + respaldo; no hay caso de uso de reversa en la demo | `F1-R08` |
| R-7 | Precisión de display vs. precisión de microsegundos del borde | `P-01` resuelto hacia la opción (c): la interfaz muestra la regla, no un instante derivado | `L-31`, `F1-R05` |
| R-8 | Pruebas concurrentes falsas por SQLite en memoria o por hilo que reutiliza conexión | Patrón ya validado: `TransactionTestCase`, archivo real, `Barrier`, `close_old_connections` | `E-13` |
| R-9 | `README.md` desalineado con el `compose.yaml` vigente (volumen nombrado vs. bind mount) | Ver §8.2; corregir en la tarea de documentación | — |
| R-10 | Que el admin permita eludir las reglas | `readonly_fields` + sin alta ni baja; ninguna escritura de `cancelled_at` desde el panel | `F1-R27`, `README.md:74` |

### 10.2 Alternativas consideradas y descartadas

| Alternativa | Por qué se descarta |
| --- | --- |
| Campo `status` (`confirmada/cancelada`) o modelo `Cancellation` aparte | D1: dos fuentes de verdad que se pueden contradecir; estado terminal no justifica máquina de estados (`F1-R12`) |
| Borrar la fila al cancelar | `F1-R08`: exige conservar la fila, `created_at` y `cancelled_at`; además chocaría con el `UniqueConstraint` y habilitaría la reinscripción (`F1-R23`) |
| Snapshot de `starts_at` en la inscripción para el plazo | D4 descartada explícitamente; obligaría a migración de datos y a una columna más. Se asume `S-02` (reprogramar reabre/cierra el plazo) |
| Ruta de cancelación por inscripción (`/registrations/<pk>/cancel/`) | `P-03(b)`: exige validar propiedad antes de responder y multiplica superficie de fuga; se mantiene la ruta por actividad (`D6`, `P-03(a)`) |
| `select_for_update()` para la concurrencia | No protege en SQLite (`README.md:74`); el `IMMEDIATE` ya da la reserva de escritura antes de leer |
| Destino de redirección según el resultado (detalle vs. «mis inscripciones») | `X-04`/`F1-R24`: un destino por caso reintroduce la fuga de `F1-R03` |
| Cancelación desde el admin o con acción masiva | Excluida por `F1-R27` y `README.md:74`: el panel es de consulta |
| Reinscripción reactivando la fila | `D3`/`F1-R20`: fuera de F1; además habría que borrar `cancelled_at`, operación que F1 no define |
| Mostrar el instante límite con segundos en la interfaz (`M-03`) | Viable, pero cualquier display recorta microsegundos (`L-31`); se propone `P-01(c)` y dejar `M-03` como mejora opcional (§14) |
| Crear la cancelación con señales o desde la vista, sin servicio | La precedencia, el reloj dentro del `IMMEDIATE` y la escritura condicional viven en un único lugar verificable; la vista solo orquesta (`F1-R06`, `F1-R16`) |
| Índice sobre `cancelled_at` (`M-05`) y `CheckConstraint` (`M-06`) | Sin efecto demostrable con cinco actividades; anotados como mejoras futuras, fuera de F1 |

---

## 11. Archivos afectados

| Archivo | Cambio | IDs | Etapa |
| --- | --- | --- | --- |
| `activities/models.py` | `cancelled_at` nullable; propiedad `is_cancelled`; `Activity.clean()` cuenta confirmadas | `F1-R08`, `F1-R11`, `F1-R12`, `F1-R29` | 1 |
| `activities/migrations/0002_*.py` | Nueva, generada (`AddField`, aditiva) | `F1-R08` | 1 |
| `activities/services.py` | `WINDOW`, helpers, `cancel()`, `with_availability()` filtrado, ramas de `register()`, 5 claves en `MESSAGES` | `F1-R04` a `F1-R17`, `F1-R20` a `F1-R23`, `F1-R26` | 2 |
| `activities/views.py` | `cancel_registration`; contexto `can_cancel`/`cancellable_ids` en `detail` y `mine` | `F1-R01`, `F1-R02`, `F1-R24` a `F1-R26` | 3 |
| `activities/urls.py` | Ruta `activities/<int:pk>/cancel/`, nombre `cancel` | `F1-R24` | 3 |
| `templates/activities/detail.html` | Badge de estado, `cancelled_at`, botón condicionado al plazo, sin alta tras cancelar | `F1-R25`, `F1-R26` | 3 |
| `templates/activities/mine.html` | Ídem por inscripción | `F1-R25`, `F1-R26` | 3 |
| `activities/admin.py` | `cancelled_at` en `list_display` y `readonly_fields` | `F1-R27`, `M-08` | 4 |
| `activities/management/commands/seed_demo.py` | Dos altas directas con guarda de existencia | `D5`, `E-17`, `F-02` | 5 |
| `activities/tests/` | Tres módulos nuevos (§9.1); `test_base.py` se conserva | `§4`, `§5` de la spec | 1-5, junto a cada etapa |
| `README.md` | Recorrido con cancelación, tabla de resultados, casos nuevos del seed, alineación con `compose.yaml` | `§6.6` | 6 |

**No cambia:** `activities/forms.py`, `activities/management/commands/reset_demo.py`, `static/` (los mensajes heredan `.message`), `config/settings.py`, `config/urls.py`, `Dockerfile`, `uv.lock`, `compose.yaml`, `manage.py`, `entrypoint.sh`.

---

## 12. Orden de trabajo

Dependencias reales; cada etapa deja verificable lo anterior.

| # | Etapa | Resultado concreto | Depende de | Cierre comprobable |
| --- | --- | --- | --- | --- |
| 0 | Aprobación de hallazgos `F-01`, `F-02`, `F-03` y de `P-01`..`P-04` (§1, §14) | Spec alineada con el plan | — | Docente aprueba o ajusta; si algo cambia, se ajusta este plan |
| 1 | Modelos + migración + propiedad + `clean()` | `0002` generada; `makemigrations --check --dry-run` limpio | 0 | `manage.py check` + migración aplicada sobre copia de la base |
| 2 | Servicios (`WINDOW`, helpers, `cancel()`, cupo filtrado, `register()`, `MESSAGES`) | Toda la regla de dominio en `services.py` | 1 | `test_cancel_service.py` en verde + `test_base.py` intacto |
| 3 | Vistas + URL + templates | Superficie visible completa | 2 | `test_cancel_views.py` en verde; recorrido manual a mano |
| 4 | Admin | `cancelled_at` visible y de solo lectura; capacidad sobre confirmadas | 1 | Pruebas `E-16`/`L-21`/`L-22` en verde |
| 5 | Seed (+ verificación de `reset_demo`) | `E-17` demostrable en pantalla; cancelaciones conservadas entre corridas | 2 | Pruebas de idempotencia con cancelación previa en verde |
| 6 | Concurrencia | `E-13`, reloj tras el bloqueo, `busy` | 2 | `test_cancel_concurrency.py` en verde (3 corridas seguidas) |
| 7 | Suite completa + documentación | README actualizado; criterios de `§6.6` cumplidos | 1-6 | `test`, `check`, `makemigrations --check` en verde con uv **y** con Docker; recorrido del README demuestra `E-06` y `E-08` |

Las pruebas de cada etapa se escriben **junto con** el código de esa etapa, no al final; la etapa 6 solo acumula las que necesitan hilos.

---

## 13. Cobertura: requisito → decisión del plan → verificación

| Requisito | Decisión | Verificación |
| --- | --- | --- |
| `F1-R01` | DD-07 (identidad solo de `request.user`), DD-05 (filtro por titular) | `E-03`, `E-04`, `L-13`, `L-16` · `test_cancel_service` / `test_cancel_views` |
| `F1-R02` | DD-07 (`login_required` + `require_POST` + CSRF) | `E-14`, `L-24`, `L-25`, `L-26` |
| `F1-R03` | DD-05 (una sola rama genérica), DD-07 (sin `get_object_or_404`) | `E-03` vs `E-04` vs `E-05` con comparación de clave/texto/status/destino; `L-15` |
| `F1-R04` | DD-03 (`WINDOW`, `cancellation_deadline`) | `L-01`, `L-02` |
| `F1-R05` | DD-03 (comparación `<=`, sin redondeo) | `L-03`, `L-04`, `L-05`, `L-06`, `L-07` |
| `F1-R06` | DD-05 (reloj dentro del `atomic`) | §7: test con reloj parchado + `assert_called_once` + `in_atomic_block` |
| `F1-R07` | DD-03 (límite desde `starts_at` vigente) | Test de reprogramación (`E-10`), `S-02` |
| `F1-R08` | DD-01 (misma fila) | `E-01`, `E-02`; migración aditiva §3 |
| `F1-R09` | DD-05 (`.update()` condicional, sin reescritura) | `E-09`, `E-10`, `L-19` |
| `F1-R10` | DD-05 (un `UPDATE` por transición) + restricción única | `E-02`, `L-17`, `L-19`, `E-13` |
| `F1-R11` | DD-04 (tres puntos en el mismo commit) | `E-15`, `L-18`, `L-20`, `L-21`, `L-22` |
| `F1-R12` | DD-01 (un solo campo) | Revisión de modelo; `F1-R29` |
| `F1-R13` | DD-05 (rama de repetición + update condicional) | `E-09`, `L-19` |
| `F1-R14` | DD-05 (orden: repetición antes que plazo) | `E-10`, `L-10`, `L-11`, `L-12` |
| `F1-R15` | DD-05 (reloj no leído en la rama) | Test con `timezone.now` que falla si se invoca |
| `F1-R16` | DD-05 (IMMEDIATE + escritura condicional) | `E-13`, `L-23` + prueba aislada de la defensa estructural |
| `F1-R17` | DD-05 (`except OperationalError` selectivo) | `L-28`, `L-29` |
| `F1-R18` | DD-05 (sin guarda `is_active`) | `E-06` |
| `F1-R19` | DD-05 (lectura de `is_active` omitida) | `E-06`, `L-11` + revisión de código |
| `F1-R20` | DD-06 (rama `not_reenrollable`) | `E-11` |
| `F1-R21` | DD-06 + corrección F-01 (texto en `MESSAGES`) | `E-11` (mensaje distinto de `already_registered`) |
| `F1-R22` | DD-06 (posición de precedencia) | `E-12` |
| `F1-R23` | DD-06 + `UniqueConstraint` existente | `E-11` (conteo de filas sin cambios) |
| `F1-R24` | DD-07 (destino único `mine`) | `E-01`, `E-03`..`E-05`, test de `302` en todos los resultados |
| `F1-R25` | DD-09 (badges y fecha en `detail`/`mine`) | Pruebas de plantilla: `assertNotContains` «confirmada» sobre fila cancelada |
| `F1-R26` | DD-03 (helper compartido, corrección F-03) | Test que parcha el reloj en la posición del servicio y compara botón vs. concesión |
| `F1-R27` | DD-10 (admin) | `E-16`, `L-21`, `L-22`, lectura de `cancelled_at` en listado |
| `F1-R28` | DD-11 (`reset_demo` sin cambios) | Prueba de `reset_demo` tras cancelaciones |
| `F1-R29` | DD-02 (propiedad única) | Prueba de `is_cancelled`; revisión de que nadie repite `cancelled_at is None` |
| `D1`-`D6` | DD-01, DD-04, DD-06, DD-03, DD-11, DD-08/09 | Según cada decisión, arriba |

---

## 14. Decisiones abiertas: propuesta del plan para el cierre

| # | Pregunta | Propuesta del plan | Motivo |
| --- | --- | --- | --- |
| `P-01` | Cómo comunicar el instante límite (`L-31`) | **(c)**: la interfaz muestra la regla («hasta 24 h antes del inicio») y no un instante derivado; el rechazo explica la regla, no una fecha calculada | `F1-R05` no admite tolerancia y todo display recorta microsegundos; así no hay display engañoso. `(a)` (límite con segundos) queda como mejora `M-03` si el docente prefiere visibilidad |
| `P-02` | Avisar a titulares al reprogramar | **(a)** no notificar | `S-07`; F1 no tiene notificaciones |
| `P-03` | Ruta por actividad o por inscripción | **(a)** por actividad (`D6`) | Menor superficie de fuga, consistente con `register` |
| `P-04` | Altas directas en el seed | **(a)** sí, **con la corrección F-02**: son dos y ambas con guarda de existencia | Mantiene el recorrido manual completo de `E-17` sin sacrificar idempotencia |

---

**Entrega:** este documento. No se modificó código de aplicación ni `docs/f1/spec.md`; ambos quedan para su revisión junto con `PROMP-TASKS.md`, que producirá `docs/f1/tasks.md` a partir de esta spec y este plan.

### Registro de aprobación T01 (etapa 0)

Fecha: 2026-10-08. Responsable: docente (registra implementador A).

| Ítem | Estado |
| --- | --- |
| F-01 (cinco claves en `MESSAGES`) | aceptado |
| F-02 (dos altas directas con guarda) | aceptado |
| F-03 (M-02 promovido al alcance) | aceptado |
| P-01 opción (c) | aceptado |
| P-02 opción (a) | aceptado |
| P-03 opción (a) | aceptado |
| P-04 opción (a) con corrección F-02 | aceptado |

# F1 · Cancelación de inscripciones

Especificación de la funcionalidad de cancelación. Estado: **resuelto — verificado contra tasks T01…T10**. No hay código de aplicación modificado al momento de este documento.

Versión del código base sobre la que se especificó: commit `72a68f4` («feat: demo base»), 22 pruebas.

---

## 1. Contexto, objetivo y alcance

### 1.1 Contexto

La demo de inscripciones permite darse de alta (`register`, `activities/services.py:19`) y consultar las propias (`activities/views.py:31`). **No existe ninguna forma de baja**: `Registration` (`activities/models.py:22`) solo tiene `created_at`, y `RegistrationAdmin.has_delete_permission` devuelve `False` (`activities/admin.py:19`) para que el docente tampoco pueda eliminar filas por el panel.

Hoy la disponibilidad se calcula contando filas: `with_availability()` (`activities/services.py:16`) anota `Count("registrations")`, y ese número manda sobre `available`, sobre el rechazo por cupo lleno en `register` (`activities/services.py:33`) y sobre el piso de capacidad de `Activity.clean()` (`activities/models.py:19`). Cualquier estado nuevo que signifique «esta inscripción no ocupa cupo» tiene que atravesar **los tres** puntos a la vez.

El modelo transaccional ya está resuelto: SQLite con `transaction_mode: "IMMEDIATE"` y `timeout: 10` (`config/settings.py:14`). `register` adquiere la reserva de escritura antes de leer el cupo y devuelve `busy` ante contención conocida (`activities/services.py:37-41`). F1 se apoya en esa base y no la redefine.

### 1.2 Objetivo

Permitir que el titular de una inscribedcancelar su inscripción liberando exactamente un cupo, conservando el registro y su fecha de cancelación, con un plazo de 24 h y sin revelar la existencia de inscripciones ajenas.

### 1.3 Alcance

**Incluido (F1)**

| Área | Ubicación |
| --- | --- |
| Campo `cancelled_at` y migración | `activities/models.py`, `activities/migrations/0002_*` |
| Servicio `cancel()` + códigos de resultado y mensajes | `activities/services.py` |
| Recuento de solo confirmadas en disponibilidad, cupo lleno y piso de capacidad | `activities/services.py`, `activities/models.py` |
| Rama de reinscripción rechazada en `register()` | `activities/services.py:26` |
| Vista `cancel_registration` + URL `cancel` | `activities/views.py`, `activities/urls.py` |
| Botón, badge y fecha en detalle y en «Mis inscripciones» | `templates/activities/detail.html`, `mine.html` |
| `cancelled_at` de solo lectura en el admin | `activities/admin.py` |
| Inscripciones de la demo para poder demostrar las reglas | `activities/management/commands/seed_demo.py` |
| Pruebas de servicio, vista, límites y concurrencia | `activities/tests/` |
| Documentación del recorrido y del comportamiento | `README.md` |

**Excluido de F1 (ver §1.4)**

### 1.4 Terminado, no es F1

- **Reinscripción**: F1 la rechaza de forma explícita, no la implementa.
- **Notificaciones** al cancelar (correo, aviso al docente, acta).
- **Motivo de la cancelación** y cualquier registro de auditoría adicional. El actor ya es conocido: es el titular, por definición.
- **Reembolso, penalización o crédito**: la demo no modela pagos.
- **Baja desde el panel del docente**: se mantiene la decisión vigente de que la administración de inscripciones es de consulta (`README.md:74`).
- **Historial de cambios**: una inscripción cancelada no tiene reinscripción, así que su estado terminal.

### 1.5 Decisiones tomadas en la revisión previa

Estas seis quedaron resueltas con el docente antes de redactar y condicionan todo lo que sigue.

| # | Decisión |
| --- | --- |
| D1 | Estado de cancelación con un campo `cancelled_at` nullable en `Registration`. Sin `status`, sin modelo aparte. |
| D2 | Alcance completo: servicio + vista + plantillas + admin + seed + pruebas. |
| D3 | Reinscripción rechazada con un código de resultado propio, `not_reenrollable`. |
| D4 | El plazo se ancla al `starts_at` **actual** de la actividad, con la consecuencia asumida y documentada en §6.1. |
| D5 | Se amplía el seed con dos inscripciones que hoy no existen, para que el recorrido manual pueda demostrar las reglas de actividad deshabilitada y de plazo vencido. |
| D6 | El botón de cancelación aparece en el detalle y en «Mis inscripciones». La URL es por actividad. |

---

## 2. Vocabulario

Términos estables. El nombre del término es la clave de `MESSAGES` (`activities/services.py:6`) cuando existe, para que especificación y código no se separen.

| Término | Significado |
| --- | --- |
| **Inscripción** | Fila de `Registration`, que une un `student` con un `activity`. Existe siempre que haya habido alta. |
| **Confirmada** | Inscripción con `cancelled_at IS NULL`. Es la que ocupa cupo. |
| **Cancelada** | Inscripción con `cancelled_at` no nulo. Conserva la fila, ya no ocupa cupo. Estado terminal en F1. |
| **Titular** | `Registration.student` de la fila. Único actor con permiso para cancelar. |
| **Solicitante** | Usuario autenticado que envía el POST. Se contrasta con el titular. |
| **Transición** | El paso de *confirmada* a *cancelada`. Ocurre **exactamente una vez** por inscripción. |
| **Cancelación efectiva** | La primera transición de una inscripción. |
| **Repetición** | Una segunda cancelación de una inscripción ya cancelada. No es una transición. |
| **Ventana de cancelación** | `WINDOW = timedelta(hours=24)`, constante de `activities/services.py`. |
| **Instante límite** | `starts_at - WINDOW`. Instante, no fecha. |
| **Dentro de plazo** | `now <= instante límite`. El borde es inclusivo. |
| **Fuera de plazo** | `now > instante límite`. |
| **Carga** | `Count` de inscripciones **confirmadas**, no de filas. |
| **Cupo liberado** | Aumento de `available` en exactamente 1 por transición. |
| **Aviso genérico** | Respuesta única que recibe tanto una inscripción ajena como una inexistente. Sin datos de terceros. |
| **`cancelled`** | Código: la solicitud resultó en una cancelación efectiva. |
| **`already_cancelled`** | Código: la inscripción ya estaba cancelada. No hubo transición. |
| **`window_closed`** | Código: inscripción confirmada fuera de plazo. No hubo transición. |
| **`not_cancellable`** | Código: aviso genérico. No hubo transición. |
| **`busy`** | Código: contención conocida de SQLite. No hubo transición ni efecto parcial. |
| **`not_reenrollable`** | Código: intento de reinscripción sobre una inscripción cancelada. Reusa en `register`. |

---

## 3. Requisitos

### 3.1 Autorización

| ID | Requisito |
| --- | --- |
| **F1-R01** | Solo el titular de la inscripción puede cancelarla. La identidad se toma de `request.user`, nunca de un campo del formulario ni de un parámetro de la URL. |
| **F1-R02** | La cancelación se dispara por `POST` exclusivamente. `GET` devuelve `405`. Exige sesión autenticada y CSRF válido, igual que `enroll` (`activities/views.py:21-28`). |
| **F1-R03** | Una inscripción ajena al solicitante y una inscripción inexistente producen **la misma** respuesta: mismo código, mismo texto, mismo código HTTP y mismo destino de redirección. La respuesta no debe permitir distinguir ambos casos, ni por mensaje, ni por status, ni por tiempo de respuesta observable de forma relevante, ni por contenido de la página de destino. |

### 3.2 Plazo

| ID | Requisito |
| --- | --- |
| **F1-R04** | Se permite cancelar mientras `now <= starts_at - WINDOW`. `WINDOW` vale 24 h exactas. |
| **F1-R05** | El borde es **inclusivo**: en `now == starts_at - WINDOW` la cancelación se concede. **No hay redondeo**: no se trunca a minutos ni a horas, no hay tolerancia ni margen. Un microsegundo por encima del instante límite ya está fuera de plazo. |
| **F1-R06** | El instante de decisión se lee **dentro** de la transacción `IMMEDIATE`, después de adquirir la reserva de escritura, igual que hace `register` (`activities/services.py:30`). Una solicitud que espera a un escritor y llega a una actividad cuyo plazo se cerró devuelve `window_closed`, no `cancelled`. El parámetro `now` conserva el reloj fijo de pruebas. |
| **F1-R07** | El plazo se ancla al `starts_at` vigente, no a un snapshot. Ver supuesto **S-02** en §6.1. |

### 3.3 Estado y cupo

| ID | Requisito |
| --- | --- |
| **F1-R08** | La cancelación **no borra** la inscripción. La misma fila pasa a cancelada y conserva `created_at`. |
| **F1-R09** | La cancelación efectiva registra `cancelled_at`. Una repetición **conserva la fecha original**: `cancelled_at` no se reescribe. |
| **F1-R10** | Cada transición libera **exactamente un** cupo: `available` aumenta en 1, nunca en más ni en menos. Como una inscripción por `(student, activity)` está garantizada por `one_registration_per_student_activity` (`activities/models.py:27`), no hay multiplicidad que ajustar. |
| **F1-R11** | La carga, y por lo tanto `available`, cuenta **solo inscripciones confirmadas**. Las canceladas quedan fuera. Este requisito obliga a cambiar los tres puntos de una vez: `with_availability()` (`activities/services.py:16-17`), el rechazo por cupo lleno en `register()` (`activities/services.py:33`) y el piso de capacidad de `Activity.clean()` (`activities/models.py:19`). |
| **F1-R12** | El dato persistido es un único `cancelled_at` nullable. No hay estado derivado ni campo redundante que pueda contradecirlo. |

### 3.4 Idempotencia y concurrencia

| ID | Requisito |
| --- | --- |
| **F1-R13** | Cancelar una inscripción ya cancelada devuelve `already_cancelled`, no `cancelled`, y no vuelve a escribir `cancelled_at`. |
| **F1-R14** | La repetición se reconoce **antes** de evaluar el plazo. Una inscripción cancelada devuelve `already_cancelled` **incluso fuera de plazo** y aunque la actividad ya haya comenzado. Esto replica la precedencia ya existente en `register`, donde el duplicado gana sobre `disabled`, `started` y `full` (`activities/tests/test_base.py:33-37`). |
| **F1-R15** | El reconocimiento de repetición no consulta el reloj: la ruta `already_cancelled` no lee `timezone.now()`. |
| **F1-R16** | Dos cancelaciones simultáneas de la misma inscripción producen **una sola** transición como máximo. El resultado conjunto es un subconjunto de `{cancelled, already_cancelled, busy}` y nunca contiene dos `cancelled`. La garantía se sostiene con el `IMMEDIATE` de SQLite **y** con una escritura condicional `WHERE cancelled_at IS NULL`; la segunda es la defensa estructural si alguna vez la primera dejara de aplicar. |
| **F1-R17** | Un timeout de contención devuelve `busy`, sin efecto parcial y con reintento permitido. Solo la contención conocida se vuelve recuperable; otros `OperationalError` se propagan, igual que en `register` (`activities/services.py:37-41`). |

### 3.5 Actividad deshabilitada

| ID | Requisito |
| --- | --- |
| **F1-R18** | `is_active` **no** es una condición de la cancelación. Una actividad deshabilitada admite cancelación mientras se cumpla el plazo. |
| **F1-R19** | La lectura de `is_active` es deliberadamente omitida en este flujo: no debe aparecer como guarda. La asimetría es intencional: deshabilitar frena altas (`activities/services.py:28-29`) y no bajas. |

### 3.6 Reinscripción

| ID | Requisito |
| --- | --- |
| **F1-R20** | La reinscripción está fuera de F1. `register()` sobre una inscripción cancelada devuelve `not_reenrollable` y no crea ni reactiva nada. |
| **F1-R21** | El mensaje debe ser comprensible por el estudiante y no puede ser `already_registered`. Para una fila cancelada, «Ya estás inscripto en esta actividad» es falso. |
| **F1-R22** | La rama de reinscripción se evalúa en la misma posición de precedencia que el duplicado confirmado: antes de `disabled`, `started` y `full`. Un estudiante con inscripción cancelada en una actividad llena o ya iniciada recibe el motivo de la reinscripción, no `full` ni `started`. |
| **F1-R23** | La restricción es doble: el `UniqueConstraint` (`activities/models.py:27`) impide una fila nueva y F1 no ofrece ninguna operación que borre `cancelled_at`. |

### 3.7 Superficie visible y coherencia transversal

| ID | Requisito |
| --- | --- |
| **F1-R24** | La vista devuelve `302` a `/my-registrations/` en **todos** los resultados, incluido el aviso genérico. Un destino dependiente del caso reintroduciría la fuga que **F1-R03** prohíbe. |
| **F1-R25** | «Mis inscripciones» y el detalle distinguen confirmada de cancelada, y muestran `cancelled_at` en la cancelada. El detalle no puede afirmar «Tu inscripción está confirmada» sobre una fila cancelada. |
| **F1-R26** | El botón de cancelación solo se ofrece dentro de plazo. La misma regla que el servicio usa para conceder debe decidir qué se muestra, para que la interfaz no ofrezca lo que el servicio va a rechazar. |
| **F1-R27** | En el admin, `cancelled_at` es de solo lectura y aparece en la lista. No hay alta, baja ni edición que eviten las reglas, en línea con `README.md:74`. |
| **F1-R28** | `reset_demo` no necesita cambios: `Activity` se elimina en cascada y con ella sus inscripciones, incluidas las canceladas. |
| **F1-R29** | El estado de la inscripción se expone con una propiedad derivada única en el modelo, para que plantillas, vistas y pruebas no repitan `cancelled_at is None`. |

---

## 4. Escenarios de aceptación

### Escenarios principales

**E-01 · Cancelación efectiva dentro de plazo**
Dado una inscripción confirmada de Ana a una actividad que comienza dentro de 48 h
Cuando Ana envía el POST de cancelación
Entonces el resultado es `cancelled`
Y la misma fila queda con `cancelled_at` no nulo y su `created_at` original intacto
Y la disponibilidad de la actividad disminuye en 1 respecto de antes de cancelar
Y la respuesta es `302` a `/my-registrations/`

**E-02 · El titular libera exactamente un cupo**
Dado una actividad con capacidad 2 y 2 inscripciones confirmadas, `available == 0`
Cuando el titular de una de ellas cancela
Entonces `available == 1`
Y el número de inscripciones de la actividad no cambia
Y el número de inscripciones confirmadas disminuye en 1

**E-03 · Solo el titular**
Dado una inscripción confirmada de Bruno
Cuando Ana envía el POST de cancelación sobre esa actividad
Entonces el resultado es `not_cancellable`
Y la inscripción sigue confirmada, con `cancelled_at` nulo
Y `available` no cambia

**E-04 · Inscripción inexistente**
Dado que Ana nunca se inscribió a una actividad
Cuando Ana envía el POST de cancelación sobre esa actividad
Entonces el resultado es `not_cancellable`
Y la respuesta es idéntica, en código, texto, status y destino, a la de **E-03**

**E-05 · Actividad inexistente**
Dado un identificador de actividad que no existe
Cuando un usuario autenticado envía el POST de cancelación
Entonces el resultado es `not_cancellable`
Y la respuesta es idéntica a la de **E-04**: ni mensaje distinto, ni `404`, ni redirección a otra página

**E-06 · Actividad deshabilitada**
Dado una inscripción confirmada a una actividad con `is_active == False` que comienza dentro de 48 h
Cuando el titular cancela
Entonces el resultado es `cancelled`
Y la disponibilidad disminuye en 1

**E-07 · Inspección fuera de plazo**
Dado una inscripción confirmada a una actividad cuyo instante límite ya pasó
Cuando el titular cancela
Entonces el resultado es `window_closed`
Y la inscripción sigue confirmada, con `cancelled_at` nulo
Y la disponibilidad no cambia

**E-08 · Actividad ya comenzada**
Dado una inscripción confirmada a una actividad que comenzó hace 2 h
Cuando el titular cancela
Entonces el resultado es `window_closed`
Porque el instante límite es 24 h **antes** del inicio y quedó atrás

**E-09 · Repetición dentro de plazo**
Dado una inscripción ya cancelada dentro de plazo
Cuando el titular repite el POST
Entonces el resultado es `already_cancelled`
Y `cancelled_at` conserva el valor de la cancelación original
Y la disponibilidad no vuelve a cambiar

**E-10 · Repetición fuera de plazo**
Dado una inscripción cancelada dentro de plazo
Y luego la actividad se reprograma o el reloj avanza más allá del instante límite
Cuando el titular repite el POST
Entonces el resultado es `already_cancelled`, **no** `window_closed`
Y `cancelled_at` conserva el valor original
Y la disponibilidad no cambia
Este escenario es la razón de **F1-R14**: una vez cancelada, la inscripción ya no depende del plazo

**E-11 · Reinscripción rechazada**
Dado una inscripción cancelada dentro de plazo, de una actividad habilitada, con cupos libres y sin iniciar
Cuando el titular intenta inscribirse
Entonces el resultado es `not_reenrollable`
Y no se crea ninguna fila y `cancelled_at` sigue con su valor
Y el mensaje explica que la reinscripción no está habilitada

**E-12 · Reinscripción rechazada aunque la actividad no admita altas**
Dado una inscripción cancelada, de una actividad deshabilitada o ya iniciada o sin cupos
Cuando el titular intenta inscribirse
Entonces el resultado es `not_reenrollable`
Y no `disabled`, ni `started`, ni `full`, ni `already_registered`

**E-13 · Cancelación simultánea de la misma inscripción**
Dado una inscripción confirmada dentro de plazo
Cuando dos hilos envían el POST de cancelación al mismo tiempo
Entonces el conjunto de resultados es `{cancelled, already_cancelled}` o incluye `busy`
Y hay exactamente una fila cancelada
Y `cancelled_at` tiene un único valor
Y `available` disminuye en 1, no en 2

**E-14 · Método y sesión**
Dado un usuario autenticado
Cuando envía un `GET` a la URL de cancelación
Entonces la respuesta es `405`
Dado un cliente con `enforce_csrf_checks` sin token
Cuando envía el `POST`
Entonces la respuesta es `403`
Dado un usuario anónimo
Cuando envía el `POST`
Entonces responde con la redirección al inicio de sesión de `config/settings.py:23`

### Escenarios de coherencia transversal

**E-15 · El cupo liberado es realmente inscribible**
Dado una actividad completa con `available == 0`
Y una inscripción cancelada dentro de plazo por su titular
Cuando otro estudiante se inscribe
Entonces el resultado es `registered`
Y `available == 0` de nuevo
Este escenario falla si `with_availability()` se cambia y `register()` no. Es el test que protege la coherencia que exige **F1-R11**.

**E-16 · El docente puede reprogramar capacidad**
Dado una actividad con 3 inscripciones confirmadas y 1 cancelada
Cuando el docente reduce la capacidad a 3 desde el admin
Entonces el formulario se guarda
Porque el piso de capacidad se mide sobre inscripciones confirmadas, no sobre filas

**E-17 · La demo cubre las reglas que antes no eran demostrables**
Dado el seed de la demo
Entonces existe una inscripción de Bruno en la actividad deshabilitada, cancelable, con **E-06** aplicable a mano
Y existe una inscripción de Ana en la actividad ya iniciada, con **E-08** aplicable a mano

---

## 5. Casos límite y resultados esperados

### 5.1 Límites temporales

Con `starts_at = S` e instante límite `L = S − 24 h`:

| # | Instante de la solicitud | Resultado esperado | Nota |
| --- | --- | --- | --- |
| L-01 | `now = L − 1 h` | `cancelled` | Holgura amplia |
| L-02 | `now = L − 1 s` | `cancelled` | Todavía dentro |
| L-03 | `now = L` | `cancelled` | **Borde inclusivo**. Contrasta con `test_exact_start_rejected`, donde el borde de `register` es exclusivo |
| L-04 | `now = L + 1 µs` | `window_closed` | El primer instante fuera de plazo |
| L-05 | `now = L + 1 s` | `window_closed` | Sin redondeo a minutos ni a horas |
| L-06 | `now = L + 59 min` | `window_closed` | Ni siquiera `L + 59 min` redondeado a `L + 1 h` cuenta |
| L-07 | `now = S` | `window_closed` | Nunca alcanzable dentro de plazo; se documenta por completitud |
| L-08 | `now` con `starts_at` en el pasado | `window_closed` | La actividad del seed «iniciada» a −2 h |

**Simetría a observar:** `register` rechaza con `started` cuando `starts_at <= now`, borde **exclusivo para el alta**. `cancel` concede cuando `now <= L`, borde **inclusivo para la baja**. No es una inconsistencia: el alta se cierra en el instante en que empieza la actividad y la baja se cierra 24 h antes. Los dos bordes deben quedar escritos en los tests para que nadie los unifique por error.

### 5.2 Límites de estado

| # | Situación inicial | Resultado esperado | Efecto |
| --- | --- | --- | --- |
| L-09 | Inscripción ya cancelada, dentro de plazo | `already_cancelled` | Fecha y cupo intactos |
| L-10 | Inscripción ya cancelada, fuera de plazo | `already_cancelled` | Fecha y cupo intactos |
| L-11 | Inscripción ya cancelada, actividad deshabilitada | `already_cancelled` | `is_active` ni se consulta |
| L-12 | Inscripción ya cancelada, actividad ya iniciada | `already_cancelled` | El plazo no se reevalúa |
| L-13 | Inscripción ajena, actividad ya deshabilitada | `not_cancellable` | Sin fuga |
| L-14 | Inscripción ajena, actividad ya iniciada | `not_cancellable` | Sin fuga: no se revela «ya começou» |
| L-15 | Actividad inexistente, usuario autenticado | `not_cancellable` | Sin `404` |
| L-16 | Titular con inscripción cancelada en A e inscripción confirmada en B; cancela A dos veces | `already_cancelled` | B no se toca |

### 5.3 Límites de cupo y capacidad

| # | Situación | Resultado esperado | Nota |
| --- | --- | --- | --- |
| L-17 | Capacidad 1, 1 confirmada, se cancela | `available: 0 → 1` | Exactamente uno |
| L-18 | Tras L-17, otro estudiante se inscribe | `registered`, `available → 0` | **E-15** |
| L-19 | Tras L-17, se repite la cancelación | `already_cancelled`, `available` sigue en 1 | Exactamente uno, no dos |
| L-20 | Actividad con capacidad 10 y 2 canceladas de 8 | `available == 10` | La carga cuenta 8 |
| L-21 | Docente reduce capacidad al número de confirmadas | Se guarda | El piso ignora las canceladas |
| L-22 | Docente reduce capacidad por debajo de las confirmadas | `ValidationError` «No puede reducir…» | Texto actual vale, cambia el origen del conteo |
| L-23 | Dos cancelaciones simultáneas con capacidad 1 ocupada | Una sola transición, `available → 1` | **E-13** |

### 5.4 Límites de transporte y de la interfaz

| # | Situación | Resultado esperado |
| --- | --- | --- |
| L-24 | `GET` a la URL de cancelación | `405`, sin efecto |
| L-25 | `POST` sin token CSRF | `403`, sin efecto |
| L-26 | `POST` anónimo | Redirección al login, sin efecto |
| L-27 | Doble clic del botón en el navegador | `cancelled` y luego `already_cancelled`; una sola fecha |
| L-28 | Contención de SQLite (`database is locked`) | `busy`, sin efecto parcial, reintentable |
| L-29 | `OperationalError` de otro tipo | Se propaga; no se enmascara |
| L-30 | Integridad referencial: la actividad se elimina entre el render y el POST | `not_cancellable` |

### 5.5 Un límite que el código actual no expresa

**L-31 · Precisión visible contra precisión real.** `detail.html` y `mine.html` formatean con `date:'d/m/Y H:i'`, es decir **minutos**, y `America/Argentina/Ushuaia` es `UTC−03:00` fijo. El instante límite se calcula con precisión de microsegundos (**F1-R05**). Un estudiante que ve «01/10 10:00» no puede saber sicanceló con 30 s de margen o sin margen, y **F1-R05** no admite tolerancia para resolverlo. Opciones: formatear el límite con segundos, o no mostrarlo y Limitarse a la regla. Queda como decisión docente, registrada en §6.4 (P-01).

---

## 6. Supuestos, contradicciones y preguntas pendientes

### 6.1 Supuestos

| # | Supuesto | Consecuencia si resulta falso |
| --- | --- | --- |
| **S-01** | `America/Argentina/Ushuaia` es `UTC−03:00` todo el año; Argentina abolió el horario de verano en 2009. | Si hubiera un salto DST dentro de la ventana, «24 h antes» dejaría de ser tiempo transcurrido exacto. Con la configuración actual no hay discontinuidad. |
| **S-02** | Anclar el plazo al `starts_at` vigente es aceptable, **con la consecuencia asumida**: `starts_at` es editable por el docente en `/admin/` sin dejar rastro. Mover el inicio más adelante **reabre** el plazo de una actividad que ya había pasado su límite; moverlo antes lo cierra de golpe, negando a estudiantes que hasta un minuto antes podían cancelar. | Si el plazo debe ser inalterable, hace falta guardar un snapshot del inicio al crear la inscripción (**D4** fue la alternativa explícitamente descartada) o bloquear la edición, lo que rompe `reset_demo`. |
| **S-03** | La fecha de cancelación es el dato de auditoría suficiente. No hace falta `cancelled_by`, porque **F1-R01** garantiza que el actor es el titular. | Si en el futuro se admiten cancelaciones de oficio, falta el actor. |
| **S-04** | SQLite almacena los `DateTimeField` con zona normalizados a UTC y con microsegundos, así que la comparación de `cancelled_at` y `starts_at` es exacta y su orden lexicográfico coincide con el cronológico. | Si se guardaran offsets distintos, la comparación textual de SQLite podría orderar mal. El backend de Django evita esto. |
| **S-05** | La restricción única `(student, activity)` garantiza que «exactamente un cupo» no necesita corrección por multiplicidad. | Si se relajara la restricción, `F1-R10` necesita una regla adicional. |
| **S-06** | El aviso genérico no necesita secrecy criptográfica. La sesión ya identifica al solicitante y los identificadores de actividad son públicos en el catálogo. | Si algún día los identificadores fueran secretos, el patrón de respuesta genérica se vuelve imprescindible y debería documentarse como tal. |
| **S-07** | No hay que notificar a nadie. La demo es de uso docente local con datos ficticios. | Si hay inscripciones reales, cancelar sin avisar al docente es un problema operativo. |
| **S-08** | `SELECT` en el servicio ya filtra por titular, así que la ruta de repetición nunca alcanza código ajeno. | Si alguien reintrodujera un filtro solo por actividad, **F1-R03** se rompe. |
| **S-09** | `is_active` es una guarda de alta, no un estado de la actividad. Cancelar una actividad deshabilitada es una baja legítima, no una excepción. | Si `is_active` significara «la actividad se dio de baja y no admite ningún movimiento», entonces **F1-R18** sería incorrecto. El nombre del campo y su uso actual en `register` apuntan a lo contrario. |

### 6.2 Contradicciones y tensiones detectadas

No hay contradicción lógica entre las nueve reglas originales. Sí hay cinco tensiones reales, tres con el código existente y dos internas:

| # | Tensión | Resolución propuesta |
| --- | --- | --- |
| **X-01** | «Cancelar libera exactamente un cupo» vs. el modelo actual, que cuenta filas en **tres** lugares: `with_availability()` (`activities/services.py:16`), el cupo lleno de `register` (`:33`) y `Activity.clean()` (`activities/models.py:19`). | Es el hallazgo de mayor riesgo. Si se cambia solo `with_availability()`, la interfaz anuncia un cupo libre que `register()` niega: el estudiante ve «Disponibilidad: 1 cupos», pulsa «Inscribirme» y recibe «La actividad no tiene cupos disponibles». **Los tres puntos cambian en el mismo commit.** **E-15** es el test que lo detecta. |
| **X-02** | «Se conserva la misma inscripción» vs. `register()` devuelve hoy `already_registered` para cualquier fila existente, cancelada incluida. | Sin tocar `register()`, la regla «se rechaza de forma comprensible» se incumple: el mensaje afirma algo falso. De ahí **D3** y `F1-R20` a `F1-R23`. |
| **X-03** | «Repetir la cancelación… incluso fuera del plazo» vs. «se permite cancelar hasta 24 h antes». Una implementación natural evalúa el plazo primero y devuelve `window_closed` en la repetición. | **F1-R14** fija la precedencia: repetición antes que plazo. La asimetría resultante es intencional y está documentada en **E-10** y **L-09** a **L-12**. |
| **X-04** | «Una inscripción ajena o inexistente recibe la misma respuesta genérica» vs. la convención existente de redirigir según el contexto. Si el aviso genérico redirigiera al detalle de la actividad, una actividad inexistente produciría `404` y ambas ramas quedarían distinguibles. | **F1-R24**: un único destino, `/my-registrations/`, para los cinco resultados. También descarta medir el tiempo de respuesta. |
| **X-05** | «Solo cancela el titular» vs. la visibilidad de la actividad. El catálogo es público para autenticados y `detail.html` expone título, cupo y disponibilidad, aunque no quién está inscrito. | No hay fuga: «esta actividad tiene 2 de 4 cupos» no revela identidades ni permite probar la existencia de una inscripción propia. **F1-R03** se limita a la respuesta de la cancelación, no al modelo de datos. |

### 6.3 Mejoras propuestas (fuera del alcance mínimo de F1)

| # | Mejora | Motivo |
| --- | --- | --- |
| **M-01** | Fijar la ventana como constante con nombre (`CANCELLATION_WINDOW`) documentada, en lugar del `24` literal regado por el código. | El plazo aparece en el servicio, en la interfaz y en los mensajes del usuario. Que viva en un solo lugar evita que tres lecturas se contradigan. |
| **M-02** | Un único método que calcule el instante límite y la elegibilidad, reutilizado por el servicio y por las vistas. | **F1-R26**. Sin esto, la interfaz y el servicio pueden divergir y ofrecer un botón que el servicio va a rechazar. |
| **M-03** | Mensajes con el plazo en el texto del rechazo: «No podés cancelar: el plazo venció el 24/09 a las 10:00». | **L-31**. Es la mejora más barata frente al problema de precisión visible. |
| **M-04** | `Registration.__str__` con el estado: `ana — Clínica de Django (cancelada)`. | Hoy devuelve texto idéntico para confirmada y cancelada; el log del admin y los `str()` de error son indistinguibles. |
| **M-05** | Índice sobre `cancelled_at` si el conjunto de datos crece. | No hace falta con las cinco actividades de la demo; se anota para que no se reinvente el problema más adelante. |
| **M-06** | `CheckConstraint` en base: `cancelled_at IS NULL OR cancelled_at >= created_at`. | Defiende contra datos imposibles si alguien escribe a mano. Opcional; el reloj es el mismo para ambas escrituras. |
| **M-07** | Corregir `enroll`, que descarta silenciosamente el resultado de `form.is_valid()` (`activities/views.py:24-27`). | Preexistente y ajeno a F1. Anotado porque F1 añade una vista sister y conviene no copiar el patrón. |
| **M-08** | Exponer `cancelled_at` en el `list_display` del admin de `Registration` con etiqueta Derived. | De **D2** y `F1-R27`. Permite al docente ver de un vistazo cuántas bajas hubo. |

### 6.4 Preguntas pendientes

Ninguna bloquea la implementación de F1 tal como está especificado. Las cuatro abiertas cambian detalles, no la arquitectura.

| # | Pregunta | Opciones | Efecto si se decide |
| --- | --- | --- | --- |
| **P-01** | ¿Cómo se comunica el instante límite, dada la tensión **L-31** entre precisión de microsegundos y display de minutos? | (a) Mostrar el límite con segundos. (b) Mostrarlo en minutos y aceptar que no es exacto. (c) No mostrarlo; solo el mensaje de rechazo con el plazo en texto. | Cambia el filtro de fecha en `detail.html` / `mine.html` y el texto de `window_closed`. No cambia la regla. |
| **P-02** | Cuando el docente reprograma una actividad y el plazo se cierra de golpe, ¿debe F1 avisar a los titulares? | (a) No, F1 no notifica (**S-07**). (b) Aviso diferido, que es trabajo nuevo. | **(a)** deja todo como está. **(b)** abre un ítem de alcance. |
| **P-03** | ¿La cancelación debe poder invocarse desde una ruta que apunte a la **inscripción** (`/registrations/<pk>/cancel/`) en vez de a la actividad? | (a) Por actividad, como `register` (**D6**). (b) Por inscripción. | **(b)** obliga a validar propiedad antes de responder y a devolver `404` o un genérico por ruta distinta; más superficie de fuga. Se recomienda **(a)**. |
| **P-04** | El seed ampliado (**D5**) crea la inscripción en la actividad ya iniciada con `Registration.objects.create` directo, porque `register()` la rechazaría con `started`. ¿Se acepta ese único alta que no pasa por el servicio? | (a) Sí, es un dato de demo. (b) No; que el escenario de plazo vencido se cubra solo por pruebas. | **(a)** deja el recorrido manual completo. **(b)** deja `E-08` sin demostrar en pantalla y hace que el seed emita un aviso de fallo en cada corrida. |

### 6.5 Mapa de impacto sobre el código

Para quien implemente, sin abrir nada: cada archivo, qué toca y por qué.

| Archivo | Cambio | Requisito |
| --- | --- | --- |
| `activities/models.py` | `cancelled_at` nullable en `Registration`; propiedad de estado derivada; `Activity.clean()` cuenta solo confirmadas | F1-R08, F1-R12, F1-R11, F1-R29 |
| `activities/migrations/0002_*.py` | Migración del campo. `makemigrations --check --dry-run` debe quedar limpio (`README.md:21`) | F1-R08 |
| `activities/services.py` | `WINDOW`; `cancel()`; carga filtrada en `with_availability()`; rama `not_reenrollable` y cupo lleno con solo confirmadas en `register()`; cuatro claves nuevas en `MESSAGES` | F1-R04, F1-R06, F1-R10, F1-R11, F1-R13 a F1-R17, F1-R20 a F1-R22 |
| `activities/views.py` | Vista `cancel_registration` (`login_required` + `require_POST`); contexto de estado en `detail` y en `mine`; `available` sigue siendo la carga filtrada | F1-R01, F1-R02, F1-R24, F1-R25, F1-R26 |
| `activities/urls.py` | `activities/<int:pk>/cancel/`, nombre `cancel` | F1-R24 |
| `templates/activities/detail.html` | Badge de estado, fecha de cancelación, botón condicionado al plazo, sin botón de inscripción tras cancelar | F1-R25, F1-R26 |
| `templates/activities/mine.html` | Ídem, por inscripción | F1-R25, F1-R26 |
| `activities/admin.py` | `cancelled_at` en `readonly_fields` y en `list_display` | F1-R27 |
| `activities/management/commands/seed_demo.py` | Dos inscripciones nuevas; `reset_demo` no cambia | D5, F1-R28, P-04 |
| `activities/tests/` | Casos de servicio, vista, los 23 límites de §5 y dos de concurrencia | §4, §5 |
| `README.md` | Recorrido con cancelación, nueva tabla de resultados, casos del seed | — |

**Ningún archivo de `static/` cambia:** los mensajes se renderizan con `class="message {{ message.tags }}"` (`templates/base.html`) y `.message` ya tiene estilo genérico, así que las claves nuevas no necesitan CSS.

### 6.6 Criterio de terminado

- [ ] `python manage.py test --noinput` pasa, con los casos de §4 y §5.
- [ ] `python manage.py check` sin avisos.
- [ ] `python manage.py makemigrations --check --dry-run` sin cambios pendientes.
- [ ] Las tres preguntas de §6.4 con efecto de comportamiento están respondidas: **P-01** es la única que cambia lo que ve el estudiante.
- [ ] El recorrido del `README` permite demostrar **E-06** (deshabilitada cancelable) y **E-08** (plazo vencido) sin preparar datos a mano.

### 6.7 Registro de aprobación T01 (etapa 0)

Fecha: 2026-10-08. Responsable: docente (registra implementador A).

| Ítem | Estado | Detalle |
| --- | --- | --- |
| F-01 | aceptado | Cinco claves nuevas en `MESSAGES` (`cancelled`, `already_cancelled`, `window_closed`, `not_cancellable`, `not_reenrollable`); corrige §6.5 fila `services.py` («cuatro» → «cinco»). |
| F-02 | aceptado | P-04 son dos altas directas (deshabilitada e iniciada), ninguna por `register()`, ambas con guarda de existencia por `(student, activity)`. |
| F-03 | aceptado | M-02 promovido al alcance de F1 como mecanismo de F1-R26. |
| P-01 | aceptado opción (c) | La interfaz muestra la regla («hasta 24 h antes del inicio»), no un instante derivado. |
| P-02 | aceptado opción (a) | No notificar al reprogramar. |
| P-03 | aceptado opción (a) | Ruta por actividad (D6). |
| P-04 | aceptado opción (a) con corrección F-02 | Sí a las dos altas directas con guarda de existencia. |
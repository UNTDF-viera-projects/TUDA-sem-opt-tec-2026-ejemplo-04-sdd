# Tarea 10 · Matriz de cobertura y revisión spec/plan/tareas (cierre, sin código)

- [x] **T10 · Verificar cobertura total R/E/L y declarar faltantes y ciclos antes de implementar**
- **Estado:** `cerrada` (aprobada por reviewer F1 2026-10-09: matriz conciliada contra 66 tests reales; R01…R29/E-01…E-17/L-01…L-30 sin huecos; L-13/L-14 probados en `test_L09_L16_matrix` — hallazgo documentado en §Faltantes.5 basta; sin ciclos bloqueantes)

## Resultado concreto

Matriz requisito → decisión del plan → tarea → verificación aprobada (abajo), conciliada el 2026-10-09 contra los nombres reales de tests en `test_cancel_service/views/concurrency`. Todo F1-R01…R29 y E-01…E-17 y L-01…L-30 tiene fila con tarea y test real ejecutado (T02…T09 cerradas con evidencia ejecutada — ver §Cierre T02…T09). Trabajo faltante y ciclos declarados en §Faltantes y §Dependencias. Con T10 en verde, spec + plan + tareas quedan listos para revisar antes de implementar.

## Archivos / componentes afectados

- Este archivo (`docs/f1/task-10.md`) + `docs/f1/task-01.md`…`task-09.md` como objeto de revisión.
- Sin código de aplicación.

## Requisitos y escenarios que cubre

- Transversal: audita la cobertura de todos los demás. No implementa reglas.

## Dependencias

- Depende de: T01…T09 redactadas (lectura, no ejecución). No bloquea implementación salvo por revisión: nada de T02…T09 se cierra sin su evidencia ejecutada.

## Condición de cierre comprobable

- Cada fila de la matriz tiene tarea asignada y verificación con nombre de test o comando.
- `grep -c "F1-R" docs/f1/task-*.md` cubre R01…R29 sin huecos; ídem E-01…E-17 y L-01…L-30.
- Faltantes y ciclos declarados abajo, sin ciclos bloqueantes.

## Prueba / evidencia para cerrarla

- Revisión docente de spec + plan + task-01…task-10 firmada (evidencia documental).
- ~~Todas las tareas T02…T09 siguen pendientes~~ — **corregido 2026-10-09**: T01…T09 ya están cerradas, cada una con su evidencia ejecutada (ver §Cierre T02…T09: salidas de `test`/`check`/`makemigrations`/Docker y recorrido manual). T10 no sustituye esas evidencias; solo las audita documentalmente.

---

## Matriz de cobertura (requisito → decisión → tarea → verificación)

> Auditoría T10 (2026-10-09): columna «Verificación» conciliada contra los nombres
> reales de `activities/tests/test_cancel_service.py`,
> `test_cancel_views.py` y `test_cancel_concurrency.py`
> (listado completo en §Evidencia T10). Donde la redacción previa usaba un nombre
> aproximado se sustituye por el real; la cobertura lógica no cambia salvo
> L-13/L-14 (ver §Faltantes punto 5).

| Requisito | Decisión del plan | Tarea | Verificación (test real ejecutado) |
| --- | --- | --- | --- |
| F1-R01 | DD-07 + DD-05 (filtro por titular) | T04 (vista/servicio), T03 | `test_E03_foreign_is_generic`, `test_L09_L16_matrix` (L-13/L-14/L-16: ajena→genérico sin fuga; A/B) |
| F1-R02 | DD-07 (`login_required`+`require_POST`+CSRF) | T04 | `test_E14_L24_get_is_405_without_effect`, `test_L25_post_without_csrf_is_403`, `test_L26_anonymous_redirects_to_login` |
| F1-R03 | DD-05 (rama genérica) + DD-07 (sin 404) | T04 (servicio en T03) | Comparación E-03 vs E-04 vs E-05 (`test_E03_E04_E05_identical_response`, `test_E03_foreign_is_generic`, `test_E04_missing_is_same_as_foreign`, `test_E05_missing_activity_no_404`); `test_L15_missing_activity_is_generic` |
| F1-R04 | DD-03 (`WINDOW`, `cancellation_deadline`) | T03 | `test_L01_minus_one_hour_allows`, `test_L02_minus_one_second_allows` |
| F1-R05 | DD-03 (`<=`, sin redondeo) | T03 (+ display en T05) | `test_L03_deadline_inclusive_allows`, `test_L04_one_microsecond_past_rejected`, `test_L05_plus_one_second_rejected`, `test_L06_plus_59min_rejected`, `test_L07_at_start_rejected` |
| F1-R06 | DD-05 (reloj dentro del `atomic`) | T08 (§7 del plan) | `test_R06_clock_read_inside_atomic_after_lock` + `test_R06_clock_inside_window_allows` + `test_clock_after_lock_inside_window_allows` / `test_clock_after_lock_outside_window_rejects` (concurrency) + `assert_called_once` + `in_atomic_block` |
| F1-R07 | DD-03 (`starts_at` vigente) | T03 | `test_R07_reschedule_reopens_and_closes_window` (S-02) |
| F1-R08 | DD-01 (misma fila) | T02 (+ T03) | `test_E01_effective_cancel_keeps_row_and_frees_one` (+ vista `test_E01_post_cancels_redirects_mine`), migración aditiva §3 |
| F1-R09 | DD-05 (update condicional) | T03 | `test_E09_repetition_keeps_original_date`, `test_L19_repeat_does_not_free_second` |
| F1-R10 | DD-05 (un UPDATE) + unique | T03 | `test_E02_exactly_one_seat`, `test_L17_single_seat_cancel_frees_one`, `test_E13_concurrent_pair_single_transition` |
| F1-R11 | DD-04 (3 puntos, mismo commit) | T02 (`clean`) + T03 (2 puntos) | `test_E15_L18_freed_seat_is_bookable`→ nombre real `test_E15_L18_freed_seat_is_registerable_guardian` (guardián X-01); `test_L20_load_counts_only_confirmed`, `test_L21_L22_E16_capacity_floor_over_confirmed`, `test_L22_below_confirmed_rejected`, `test_E16_L21_reduce_to_confirmed_count_saves` |
| F1-R12 | DD-01 (un solo campo) | T02 | Revisión de modelo |
| F1-R13 | DD-05 (rama + update condicional) | T03 | `test_E09_repetition_keeps_original_date`, `test_L19_repeat_does_not_free_second` |
| F1-R14 | DD-05 (repetición antes que plazo) | T03 | `test_E10_repetition_outside_window_still_already`, `test_L09_L16_matrix` (L-10/L-11/L-12) |
| F1-R15 | DD-05 (sin reloj en la rama) | T03 | `test_R15_repetition_does_not_read_clock` (`timezone.now` que falla si se invoca → `already_cancelled`) |
| F1-R16 | DD-05 (IMMEDIATE + condicional) | T08 | `test_E13_concurrent_pair_single_transition` (cubre L-23: una sola transición, `available` 0→1), defensa aislada `test_conditional_write_alone_returns_already` (0 filas → `already_cancelled`) |
| F1-R17 | DD-05 (`locked`→`busy`) | T03 + T08 | `test_L28_locked_returns_busy_without_effect` (servicio) + `test_L28_locked_is_busy_without_effect` (concurrency), `test_L29_other_operational_error_propagates` |
| F1-R18 | DD-05 (sin guarda `is_active`) | T03 (+ demo T07) | `test_E06_disabled_still_cancellable` |
| F1-R19 | DD-05 (`is_active` omitida) | T03 | `test_E06_disabled_still_cancellable` + revisión de código (sin guarda) |
| F1-R20 | DD-06 (`not_reenrollable`) | T03 | `test_E11_reenroll_rejected_with_own_message` (assert `not_reenrollable`, `count()` invariante) |
| F1-R21 | DD-06 + F-01 (texto en MESSAGES) | T01 + T03 | `test_E11_reenroll_rejected_with_own_message` (`assertNotEqual` vs `already_registered`) + `test_F01_five_keys_present` |
| F1-R22 | DD-06 (precedencia) | T03 | `test_E12_reenroll_wins_over_disabled_started_full` |
| F1-R23 | DD-06 + UniqueConstraint | T03 | `test_E11_reenroll_rejected_with_own_message` (`count()` invariante) |
| F1-R24 | DD-07 (destino único `mine`) | T04 | `test_all_five_results_redirect_mine_with_key` (302 a `/my-registrations/` en los 5 resultados) |
| F1-R25 | DD-09 (badges + fecha) | T05 | `test_R25_cancelled_shows_date_not_confirmed` (`assertNotContains` «confirmada» sobre cancelada; fecha visible) |
| F1-R26 | DD-03 (helper compartido, F-03) | T03 + T04 + T05 | `test_R26_button_matches_service_decision` + `test_R26_button_hidden_outside_window` (botón ⇔ concesión con reloj parchado) |
| F1-R27 | DD-10 (admin) | T06 | `test_E16_L21_reduce_to_confirmed_count_saves`, `test_L22_below_confirmed_rejected`, `test_cancelled_at_readonly_in_edit_and_present_in_list` |
| F1-R28 | DD-11 (`reset_demo` intacto) | T07 | `test_reset_rebuilds_confirmed` + `test_second_run_preserves_cancellation` + `test_seed_creates_two_confirmed` (`reset_demo` tras cancelaciones reconstruye confirmadas) |
| F1-R29 | DD-02 (`is_cancelled`) | T02 (+ T05) | `test_T02_is_cancelled_true_when_dated` / `test_T02_is_cancelled_false_when_no_date`; nadie repite `cancelled_at is None` |
| D1…D6 | DD-01/DD-04/DD-06/DD-03/DD-11/DD-08-09 | T02/T03/T07/T04-T05 | Ver filas de cada R asociado |
| E-01…E-17 | Según matriz R | T03/T04/T05/T06/T07/T08 | `test_E01`…`test_E17` 1:1 reales (E-13 en T08 `test_E13_concurrent_pair_single_transition`, E-16 en T06 `test_E16_L21_reduce_to_confirmed_count_saves`, E-17 en T07 `test_seed_creates_two_confirmed`) |
| L-01…L-30 | Según matriz R | T03/T04/T08 | `test_L01`…`test_L30` reales (L-13/L-14 dentro de `test_L09_L16_matrix`; L-23 dentro del test E-13; L-24…L-26+L-30 en T04; L-28/L-29 en T03+T08) |
| L-31/P-01 | §14 propuesta (c) | T01 (decide) + T05/T09 (muestra regla, no instante) | Decisión escrita; sin test de borde falso |
| F-01/F-02/F-03 | Plan §1 | T01 (aprueba) → T03/T07/T03 | Docs + `test_F01_five_keys_present` y `test_E11_reenroll_rejected_with_own_message` (F-01), seed idempotente `test_second_run_preserves_cancellation` (F-02), helper compartido `test_R26_button_matches_service_decision` (F-03) |
| P-02/P-03/P-04 | Plan §14 | T01 → T07/T04 | (a)/(a)/(a+F-02); P-04 con guarda de existencia |

## Faltantes (trabajo sin cobertura o fuera de F1)

1. L-31/P-01: pendiente de decisión docente en T01; la propuesta (c) no requiere código, pero si se elige (a)/(b) hay que editar T05/T09 (filtro de fecha + texto de `window_closed`).
2. Mejoras M-01…M-08 salvo M-02 (promovida por F-03) y M-08 (adoptada por D2): fuera de alcance, sin tarea — correcto según plan §10.2.
3. S-01…S-09, X-01…X-05: supuestos/tensiones documentados, no trabajo; X-01 se protege con E-15 en T03 (`test_E15_L18_freed_seat_is_registerable_guardian`).
4. `enroll` que descarta `form.is_valid()` (M-07): preexistente, fuera de F1; T04 no debe copiar el patrón pero tampoco lo corrige.
5. Brecha de nombrado detectada por la auditoría T10 (2026-10-09, sin hueco de cobertura lógica): ningún `task-*.md` mencionaba literalmente `L-13`/`L-14`, y la matriz T10 usaba nombres de tests aproximados que no existen (`test_E03_foreign_returns_generic`, `test_L16_cancel_A_leaves_B`, `test_E11_no_row_created`, `test_E11_message_not_already_registered`, `test_E11_row_count_unchanged`, `test_L15_unknown_activity_generic`, `test_is_cancelled`, etc.). Cobertura real: L-13/L-14 están probados dentro de `test_L09_L16_matrix` (`test_cancel_service.py:243-246`, ajena con deshabilitada/iniciada → `not_cancellable` sin fuga) y L-23 dentro de `test_E13_concurrent_pair_single_transition`; la matriz de arriba queda conciliada con los nombres reales. No se crea tarea nueva: queda como observación documental.

## Dependencias y ciclos

- Grafo: T01 → T02 → T03 → {T04 → T05, T06 (vía T02), T07, T08} → T09 → T10 (revisión). T06 solo necesita T02; T07/T08 solo necesitan T03 (más T02 para T07).
- Sin dependencias circulares: T05 no vuelve a T03 (consume el helper, no lo redefine); T08 solo toca servicios si un test lo exige, en cuyo caso se re-ejecuta T03 antes de T04/T05.
- Riesgo de orden: DD-04 exige que los 3 puntos de cupo (T02+T03) se commiteen juntos (X-01/R-1); T02 y T03 no se entregan por separado en ramas distintas.
- Estado del grafo a 2026-10-09: T01…T09 **cerradas** (ver §Cierre T02…T09 abajo). T10 es la única revisión pendiente y no bloquea nada ya implementado; solo su propia firma docente.

## Cierre T02…T09 (constancia de evidencia ejecutada, auditoría T10 2026-10-09)

Corrección a la nota anterior («T02…T09 siguen pendientes»): a la fecha de esta
auditoría **T01…T09 están cerradas**, cada una con su evidencia ejecutada:

- T01 `cerrada` — evidencia documental (diff spec/plan con decisiones F-01…F-03, P-01…P-04); no requiere ejecución por diseño.
- T02 `cerrada` — `migrate` + `check` + `makemigrations --check --dry-run` + `test_cancel_service.RegistrationModelTests` (`is_cancelled` F/V, `clean()` piso sobre confirmadas) + evidencia manual sobre copia de `db.sqlite3`.
- T03 `cerrada` — `test_cancel_service` + `test_base` (L-01…L-08, L-09…L-16, L-17…L-23, E-09/E-10 fecha idéntica, E-11/E-12 mensaje propio, R07 reprogramación, asimetría register/cancel).
- T04 `cerrada` (reviewer F1 2026-10-08: `CancelViewTests` 12/12 OK; 5 resultados 302 a `/my-registrations/`; E-03/E-04/E-05 idénticos sin 404; GET 405 / sin-CSRF 403 / anónimo a login; `now` único; identidad `request.user`).
- T05 `cerrada` (reviewer F1 2026-10-08: `TemplateTests` 4/4 OK; botón⇔`cancel()` mismo `now`; `assertNotContains` confirmada + `cancelled_at` visible; L-27 `count=1`).
- T06 `cerrada` — `test_cancel_views.AdminTests` + verificación manual `/admin/` (`cancelled_at` visible, readonly, sin alta/baja).
- T07 `cerrada` — `test_cancel_views.SeedResetTests` + evidencia manual (`seed_demo` ×2 con cancelación intermedia, `reset_demo --confirm` + `seed_demo` reconstruye).
- T08 `cerrada` (reviewer F1 2026-10-08: 3 corridas verdes 6 tests OK en `test_cancel_concurrency`; E-13 ⊆ {cancelled, already, busy} sin doble cancelled + `available` 0→1; escritura condicional + reloj `assert_called_once` en `atomic` + `busy` selectivo).
- T09 `cerrada` — suite en verde con uv **y** Docker (`test --noinput`, `check`, `makemigrations --check --dry-run`, `docker compose up --build` + `exec web … test`) + recorrido manual E-06/E-08.

## Evidencia T10 (revisión documental, sin código de aplicación)

Salidas adjuntas de la auditoría 2026-10-09 (T10 no ejecuta tests; audita papeles):

```
$ grep -c "F1-R" docs/f1/task-*.md
docs/f1/task-01.md:2
docs/f1/task-02.md:2
docs/f1/task-03.md:2
docs/f1/task-04.md:1
docs/f1/task-05.md:1
docs/f1/task-06.md:1
docs/f1/task-07.md:2
docs/f1/task-08.md:1
docs/f1/task-09.md:0
docs/f1/task-10.md:31
→ F1-R01…F1-R29 todos presentes (únicos, ordenados): R01 R02 … R29 sin huecos.
→ E-01…E-17 todos presentes (ambas formas E-NN/E-N): 01 02 … 17 sin huecos.
→ L-01…L-30 todos presentes (ambas formas LNN/L-NN): verificación por
  `for i in $(seq -w 1 30); do grep -ql "L$i\|L-$i" docs/f1/task-*.md || echo MISSING; done`
  → sin MISSING. L-08 vía T03 (rango L-01…L-08); L-10/L-11/L-12 vía matriz
  F1-R14; L-13/L-14 vía matriz F1-R01 + §Faltantes.5; L-23 vía matriz F1-R16.

$ grep -o "def test_[a-zA-Z0-9_]*" activities/tests/test_cancel_service.py \
    activities/tests/test_cancel_views.py activities/tests/test_cancel_concurrency.py | sort
→ 6 (concurrency) + 38 (service) + 22 (views) = 66 tests reales; cada nombre
  citado en la matriz de arriba existe verbatim en ese listado
  (clases: RegistrationModelTests, CancelMessagesTests, CancelDeadlineTests,
  CancelStateTests, CancelCapacityTests, ReenrollTests, CancelClockAndBusyTests,
  CancelViewTests, TemplateTests, AdminTests, SeedResetTests,
  CancelConcurrencyTests + BaseTests/ConcurrencyTests).

$ git log --oneline -8 -- docs/f1/ activities/tests/
600638a X-01: T02+T03 modelo cancelled_at + servicios cancel (R-1)
72a68f4 feat: demo base
(nota: docs/f1/*.md y los tests de cancelación están sin commitear a la fecha;
el diff de esta auditoría es solo docs/f1/task-10.md — ver git diff --stat.)

$ git diff --stat -- docs/f1/task-10.md
→ único archivo tocado por T10 (esta revisión); sin código de aplicación.
```

- Estado T10: `cerrada` — auditoría documental completa y firmada por reviewer F1
  2026-10-09 (spec + plan + task-01…task-10 revisados).

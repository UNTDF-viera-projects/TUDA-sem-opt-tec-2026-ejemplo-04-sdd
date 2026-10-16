# Tarea 01 · Aprobación de hallazgos y preguntas abiertas (etapa 0 del plan)

- [x] **T01 · Aprobar F-01/F-02/F-03 y P-01…P-04 antes de codificar**
- **Estado:** cerrada

## Resultado concreto

`docs/f1/spec.md` y/o `docs/f1/plan.md` dejan constancia de la decisión docente sobre los tres hallazgos (F-01, F-02, F-03) y las cuatro preguntas (P-01…P-04, propuesta del plan en `plan.md §14`), o se rechazan con alternativa escrita. Sin esta aprobación no se inicia la etapa 1.

## Archivos / componentes afectados

- `docs/f1/spec.md` (§6.4 P-04, §6.5 fila `services.py`)
- `docs/f1/plan.md` (§1 F-01…F-03, §14 P-01…P-04)
- Sin código de aplicación en esta tarea.

## Requisitos y escenarios que cubre

- F-01: cinco claves nuevas en `MESSAGES` (`cancelled`, `already_cancelled`, `window_closed`, `not_cancellable`, `not_reenrollable`) — base de F1-R20/F1-R21.
- F-02: dos altas directas en seed (Bruno en deshabilitada, Ana en iniciada) con guarda de existencia — base de D5/E-17.
- F-03: promover M-02 (helper único) al alcance de F1 — base de F1-R26.
- P-01 (L-31, propuesta (c)), P-02 (a), P-03 (a, D6), P-04 (a con corrección F-02).

## Dependencias

- Ninguna. Bloquea a T02…T09.

## Condición de cierre comprobable

- Cada ítem F-01/F-02/F-03 y P-01…P-04 tiene estado escrito `aceptado` / `rechazado con alternativa` en spec o plan, con fecha y responsable.
- Si hay un rechazo, la tarea que lo implementa (T03/T05/T07/T09) referencia la alternativa.

## Prueba / evidencia para cerrarla

- Diff de `docs/f1/spec.md` y/o `docs/f1/plan.md` mostrando las decisiones (evidencia documental, no ejecutada).
- `git log --oneline -3` y `git diff --stat` de los docs.
- No requiere `manage.py test`. El cierre es revisión docente, no ejecución.

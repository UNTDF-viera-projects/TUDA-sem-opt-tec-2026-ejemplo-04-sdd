Usa la versión revisada de docs/f1/spec.md y el código actual para crear docs/f1/plan.md.

Conserva Django con templates, autenticación por sesión, SQLite, uv y Docker.

El plan debe explicar:

- El diseño propuesto y las decisiones técnicas, con sus motivos.
- Los cambios en modelos y la migración de inscripciones existentes.
- Los cambios en servicios, consultas de cupos, vistas, templates y Admin.
- Cómo se comprobarán titularidad, plazo y repetición.
- Cómo se protegerán las operaciones concurrentes.
- Cómo se tomará una decisión temporal correcta si la operación espera por un bloqueo.
- Cómo seed y los reinicios conservarán las cancelaciones.
- La estrategia de pruebas, ejecución y recuperación.
- Los riesgos y las alternativas consideradas.

Vincula las decisiones y verificaciones con los identificadores de la spec. Identifica los archivos afectados y el orden de trabajo.

Si encuentras una omisión en la spec, informa el hallazgo y propone una corrección explícita antes de continuar.

Entrega el plan y detente para su revisión, conservando el código de la aplicación.

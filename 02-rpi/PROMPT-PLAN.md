PLAN

Queremos agregar la posibilidad de cancelar una inscripción nombraremos esta funcionalidad F1.

Estas son las reglas acordadas:

- Solo el titular puede cancelar su inscripción.
- Se permite cancelar cuando faltan al menos 24 horas para el inicio, inclusive, sin redondear.
- La inscripción se conserva como cancelada, con su fecha de cancelación.
- Una cancelación exitosa libera exactamente un cupo.
- Repetir la cancelación conserva la fecha original y no libera otro cupo, incluso fuera del plazo.
- Una actividad deshabilitada permite cancelar si se cumple el plazo.
- Debe existir una confirmación previa. La ejecución usa POST, sesión autenticada y CSRF.
- Las solicitudes ajenas o inexistentes reciben una respuesta genérica sin revelar datos.
- Dos cancelaciones simultáneas deben producir una sola transición.
- La reinscripción queda fuera de F1 y debe rechazarse de forma comprensible.

Justifica las decisiones técnicas. Entrega el plan en la conversación y detente antes de implementar.

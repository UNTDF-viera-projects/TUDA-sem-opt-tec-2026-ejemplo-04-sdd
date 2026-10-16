Queremos agregar cancelación de inscripciones (a la que llamaremos F1) con estas reglas:

- Solo cancela el titular de la inscripción.
- Se permite cancelar hasta 24 horas antes del inicio, inclusive y sin redondear.
- Se conserva la misma inscripción como cancelada, con su fecha de cancelación.
- Cancelar libera exactamente un cupo.
- Repetir la cancelación conserva la fecha original y no libera otro cupo, incluso fuera del plazo.
- Una actividad deshabilitada permite cancelar si se cumple el plazo.
- Una inscripción ajena o inexistente recibe la misma respuesta genérica, sin revelar datos.
- Dos cancelaciones simultáneas producen una sola transición.
- La reinscripción queda fuera de F1 y se rechaza de forma comprensible.

Igualmente quiero que explores el código y verifiques si necesitamos considerar algo extra. Y propongas mejoras.

Crea docs/f1/spec.md con:

1. Contexto, objetivo y alcance.
2. Vocabulario con terminos estables.
2. Requisitos con identificadores estables.
3. Escenarios de aceptación expresados como Dado/Cuando/Entonces.
4. Casos límite y resultados esperados.
5. Supuestos y preguntas pendientes.

Hazme todas las preguntas que consideres y clarifica conmigo cualquier aspecto

Describe comportamientos observables y criterios verificables. Señala cualquier contradicción o decisión pendiente.

Entrega la especificación y detente para su revisión, conservando el código de la aplicación.

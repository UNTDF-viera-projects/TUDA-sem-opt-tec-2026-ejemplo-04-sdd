# Fundamentos de SDD · Guion docente

Cada ID enlaza a la diapositiva. Los estados base, F1 y F2 se distinguen en cada nota.

## sdd-01 · De prompts a especificaciones

- Propósito: Spec-Driven Development · UNTDF · 2026
- Explicación: Presentar SDD como forma de conducir trabajo con agentes y documentos revisables. No es una propiedad de un modelo.
- Conclusión: Spec-Driven Development · UNTDF · 2026
- Pregunta: ¿Cómo sabemos que el agente resolvió la necesidad correcta?
- Estado del ejemplo: Objetivo de aprendizaje
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-01`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-02 · Qué podremos hacer al terminar

- Propósito: Seguir una decisión desde el pedido hasta su evidencia.
- Explicación: Conectar brevemente con las clases anteriores: harness coordina contexto, reglas, herramientas y permisos. Esa infraestructura permite trabajar, pero todavía debemos acordar qué cambio queremos. Presentar cuatro resultados de aprendizaje y seguir la misma inscripción hasta su evidencia; no repetir la clase de herramientas.
- Conclusión: Seguir una decisión desde el pedido hasta su evidencia.
- Pregunta: ¿Qué evidencia conservarían para que otra persona pueda retomar el cambio?
- Estado del ejemplo: Objetivo de aprendizaje
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-02`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-03 · El sistema que vamos a ampliar

- Propósito: Base del alumno: inscribirse y consultar sus inscripciones.
- Explicación: PD-01. Estado inicial: base restaurada y seed_demo; cuenta ana / untdf-demo-2026. Acción: iniciar sesión, consultar catálogo/detalle, inscribirse y abrir Mis inscripciones. Resultado: inscripción propia confirmada y cupo actualizado. La captura procede del recorrido real del coordinador sobre copia limpia 8004. En clase la base usa 8000. Recuperación: README de la base, captura y resultado.json. Volver a sdd-03.
- Conclusión: Base del alumno: inscribirse y consultar sus inscripciones.
- Pregunta: ¿Qué recorrido puede ejecutar hoy un estudiante y qué acción todavía no existe?
- Estado del ejemplo: Base verificada · captura real
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-03`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-04 · Queremos cancelar una inscripción

- Propósito: El pedido expresa intención; todavía deja decisiones abiertas.
- Explicación: El pedido expresa intención; todavía deja decisiones abiertas.
- Conclusión: El pedido expresa intención; todavía deja decisiones abiertas.
- Pregunta: ¿Qué tendrían que decidir antes de escribir código?
- Estado del ejemplo: Decisiones del caso
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-04`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-05 · Dos soluciones plausibles

- Propósito: Las decisiones faltantes producen comportamientos diferentes.
- Explicación: No presentar una técnica como universalmente incorrecta. En nuestro caso se acuerda conservar el historial.
- Conclusión: Las decisiones faltantes producen comportamientos diferentes.
- Pregunta: ¿Qué necesidad de negocio justificaría borrar el registro o conservarlo?
- Estado del ejemplo: Comparación hipotética
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-05`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-06 · Qué falta decidir

- Propósito: Las preguntas anticipan efectos que después deberán probarse.
- Explicación: Las preguntas anticipan efectos que después deberán probarse.
- Conclusión: Las preguntas anticipan efectos que después deberán probarse.
- Pregunta: ¿Quién puede responder estas preguntas y qué pasa si el agente decide sin consultarlas?
- Estado del ejemplo: Decisiones del caso
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-06`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-07 · De preguntas a decisiones

- Propósito: Cada respuesta debe quedar registrada y ser revisable.
- Explicación: Mostrar el registro de preguntas y decisiones de material-docente/cancelacion. Son decisiones del caso, no inferencias de la frase inicial.
- Conclusión: Cada respuesta debe quedar registrada y ser revisable.
- Pregunta: ¿Dónde registrarían la regla de repetición para no volver a discutirla durante la implementación?
- Estado del ejemplo: Decisiones del caso
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-07`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-08 · Alcance de F1

- Propósito: Cancelación primero; reinscripción como extensión posterior.
- Explicación: Cancelación primero; reinscripción como extensión posterior.
- Conclusión: Cancelación primero; reinscripción como extensión posterior.
- Pregunta: ¿Por qué volver a inscribirse no es una tarea pendiente de cancelar?
- Estado del ejemplo: Decisiones del caso
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-08`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-09 · Un prompt largo puede seguir siendo ambiguo

- Propósito: La diferencia está en el comportamiento verificable.
- Explicación: Pedir que identifiquen expresiones sin condición observable: segura, cuando corresponda, bien.
- Conclusión: La diferencia está en el comportamiento verificable.
- Pregunta: ¿Podrían dos pruebas contradictorias pasar con el borrador?
- Estado del ejemplo: Decisiones del caso
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-09`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-10 · Investigar el sistema real

- Propósito: Separar observaciones, hipótesis y preguntas.
- Explicación: PD-02. Estado inicial: checkpoint base verificado, sin estado cancelado. Acción: abrir activities/models.py, services.py, vistas/templates y tests de la base; distinguir unicidad, cupo calculado, IMMEDIATE y sesión. Resultado esperado: hechos con referencias y preguntas para F1; no respuestas deducidas automáticamente del código. Recuperación: material-docente/cancelacion/research.md guardado y base.tar.gz. Volver sdd-10.
- Conclusión: Separar observaciones, hipótesis y preguntas.
- Pregunta: ¿Qué parte del repositorio confirma cómo se calcula la disponibilidad?
- Estado del ejemplo: Base investigada · research.md
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-10`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-11 · RPI: conducir el trabajo

- Propósito: Research–Plan–Implement es un patrón de trabajo.
- Explicación: Introducir RPI aquí antes de compararlo con SDD. Verificación sigue siendo necesaria aunque no figure en la sigla.
- Conclusión: Research–Plan–Implement es un patrón de trabajo.
- Pregunta: ¿Qué resultado debería dejar cada etapa?
- Estado del ejemplo: Concepto
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-11`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-12 · Research: mirar y registrar

- Propósito: Investigar el repositorio antes de decidir cómo modificarlo.
- Explicación: Investigar el repositorio antes de decidir cómo modificarlo.
- Conclusión: Investigar el repositorio antes de decidir cómo modificarlo.
- Pregunta: ¿Qué hallazgo observado cambiaría el plan técnico sin cambiar la necesidad del negocio?
- Estado del ejemplo: Concepto aplicado
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-12`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-13 · Plan: elegir una estrategia

- Propósito: Una regla puede cumplirse mediante distintos diseños.
- Explicación: La spec fija efectos. El plan explica responsabilidades, consistencia y tradeoffs sobre SQLite.
- Conclusión: Una regla puede cumplirse mediante distintos diseños.
- Pregunta: ¿Qué alternativa técnica consideraron y qué hecho permite justificar la elegida?
- Estado del ejemplo: Estrategia del caso
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-13`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-14 · Implement: ejecutar y comprobar

- Propósito: Realizar cambios acotados y contrastarlos con lo acordado.
- Explicación: Realizar cambios acotados y contrastarlos con lo acordado.
- Conclusión: Realizar cambios acotados y contrastarlos con lo acordado.
- Pregunta: ¿Qué prueba relaciona el cambio de código con una regla acordada?
- Estado del ejemplo: Decisiones del caso
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-14`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-15 · RPI y artefactos de SDD

- Propósito: La investigación y la especificación se refinan entre sí.
- Explicación: No imponer un orden universal: puede existir un borrador de spec antes del research. SDD aporta artefactos durables y trazabilidad.
- Conclusión: La investigación y la especificación se refinan entre sí.
- Pregunta: ¿Qué sucede con la spec cuando research descubre una restricción que no conocíamos?
- Estado del ejemplo: Decisiones del caso
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-15`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-16 · Cinco conceptos, un mismo caso

- Propósito: Cada artefacto agrega información distinta.
- Explicación: Cada artefacto agrega información distinta.
- Conclusión: Cada artefacto agrega información distinta.
- Pregunta: ¿Cuál de estos cinco conceptos define el resultado y cuál describe cómo alcanzarlo?
- Estado del ejemplo: Decisiones del caso
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-16`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-17 · De intención a requisito

- Propósito: Una regla identifica sujeto, condición y resultado.
- Explicación: Una regla identifica sujeto, condición y resultado.
- Conclusión: Una regla identifica sujeto, condición y resultado.
- Pregunta: ¿Cómo comprobarían esta regla sin conocer los detalles de la implementación?
- Estado del ejemplo: Decisiones del caso
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-17`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-18 · Anatomía de una especificación

- Propósito: Estructura y fragmento: objetivo y alcance.
- Explicación: Fragmento literal del documento completo enlazado; leer sección resaltada y explicar qué decisión o ambigüedad resuelve. Estructura y fragmento: objetivo y alcance.
- Conclusión: Estructura y fragmento: objetivo y alcance.
- Pregunta: ¿En qué sección encontraría el agente el alcance y en cuál una condición de aceptación?
- Estado del ejemplo: Documento completo real · F1
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-18`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-19 · Requisitos y restricciones

- Propósito: Un identificador permite seguir la regla durante el cambio.
- Explicación: Fragmento literal del documento completo enlazado; leer sección resaltada y explicar qué decisión o ambigüedad resuelve. Un identificador permite seguir la regla durante el cambio.
- Conclusión: Un identificador permite seguir la regla durante el cambio.
- Pregunta: ¿Las 24 horas exactas pertenecen al caso aceptado o al rechazado?
- Estado del ejemplo: Documento completo real · F1
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-19`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-19b · Cupo y repetición en la spec

- Propósito: Dos requisitos diferentes; dos efectos observables.
- Explicación: Fragmento literal del documento completo enlazado; leer sección resaltada y explicar qué decisión o ambigüedad resuelve. Dos requisitos diferentes; dos efectos observables.
- Conclusión: Dos requisitos diferentes; dos efectos observables.
- Pregunta: ¿Qué campos y conteos deben permanecer iguales al repetir?
- Estado del ejemplo: Documento completo real · F1
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-19b`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-20 · Escenarios observables

- Propósito: Condición, acción y resultado; también los rechazos.
- Explicación: Fragmento literal del documento completo enlazado; leer sección resaltada y explicar qué decisión o ambigüedad resuelve. Condición, acción y resultado; también los rechazos.
- Conclusión: Condición, acción y resultado; también los rechazos.
- Pregunta: ¿Qué dato, acción y resultado hacen reproducible cada escenario?
- Estado del ejemplo: Documento completo real · F1
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-20`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-21 · Criterios de aceptación

- Propósito: Decidir qué evidencia exige cada regla.
- Explicación: Decidir qué evidencia exige cada regla.
- Conclusión: Decidir qué evidencia exige cada regla.
- Pregunta: ¿Qué evidencia falta si sólo sabemos que la página devuelve HTTP 200?
- Estado del ejemplo: Decisiones del caso
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-21`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-22 · Revisar antes de planificar

- Propósito: Caso preparado para detectar omisión y ambigüedad.
- Explicación: Ejercicio preparado, no salida de una herramienta. Pedir al grupo que proponga un escenario faltante antes de mostrar la revisión.
- Conclusión: Caso preparado para detectar omisión y ambigüedad.
- Pregunta: ¿Qué dos implementaciones distintas permite todavía el fragmento defectuoso?
- Estado del ejemplo: Ejercicio de revisión
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-22`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-23 · Qué agrega un plan

- Propósito: Estrategia técnica basada en el sistema investigado.
- Explicación: Fragmento literal de Arquitectura y datos hasta la conservación de unicidad, con omisión indicada. Explicar por qué F1 conserva unique(student,activity) y F2 requerirá cambiarla. El plan no es una lista de archivos: justifica preservación e impactos.
- Conclusión: Estrategia técnica basada en el sistema investigado.
- Pregunta: ¿Qué agrega esta decisión técnica que todavía no está en el requisito?
- Estado del ejemplo: Documento completo real · F1
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-23`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-24 · Responsabilidades del cambio

- Propósito: Django con templates: una regla, varias superficies.
- Explicación: No agregar frontend o API para enseñar F1. En la base no existe cancelación: mostrar el antes/después en su copia docente.
- Conclusión: Django con templates: una regla, varias superficies.
- Pregunta: ¿Dónde se revalida el plazo si el usuario deja abierta la confirmación?
- Estado del ejemplo: Arquitectura propuesta F1
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-24`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-25 · Mantener consistente el cupo

- Propósito: Decisión técnica conectada con un resultado observable.
- Explicación: Explicar consistencia sin afirmar que select_for_update proporciona bloqueo real en SQLite. La solución debe justificar su mecanismo.
- Conclusión: Decisión técnica conectada con un resultado observable.
- Pregunta: ¿Qué riesgo aparece si guardamos a la vez un contador de cupo y estados de inscripción?
- Estado del ejemplo: Decisiones del caso
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-25`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-26 · Orden y dependencias

- Propósito: El orden protege la interpretación de los datos.
- Explicación: El orden protege la interpretación de los datos.
- Conclusión: El orden protege la interpretación de los datos.
- Pregunta: ¿Qué tarea no puede iniciarse antes de aplicar la migración?
- Estado del ejemplo: Decisiones del caso
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-26`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-27 · La validación también se planifica

- Propósito: No esperar al final para decidir qué comprobar.
- Explicación: Fragmento literal del plan final: mantener las 22 pruebas de base y probar concurrencia con conexiones reales. La sección completa también cubre migración, fronteras temporales, titularidad, UI/CSRF y repetición. Los puntos suspensivos identifican selección; el documento completo conserva estrategia y evidencia.
- Conclusión: No esperar al final para decidir qué comprobar.
- Pregunta: ¿Por qué hacen falta conexiones independientes para probar concurrencia?
- Estado del ejemplo: Documento completo real · F1
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-27`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-28 · Anatomía de una tarea

- Propósito: Una tarea contiene acción, dependencia y condición de cierre.
- Explicación: Tarea real F1-T05: acción de servicio, dependencia T04 y condición de cierre literal. La estructura editorial reorganiza celdas de la tabla para proyectar; no inventa un formato producido por OpenSpec o Spec Kit. T08/T09 documentan pruebas/logs; el criterio obliga a titularidad, reserva IMMEDIATE, repetición antes de plazo y única transición. Abrir tasks.md completo y contrastar cierre con CancellationTests/CancellationConcurrencyTests antes de afirmar Hecha.
- Conclusión: Una tarea contiene acción, dependencia y condición de cierre.
- Pregunta: ¿Qué evidencia permite cerrar T05 y qué tarea debe estar terminada antes?
- Estado del ejemplo: Documento completo real · F1
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-28`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-29 · Dividir trabajo sin perder intención

- Propósito: Las dependencias describen qué debe estar listo primero.
- Explicación: Grafo resumido de tasks.md real. Mostrar desde F1-T04 persistencia hasta F1-T07 interfaz, y T08 prueba global. No son IDs hipotéticos: T06 cubre cupos y rechazo explícito F2. T09 ejecuta uv/Docker y T10 guarda checkpoint y trazabilidad.
- Conclusión: Las dependencias describen qué debe estar listo primero.
- Pregunta: ¿Qué trabajo puede avanzar en paralelo sin romper estas dependencias?
- Estado del ejemplo: Decisiones del caso
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-29`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-30 · “Modificar el modelo” no alcanza

- Propósito: Reformular una tarea para poder revisarla.
- Explicación: Reformular una tarea para poder revisarla.
- Conclusión: Reformular una tarea para poder revisarla.
- Pregunta: ¿Qué falta en “modificar el modelo” para que otra persona sepa cuándo terminó?
- Estado del ejemplo: Ejercicio de revisión
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-30`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-31 · Trazabilidad del plazo

- Propósito: Requisito → decisión → tarea → prueba identificable.
- Explicación: PD-03. Estado inicial: spec, plan y tasks de F1 revisados junto a matriz trazabilidad.md y pruebas reales. Acción: seguir la regla de plazo inclusivo hasta decisión, tarea F1-T05/T06/T08 y funciones de test mostradas. Resultado esperado: cada eslabón tiene identificador y evidencia; una casilla no sustituye una prueba. Recuperación: documentos completos en material-docente/cancelacion y código test_f1.py de practicas/solucion-f1; logs guardados si no se ejecuta suite. Volver sdd-31.
- Conclusión: Requisito → decisión → tarea → prueba identificable.
- Pregunta: ¿Qué prueba detectaría un cambio accidental de ≥24 h a >24 h?
- Estado del ejemplo: F1 implementado · trazabilidad real
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-31`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-31b · Trazabilidad de cupos

- Propósito: Requisito → decisión → tarea → prueba identificable.
- Explicación: PD-03. Estado inicial: spec, plan y tasks de F1 revisados junto a matriz trazabilidad.md y pruebas reales. Acción: seguir la regla de cupo liberado hasta decisión, tarea F1-T05/T06/T08 y funciones de test mostradas. Resultado esperado: cada eslabón tiene identificador y evidencia; una casilla no sustituye una prueba. Recuperación: documentos completos en material-docente/cancelacion y código test_f1.py de practicas/solucion-f1; logs guardados si no se ejecuta suite. Volver sdd-31b.
- Conclusión: Requisito → decisión → tarea → prueba identificable.
- Pregunta: ¿Cómo demostrarían que cancelar libera exactamente un cupo reutilizable por otro estudiante?
- Estado del ejemplo: F1 implementado · trazabilidad real
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-31b`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-31c · Trazabilidad de la repetición

- Propósito: Requisito → decisión → tarea → prueba identificable.
- Explicación: PD-03. Estado inicial: spec, plan y tasks de F1 revisados junto a matriz trazabilidad.md y pruebas reales. Acción: seguir la regla de repetición sin segundo efecto hasta decisión, tarea F1-T05/T06/T08 y funciones de test mostradas. Resultado esperado: cada eslabón tiene identificador y evidencia; una casilla no sustituye una prueba. Recuperación: documentos completos en material-docente/cancelacion y código test_f1.py de practicas/solucion-f1; logs guardados si no se ejecuta suite. Volver sdd-31c.
- Conclusión: Requisito → decisión → tarea → prueba identificable.
- Pregunta: ¿Qué prueba detectaría que repetir una cancelación modifica su fecha original?
- Estado del ejemplo: F1 implementado · trazabilidad real
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-31c`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-32 · Estados y efectos de F1

- Propósito: Cancelar conserva el registro y cambia su participación en el cupo.
- Explicación: Cancelar conserva el registro y cambia su participación en el cupo.
- Conclusión: Cancelar conserva el registro y cambia su participación en el cupo.
- Pregunta: ¿Qué transición produce la primera cancelación y cuál produce el segundo intento?
- Estado del ejemplo: Decisiones del caso
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-32`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-33 · El borde de las 24 horas

- Propósito: Tiempo restante = inicio − ahora; no tiempo desde la inscripción.
- Explicación: Tiempo restante = inicio − ahora; no tiempo desde la inscripción.
- Conclusión: Tiempo restante = inicio − ahora; no tiempo desde la inscripción.
- Pregunta: ¿Qué diferencia hay entre tiempo restante y tiempo transcurrido en esta línea?
- Estado del ejemplo: Decisiones del caso
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-33`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-34 · Repetir una cancelación

- Propósito: La condición temporal no se reaplica a una inscripción ya cancelada.
- Explicación: La condición temporal no se reaplica a una inscripción ya cancelada.
- Conclusión: La condición temporal no se reaplica a una inscripción ya cancelada.
- Pregunta: ¿Por qué la repetición después del inicio sigue devolviendo ya cancelada?
- Estado del ejemplo: Decisiones del caso
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-34`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-35 · Implementar sobre una copia

- Propósito: La base del alumno sigue siendo el punto de partida.
- Explicación: PD-04: partir del checkpoint F1 y datos reiniciados. Recuperación: copia docente y evidencia guardada. Abrir documento de cambios reales.
- Conclusión: La base del alumno sigue siendo el punto de partida.
- Pregunta: ¿Por qué se comprueba el estado cancelado antes de leer el plazo?
- Estado del ejemplo: F1 implementado · servicio y reloj reales
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-35`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-35a · Cancelar en la aplicación real

- Propósito: PD-04 · confirmar intención y consultar el resultado.
- Explicación: Estado inicial: copia docente F1, seed con cuenta ana/untdf-demo-2026, inscripción Taller confirmada. Acción: abrir confirmación y enviar formulario. Resultado real del coordinador: registro conserva ID y fecha, disponibilidad 2→3; repetir mantiene 3. Captura clickeable para verla completa. Recuperación: f1-browser/03-cancelada.png,04-disponibilidad.png,05-repeticion.png y resultado.json. El volumen Docker 8011 quedó con esta inscripción cancelada; reset explícito antes de repetir la clase. Volver sdd-35a.
- Conclusión: PD-04 · confirmar intención y consultar el resultado.
- Pregunta: ¿Qué vemos antes de enviar el POST y qué evidencia queda después?
- Estado del ejemplo: Captura y recorrido real · F1
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-35a`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-36 · Verificar lo acordado

- Propósito: Documentos, pruebas y aplicación deben contar la misma historia.
- Explicación: PD-05. Estado inicial: solución F1 final con 37 pruebas (22 de base y 15 F1). Abrir salida local/Docker o ejecutar desde practicas/solucion-f1; seguir plazo, repetición, migración y concurrencia hasta test_f1.py. Reloj 2030-10-01T12:00:00Z evita depender de la hora de clase. Recuperación: evidencia/f1-local-tests.txt, f1-docker-tests.txt y verificacion.md; volver a sdd-36. Los logs históricos 21/36 están preservados y no representan el paquete final.
- Conclusión: Documentos, pruebas y aplicación deben contar la misma historia.
- Pregunta: ¿Qué requisito acredita cada familia de pruebas y cuál necesita además observar la interfaz?
- Estado del ejemplo: Resultado ejecutado · uv y Docker
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-36`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-37 · Si no cumple, ¿a dónde volvemos?

- Propósito: Ejercicio: a las 24 horas exactas se produce un rechazo.
- Explicación: Caso preparado, no fallo observado. Evitar caricatura de waterfall: los retornos responden a evidencia.
- Conclusión: Ejercicio: a las 24 horas exactas se produce un rechazo.
- Pregunta: ¿Cómo distinguirían un defecto de código de una ambigüedad de spec?
- Estado del ejemplo: Ejercicio preparado
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-37`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-37a · Un hallazgo real modifica el plan

- Propósito: El instante de decisión debe medirse después de adquirir la reserva.
- Explicación: Hallazgo real en revisión técnica de F1: capturar tiempo antes de la reserva podía aceptar una petición que cruza 24 h durante la espera. Se actualizó plan, servicio, tareas, trazabilidad y tests; suites 35→36. La revisión posterior encontró el mismo riesgo en inscripción al cruzar inicio: corrección transversal D-B07 y prueba nueva; base final 22, F1 final 37. No cambió la intención ni se añadió F2. Contrastar OpenSpec OS17: detectó la necesidad como omisión documental antes de implementar. Evidencia y logs históricos/finales preservados en verificacion.md.
- Conclusión: El instante de decisión debe medirse después de adquirir la reserva.
- Pregunta: ¿Por qué pasa de corregir código a actualizar también plan, tareas y evidencia?
- Estado del ejemplo: Iteración real · F1 corregido y verificado
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-37a`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-38 · Recuperar la intención del cambio

- Propósito: Versionar artefactos permite retomar decisiones.
- Explicación: Versionar artefactos permite retomar decisiones.
- Conclusión: Versionar artefactos permite retomar decisiones.
- Pregunta: ¿Qué debería leer un nuevo agente para recuperar la razón de una decisión?
- Estado del ejemplo: Decisiones del caso
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-38`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-39 · Quién decide y quién revisa

- Propósito: El agente propone; las personas revisan intención y evidencia.
- Explicación: No atribuir una función universal a todos los agentes. Las capacidades concretas dependen del entorno e integración.
- Conclusión: El agente propone; las personas revisan intención y evidencia.
- Pregunta: ¿Qué decisión corresponde al negocio y qué propuesta técnica puede hacer el agente?
- Estado del ejemplo: Decisiones del caso
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-39`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-40 · Un nuevo pedido: volver a inscribirse

- Propósito: F2 modifica F1; todavía no se implementa en esta entrega.
- Explicación: F2 crea un registro nuevo y conserva el cancelado con su fecha. Cambiaría la unicidad por estudiante/actividad para admitir historial cancelado y una sola inscripción confirmada. Revisar spec, plan, tareas y pruebas antes de desarrollar. Cupo, habilitación y comienzo siguen siendo reglas de inscripción; el límite de 24 h pertenece a cancelar. Extensión conceptual pendiente, sin código F2 en esta entrega.
- Conclusión: F2 modifica F1; todavía no se implementa en esta entrega.
- Pregunta: ¿Por qué F2 necesita revisar unicidad en lugar de reactivar la inscripción cancelada?
- Estado del ejemplo: Extensión conceptual F2
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-40`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-41 · Conducir el cambio con preguntas

- Propósito: Una revisión atraviesa todo el recorrido.
- Explicación: Una revisión atraviesa todo el recorrido.
- Conclusión: Una revisión atraviesa todo el recorrido.
- Pregunta: ¿En qué etapa volverían si la evidencia contradice una decisión del plan?
- Estado del ejemplo: Decisiones del caso
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-41`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-42 · OpenSpec: especificaciones y cambios

- Propósito: Una herramienta para organizar artefactos y evolución.
- Explicación: Una herramienta para organizar artefactos y evolución.
- Conclusión: Una herramienta para organizar artefactos y evolución.
- Pregunta: ¿Qué diferencia hay entre una especificación vigente y un delta de cambio?
- Estado del ejemplo: Panorama · ver guía de versión comprobada
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-42`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-43 · Spec Kit: conducir el recorrido

- Propósito: Principios, feature, estrategia, tareas y revisión.
- Explicación: Principios, feature, estrategia, tareas y revisión.
- Conclusión: Principios, feature, estrategia, tareas y revisión.
- Pregunta: ¿Qué artefacto conecta los principios del proyecto con las tareas ejecutables?
- Estado del ejemplo: Panorama · ver guía de versión comprobada
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-43`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-44 · Práctica sobre la base

- Propósito: Desarrollar F1 sin abrir la solución docente al comenzar.
- Explicación: Desarrollar F1 sin abrir la solución docente al comenzar.
- Conclusión: Desarrollar F1 sin abrir la solución docente al comenzar.
- Pregunta: ¿Cómo comprobarán que su práctica conserva la base y no incorpora F2?
- Estado del ejemplo: Decisiones del caso
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-44`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sdd-45 · Material para retomar el recorrido

- Propósito: La intención se conserva junto al resultado.
- Explicación: La intención se conserva junto al resultado.
- Conclusión: La intención se conserva junto al resultado.
- Pregunta: ¿Qué archivo abrirían para recuperar el comportamiento, la estrategia o la evidencia?
- Estado del ejemplo: Decisiones del caso
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sdd-45`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.

# Spec Kit paso a paso · Guion docente

Cada ID enlaza a la diapositiva. Los estados base, F1 y F2 se distinguen en cada nota.

## sk-01 · F1 con Spec Kit

- Propósito: El mismo cambio y las mismas reglas de aceptación.
- Explicación: El mismo cambio y las mismas reglas de aceptación.
- Conclusión: El mismo cambio y las mismas reglas de aceptación.
- Pregunta: ¿Qué criterios de F1 se mantienen iguales aunque cambie el formato de los artefactos?
- Estado del ejemplo: Recorrido real completo · leer README y logs
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sk-01`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sk-02 · Otra copia de la base

- Propósito: Código, datos y requisitos iguales; entorno independiente.
- Explicación: PD-07: partir del mismo checkpoint que OpenSpec y verificar manifiesto antes de implementar. Origen histórico común: base-v1.tar.gz, SHA d01f06… y 21 pruebas, conservado intacto. La corrección transversal posterior produjo base v2 final de 22 pruebas; no se presenta esa base nueva como origen ya ejecutado. Confirmar puerto 8013 y proyecto Compose independiente antes de mostrar la copia. Para exponer sin agente, abrir documentos y evidencia guardada; volver a sk-02.
- Conclusión: Código, datos y requisitos iguales; entorno independiente.
- Pregunta: ¿Qué manifiesto demuestra el origen común con OpenSpec?
- Estado del ejemplo: Recorrido real completo · leer README y logs
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sk-02`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sk-03 · Mapa del recorrido

- Propósito: Cada etapa produce contexto para la siguiente revisión.
- Explicación: Cada etapa produce contexto para la siguiente revisión.
- Conclusión: Cada etapa produce contexto para la siguiente revisión.
- Pregunta: ¿Qué producto deja cada etapa y a dónde volvemos si falla la verificación?
- Estado del ejemplo: Recorrido real completo · leer README y logs
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sk-03`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sk-04 · Preparar las tres capas

- Propósito: La app puede funcionar sin instalar Spec Kit.
- Explicación: Commit completo: 838f1184d1b2ed254a99e8b818dbc23aa80a7f1f. No interpretar dev0 como release estable.
- Conclusión: La app puede funcionar sin instalar Spec Kit.
- Pregunta: ¿Qué versión e integración explican las invocaciones que veremos?
- Estado del ejemplo: Recorrido real completo · leer README y logs
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sk-04`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sk-04a · Usar Spec Kit con commit fijado

- Propósito: Terminal en sdd · script reproducible de preparación.
- Explicación: El wrapper specify.sh contiene el commit completo 838f1184d1b2ed254a99e8b818dbc23aa80a7f1f. Ejecutar desde sdd para versión; luego entrar en practicas/spec-kit. La siguiente diapositiva emplea el mismo wrapper desde esa copia.
- Conclusión: Terminal en sdd · script reproducible de preparación.
- Pregunta: ¿Por qué fijamos un commit además del nombre de la herramienta?
- Estado del ejemplo: Instalación real · script guardado
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sk-04a`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sk-05 · Inicializar el proyecto

- Propósito: Terminal · dentro de la copia Spec Kit.
- Explicación: Terminal · dentro de la copia Spec Kit.
- Conclusión: Terminal · dentro de la copia Spec Kit.
- Pregunta: ¿Qué estructura creó specify init y qué contenido todavía no está decidido?
- Estado del ejemplo: CLI ejecutada · init.txt
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sk-05`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sk-06 · Invocar desde el lugar correcto

- Propósito: Las capacidades se llaman en la conversación de Codex.
- Explicación: Las capacidades se llaman en la conversación de Codex. La diapositiva abrevia la entrada para proyectar; el registro completo enlazado conserva contexto y decisiones realmente usados. La invocación corresponde a la integración Codex verificada.
- Conclusión: Las capacidades se llaman en la conversación de Codex.
- Pregunta: ¿Qué diferencia hay entre specify init y $speckit-specify?
- Estado del ejemplo: Recorrido real completo · leer README y logs
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sk-06`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sk-07 · Constitución: principios del proyecto

- Propósito: Orientar decisiones comunes antes de diseñar una feature.
- Explicación: Método real: agente de esta ejecución leyó y aplicó skills instaladas; CLI y scripts nativos se ejecutaron con logs. No se afirma invocación slash en UI. Orientar decisiones comunes antes de diseñar una feature.
- Conclusión: Orientar decisiones comunes antes de diseñar una feature.
- Pregunta: ¿Qué decisión concreta obliga a preservar datos e historial?
- Estado del ejemplo: Artefacto nativo real · Spec Kit commit fijado
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sk-07`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sk-08 · Principios aplicados a la demo

- Propósito: Un principio es útil si permite revisar una decisión.
- Explicación: Un principio es útil si permite revisar una decisión.
- Conclusión: Un principio es útil si permite revisar una decisión.
- Pregunta: ¿Cómo condiciona Django clásico el plan sin convertirse en una regla del negocio?
- Estado del ejemplo: Recorrido real completo · leer README y logs
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sk-08`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sk-09 · Especificar el cambio

- Propósito: Entrada de negocio: comportamiento, alcance y restricciones.
- Explicación: Entrada de negocio: comportamiento, alcance y restricciones. La diapositiva abrevia la entrada para proyectar; el registro completo enlazado conserva contexto y decisiones realmente usados. La invocación corresponde a la integración Codex verificada.
- Conclusión: Entrada de negocio: comportamiento, alcance y restricciones.
- Pregunta: ¿Qué información de F1 debe incluir la entrada para no delegar decisiones del negocio?
- Estado del ejemplo: Recorrido real completo · leer README y logs
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sk-09`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sk-10 · Leer la especificación generada

- Propósito: Formato nativo: historias, requisitos y éxito medible.
- Explicación: Método real: agente de esta ejecución leyó y aplicó skills instaladas; CLI y scripts nativos se ejecutaron con logs. No se afirma invocación slash en UI. Formato nativo: historias, requisitos y éxito medible.
- Conclusión: Formato nativo: historias, requisitos y éxito medible.
- Pregunta: ¿Qué relación hay entre una historia, FR-002 y su criterio de éxito?
- Estado del ejemplo: Artefacto nativo real · Spec Kit commit fijado
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sk-10`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sk-11 · Detectar lo que sigue ambiguo

- Propósito: Aclarar antes de planificar evita consolidar supuestos.
- Explicación: Aclarar antes de planificar evita consolidar supuestos.
- Conclusión: Aclarar antes de planificar evita consolidar supuestos.
- Pregunta: ¿Qué ambigüedad existiría si no se hubiera fijado repetición fuera de plazo?
- Estado del ejemplo: Recorrido real completo · leer README y logs
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sk-11`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sk-12 · Aclarar y guardar decisiones

- Propósito: Skill opcional elegida para resolver preguntas de este caso.
- Explicación: Método real: agente de esta ejecución leyó y aplicó skills instaladas; CLI y scripts nativos se ejecutaron con logs. No se afirma invocación slash en UI. Clarify real aplicó check-prerequisites y revisión de cobertura. Resultado 0 nuevas preguntas porque el usuario ya fijó todas las reglas. No se simula una conversación de aclaraciones. Sigue plan técnico. La diapositiva abrevia la entrada para proyectar; el registro completo enlazado conserva contexto y decisiones realmente usados. La invocación corresponde a la integración Codex verificada.
- Conclusión: Skill opcional elegida para resolver preguntas de este caso.
- Pregunta: ¿Por qué la revisión de claridad puede concluir con cero preguntas?
- Estado del ejemplo: Artefacto nativo real · Spec Kit commit fijado
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sk-12`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sk-13 · Revisar calidad de requisitos

- Propósito: Comprobar claridad y aceptación antes de pasar al plan.
- Explicación: Método real: agente de esta ejecución leyó y aplicó skills instaladas; CLI y scripts nativos se ejecutaron con logs. No se afirma invocación slash en UI. Comprobar claridad y aceptación antes de pasar al plan.
- Conclusión: Comprobar claridad y aceptación antes de pasar al plan.
- Pregunta: ¿Qué revisa una checklist de requisitos que todavía no pueden demostrar tests de código?
- Estado del ejemplo: Artefacto nativo real · Spec Kit commit fijado
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sk-13`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sk-14 · Contexto técnico para el plan

- Propósito: Ahora sí: stack, arquitectura observada y restricciones.
- Explicación: Ahora sí: stack, arquitectura observada y restricciones. La diapositiva abrevia la entrada para proyectar; el registro completo enlazado conserva contexto y decisiones realmente usados. La invocación corresponde a la integración Codex verificada.
- Conclusión: Ahora sí: stack, arquitectura observada y restricciones.
- Pregunta: ¿Qué contexto técnico necesita el plan además de la spec de negocio?
- Estado del ejemplo: Recorrido real completo · leer README y logs
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sk-14`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sk-15 · Leer el plan y sus productos

- Propósito: La estrategia tiene razones y productos técnicos relacionados.
- Explicación: Método real: agente de esta ejecución leyó y aplicó skills instaladas; CLI y scripts nativos se ejecutaron con logs. No se afirma invocación slash en UI. La estrategia tiene razones y productos técnicos relacionados.
- Conclusión: La estrategia tiene razones y productos técnicos relacionados.
- Pregunta: ¿Por qué data-model y contratos acompañan al plan en esta versión?
- Estado del ejemplo: Artefacto nativo real · Spec Kit commit fijado
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sk-15`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sk-16 · Revisar decisiones contra la spec

- Propósito: La implementación propuesta debe preservar el comportamiento.
- Explicación: La implementación propuesta debe preservar el comportamiento.
- Conclusión: La implementación propuesta debe preservar el comportamiento.
- Pregunta: ¿Cómo justificamos IMMEDIATE a partir del riesgo de transición simultánea?
- Estado del ejemplo: Recorrido real completo · leer README y logs
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sk-16`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sk-17 · Generar tareas

- Propósito: Traducir estrategia a trabajo ejecutable.
- Explicación: Traducir estrategia a trabajo ejecutable. La diapositiva abrevia la entrada para proyectar; el registro completo enlazado conserva contexto y decisiones realmente usados. La invocación corresponde a la integración Codex verificada.
- Conclusión: Traducir estrategia a trabajo ejecutable.
- Pregunta: ¿Qué parte del plan debe estar estable antes de generar tareas?
- Estado del ejemplo: Recorrido real completo · leer README y logs
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sk-17`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sk-18 · Leer dependencias y cierre

- Propósito: Formato nativo con IDs; paralelizar sólo lo independiente.
- Explicación: Método real: agente de esta ejecución leyó y aplicó skills instaladas; CLI y scripts nativos se ejecutaron con logs. No se afirma invocación slash en UI. Formato nativo con IDs; paralelizar sólo lo independiente.
- Conclusión: Formato nativo con IDs; paralelizar sólo lo independiente.
- Pregunta: ¿Qué evidencia cierra T008 y qué dependencia tiene?
- Estado del ejemplo: Artefacto nativo real · Spec Kit commit fijado
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sk-18`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sk-19 · Analizar consistencia

- Propósito: La revisión puede detectar requisitos sin cobertura.
- Explicación: Método real: agente de esta ejecución leyó y aplicó skills instaladas; CLI y scripts nativos se ejecutaron con logs. No se afirma invocación slash en UI. Análisis real guardado. T008 implementaba rechazo F2 pero no incluía test explícito SF1-08; T002 preservaba datos pero sin prueba con datos anteriores. Analyze no editó documentos. La corrección siguiente se realizó fuera de esa skill.
- Conclusión: La revisión puede detectar requisitos sin cobertura.
- Pregunta: ¿Qué omisión encontró analyze y por qué no la corrigió durante el análisis?
- Estado del ejemplo: Artefacto nativo real · Spec Kit commit fijado
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sk-19`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sk-20 · Corregir donde corresponde

- Propósito: Dos omisiones reales se corrigen antes de implementar.
- Explicación: Ejercicio preparado explícito. Si el hallazgo cambia intención, volver a spec; si falta ejecución, corregir tareas.
- Conclusión: Dos omisiones reales se corrigen antes de implementar.
- Pregunta: ¿Qué archivo se corrige para cada hallazgo y qué revisión se repite después?
- Estado del ejemplo: Corrección real · artefactos; no resultado de código
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sk-20`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sk-21 · Implementar lo revisado

- Propósito: Conversación del agente · no basta con completar casillas.
- Explicación: Aplicación real de la skill leída por el agente actual. Hubo tests rojos por servicio inexistente y primera pasada 37/38 por fixture de sesión 2030; se corrigió expiración del fixture. La intención F1 no cambió. Leer tests-rojo.txt y tests-primer-verde.txt en el recorrido. Código propio de esta copia, no copiar solución genérica. La diapositiva abrevia la entrada para proyectar; el registro completo enlazado conserva contexto y decisiones realmente usados. La invocación corresponde a la integración Codex verificada.
- Conclusión: Conversación del agente · no basta con completar casillas.
- Pregunta: ¿Qué nos enseña un test rojo antes de implementar la lógica?
- Estado del ejemplo: Recorrido real completo · leer README y logs
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sk-21`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sk-22 · Verificar la misma F1

- Propósito: Terminal y aplicación · comparar contra escenarios acordados.
- Explicación: Resultado final: 39 tests locales y Docker, 9 comprobaciones UI guardadas. Desglose: 21 de baseline v1, 17 F1 y una corrección transversal D-B07; su prueba reproduce la espera de un escritor y cruce del inicio sin sleeps. La primera pasada de F1 tuvo 37/38 por vencimiento de fixture de sesión al cambiar reloj a 2030; se corrigió fixture, luego 38/38. La revisión técnica posterior añadió register bajo IMMEDIATE, final 39/39. Los logs de cada etapa quedan preservados; ningún fallo cambia la regla de negocio.
- Conclusión: Terminal y aplicación · comparar contra escenarios acordados.
- Pregunta: ¿Qué cambió entre la primera pasada y las 39 pruebas finales?
- Estado del ejemplo: Recorrido real completo · leer README y logs
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sk-22`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sk-22a · Spec Kit: resultado en la aplicación

- Propósito: Captura real · copia independiente en localhost:8013.
- Explicación: PD-07. Estado inicial: copiaSpecKit propia con seed y cuentaana/untdf-demo-2026. Mostrar formulario confirmado y resultado. Capturas guardadas por el revisor con Chrome 152 a1280x720 y9 asserts. Temporal exactamente 24 h y−1s se prueba con reloj fijo, no capturaen vivo. Recuperación: README/checkpoints y las seis capturas. Volver sk-22a.
- Conclusión: Captura real · copia independiente en localhost:8013.
- Pregunta: ¿Qué datos observables permanecen iguales al repetir la cancelación?
- Estado del ejemplo: Captura real · Spec Kit
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sk-22a`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sk-23 · Evaluar el resultado contra artefactos

- Propósito: Converge revisa implementación y evidencia después de implement.
- Explicación: Convergencia final real: 11 FR, 4 SC, 5 principios, 6 decisiones y 12 tareas contrastadas con código, 39 tests local/Docker y 9 comprobaciones UI. Cero gaps; los hashes tasks antes/después son iguales, sin fase vacía ni tarea inventada. La primera convergencia 38 tests/11 tareas está preservada en primera-pasada-converge.md. La revisión transversal posterior añadió T012 y prueba D-B07 fuera de converge; se corrigió implementación y luego se volvió a evaluar. Leer converge.md y revision-transversal.md; cantidad de tests no compara calidad con OpenSpec.
- Conclusión: Converge revisa implementación y evidencia después de implement.
- Pregunta: ¿Por qué cero gaps no exige agregar una fase vacía a tasks?
- Estado del ejemplo: Recorrido real completo · leer README y logs
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sk-23`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sk-24 · Cerrar y recuperar el recorrido

- Propósito: Guardar un estado reproducible y documentos coherentes.
- Explicación: Checkpoints reales material-docente/checkpoints/spec-kit-preimplementacion.tar.gz y spec-kit-f1.tar.gz, raíz spec-kit/. Extraer a carpeta nueva; uv sync --locked, migrate y seed_demo. Puerto 8013 / Compose sdd-speckit y SQLite independiente. Para una segunda copia simultánea cambiar ambos; nunca extraer sobre base alumno. Quickstart enlazado trae comandos completos. Resultado guardado permite continuar sin agente.
- Conclusión: Guardar un estado reproducible y documentos coherentes.
- Pregunta: ¿Qué checkpoint usarían para revisar el plan y cuál para mostrar el resultado?
- Estado del ejemplo: Recorrido real completo · leer README y logs
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sk-24`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sk-25 · Problemas de preparación y coherencia

- Propósito: La versión fijada define sintaxis e integración.
- Explicación: La orden fallida fue un ensayo deliberado y no mutante para enseñar lugares de invocación. Está realmente ejecutada. No proponer correr plan en terminal. Método de recuperación: Codex en la copia inicializada, skill $speckit-plan con contexto técnico. La segunda dificultad fue una omisión real en tareas y se corrigió antes de implementar.
- Conclusión: La versión fijada define sintaxis e integración.
- Pregunta: ¿Qué explica No such command plan y dónde se invoca el paso correcto?
- Estado del ejemplo: Recorrido real completo · leer README y logs
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sk-25`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## sk-26 · Referencia del recorrido

- Propósito: Principios y comportamiento antes de estrategia y tareas.
- Explicación: Principios y comportamiento antes de estrategia y tareas.
- Conclusión: Principios y comportamiento antes de estrategia y tareas.
- Pregunta: ¿Qué entrada, archivo y evidencia corresponden al siguiente paso del recorrido?
- Estado del ejemplo: Recorrido real completo · leer README y logs
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `sk-26`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.

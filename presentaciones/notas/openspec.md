# OpenSpec paso a paso · Guion docente

Cada ID enlaza a la diapositiva. Los estados base, F1 y F2 se distinguen en cada nota.

## os-01 · F1 con OpenSpec

- Propósito: Organizar un cambio concreto, implementarlo y conservar su intención.
- Explicación: Organizar un cambio concreto, implementarlo y conservar su intención.
- Conclusión: Organizar un cambio concreto, implementarlo y conservar su intención.
- Pregunta: ¿Qué criterios comunes permiten comparar este resultado con la solución docente?
- Estado del ejemplo: Recorrido real completo · CLI y Codex verificados
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `os-01`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## os-02 · Una copia del mismo checkpoint

- Propósito: El recorrido no recibe la solución docente ya implementada.
- Explicación: PD-06: verificar manifiesto del checkpoint y restaurar sólo esta copia. No usar la base del alumno para ejecutar cambios. Origen histórico común: base-v1.tar.gz, SHA d01f06… y 21 pruebas, conservado intacto. La corrección transversal posterior produjo base v2 final de 22 pruebas; no se presenta esa base nueva como origen ya ejecutado. Confirmar puerto 8012 y proyecto Compose independiente antes de mostrar la copia. Para exponer sin agente, abrir documentos y evidencia guardada; volver a os-02.
- Conclusión: El recorrido no recibe la solución docente ya implementada.
- Pregunta: ¿Cómo verificamos que las dos herramientas partieron de la misma base v1?
- Estado del ejemplo: Recorrido real completo · CLI y Codex verificados
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `os-02`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## os-03 · Sistema y cambios en curso

- Propósito: Las especificaciones del sistema y un cambio tienen vidas distintas.
- Explicación: Las especificaciones del sistema y un cambio tienen vidas distintas.
- Conclusión: Las especificaciones del sistema y un cambio tienen vidas distintas.
- Pregunta: ¿Qué documento describe el sistema hoy y cuál describe lo que proponemos cambiar?
- Estado del ejemplo: Recorrido real completo · CLI y Codex verificados
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `os-03`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## os-04 · Mapa de artefactos

- Propósito: Una ubicación reconocible para cada pregunta del cambio.
- Explicación: Una ubicación reconocible para cada pregunta del cambio.
- Conclusión: Una ubicación reconocible para cada pregunta del cambio.
- Pregunta: ¿Dónde buscarían la razón técnica de una tarea?
- Estado del ejemplo: Mapa esquemático
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `os-04`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## os-05 · Aplicación, herramienta y agente

- Propósito: Preparar cada capa por separado.
- Explicación: Instalar requiere Internet; consultar las diapositivas y documentos guardados no. Versiones verificadas por el coordinador.
- Conclusión: Preparar cada capa por separado.
- Pregunta: ¿Qué dependencia pertenece a Django y cuál a la herramienta de SDD?
- Estado del ejemplo: Recorrido real completo · CLI y Codex verificados
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `os-05`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## os-05a · Instalar la versión comprobada

- Propósito: Terminal en sdd · primera preparación con conexión.
- Explicación: Script reproducible usado por el coordinador. Ejecutar desde sdd, revisar CLI --version y exportar PATH en esa terminal. Después cd practicas/openspec para init. Recuperación: volver a correr instalación sin borrar código ni SQLite.
- Conclusión: Terminal en sdd · primera preparación con conexión.
- Pregunta: ¿Por qué fijar la versión local antes de reproducir el recorrido?
- Estado del ejemplo: Instalación real · script guardado
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `os-05a`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## os-06 · Inicializar en la carpeta correcta

- Propósito: Terminal · dentro de la copia OpenSpec de la demo.
- Explicación: Terminal desde practicas/openspec. Entrada exacta guardada en01-init.txt; salida real creó openspec/config.yaml y seis skills de Codex. Revisar .agents/skills antes de llamar $openspec-propose. Si skills no aparecen, reiniciar el agente desde la misma copia y comprobar init. No escribir la invocación $skill en terminal.
- Conclusión: Terminal · dentro de la copia OpenSpec de la demo.
- Pregunta: ¿Qué archivos confirma la salida real de init y cuáles todavía no genera?
- Estado del ejemplo: CLI ejecutada · 01-init.txt
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `os-06`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## os-07 · Invocar capacidades del agente

- Propósito: Los nombres de skills no son subcomandos de terminal.
- Explicación: Los nombres de skills no son subcomandos de terminal. La diapositiva abrevia la entrada para proyectar; el registro completo enlazado conserva contexto y decisiones realmente usados. La invocación corresponde a la integración Codex verificada.
- Conclusión: Los nombres de skills no son subcomandos de terminal.
- Pregunta: ¿Por qué escribir $openspec-propose en la terminal no invoca la skill del agente?
- Estado del ejemplo: Recorrido real completo · CLI y Codex verificados
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `os-07`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## os-08 · Registrar la base existente

- Propósito: Inicializar la herramienta no infiere automáticamente todas las reglas.
- Explicación: Leer el documento nativo completo enlazado y contrastar con la base y reglas F1. CLI Codex generó estos artefactos sobre copia independiente; no se presentan como los documentos genéricos del ejercicio. Inicializar la herramienta no infiere automáticamente todas las reglas.
- Conclusión: Inicializar la herramienta no infiere automáticamente todas las reglas.
- Pregunta: ¿Quién debe contrastar la spec de base con el código existente?
- Estado del ejemplo: Documento nativo real · OpenSpec1.14.0
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `os-08`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## os-09 · Explorar antes de proponer

- Propósito: Research conecta comportamiento actual y preguntas pendientes.
- Explicación: Leer el documento nativo completo enlazado y contrastar con la base y reglas F1. CLI Codex generó estos artefactos sobre copia independiente; no se presentan como los documentos genéricos del ejercicio. Research conecta comportamiento actual y preguntas pendientes. La diapositiva abrevia la entrada para proyectar; el registro completo enlazado conserva contexto y decisiones realmente usados. La invocación corresponde a la integración Codex verificada.
- Conclusión: Research conecta comportamiento actual y preguntas pendientes.
- Pregunta: ¿Qué hallazgo observado condiciona el diseño de cancelación?
- Estado del ejemplo: Documento nativo real · OpenSpec1.14.0
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `os-09`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## os-10 · Proponer la cancelación

- Propósito: La entrada expresa necesidad y reglas, sin imponer archivos a modificar.
- Explicación: Leer el documento nativo completo enlazado y contrastar con la base y reglas F1. CLI Codex generó estos artefactos sobre copia independiente; no se presentan como los documentos genéricos del ejercicio. La entrada expresa necesidad y reglas, sin imponer archivos a modificar. La diapositiva abrevia la entrada para proyectar; el registro completo enlazado conserva contexto y decisiones realmente usados. La invocación corresponde a la integración Codex verificada.
- Conclusión: La entrada expresa necesidad y reglas, sin imponer archivos a modificar.
- Pregunta: ¿Qué parte de la entrada fija negocio y qué parte debe proponer el agente?
- Estado del ejemplo: Documento nativo real · OpenSpec1.14.0
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `os-10`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## os-11 · Revisar objetivo y alcance

- Propósito: La propuesta delimita la entrega antes de invertir en implementación.
- Explicación: La propuesta delimita la entrega antes de invertir en implementación.
- Conclusión: La propuesta delimita la entrega antes de invertir en implementación.
- Pregunta: ¿Qué pedido tentador debe quedar fuera de cancelar-inscripcion?
- Estado del ejemplo: Recorrido real completo · CLI y Codex verificados
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `os-11`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## os-12 · Requisitos nuevos o modificados

- Propósito: Formato nativo de delta: qué añade el cambio al sistema.
- Explicación: Leer el documento nativo completo enlazado y contrastar con la base y reglas F1. CLI Codex generó estos artefactos sobre copia independiente; no se presentan como los documentos genéricos del ejercicio. Formato nativo de delta: qué añade el cambio al sistema.
- Conclusión: Formato nativo de delta: qué añade el cambio al sistema.
- Pregunta: ¿Qué significa SHALL en este delta y qué caso exacto debemos probar?
- Estado del ejemplo: Documento nativo real · OpenSpec1.14.0
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `os-12`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## os-13 · Escenarios de F1

- Propósito: La revisión incluye éxito, frontera, rechazo y repetición.
- Explicación: Leer el documento nativo completo enlazado y contrastar con la base y reglas F1. CLI Codex generó estos artefactos sobre copia independiente; no se presentan como los documentos genéricos del ejercicio. La revisión incluye éxito, frontera, rechazo y repetición.
- Conclusión: La revisión incluye éxito, frontera, rechazo y repetición.
- Pregunta: ¿Qué condición de WHEN hace reproducible el resultado THEN?
- Estado del ejemplo: Documento nativo real · OpenSpec1.14.0
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `os-13`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## os-14 · Diseño del cambio

- Propósito: La herramienta organiza; la decisión técnica requiere justificación.
- Explicación: Leer el documento nativo completo enlazado y contrastar con la base y reglas F1. CLI Codex generó estos artefactos sobre copia independiente; no se presentan como los documentos genéricos del ejercicio. La herramienta organiza; la decisión técnica requiere justificación.
- Conclusión: La herramienta organiza; la decisión técnica requiere justificación.
- Pregunta: ¿Qué decisión evita mantener dos fuentes de verdad sobre cupos?
- Estado del ejemplo: Documento nativo real · OpenSpec1.14.0
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `os-14`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## os-15 · Tareas para ejecutar

- Propósito: El trabajo conserva su vínculo con decisiones y escenarios.
- Explicación: El trabajo conserva su vínculo con decisiones y escenarios.
- Conclusión: El trabajo conserva su vínculo con decisiones y escenarios.
- Pregunta: ¿Qué dependencia y condición de cierre tiene la tarea 2.2?
- Estado del ejemplo: Tareas nativas reales · antes de apply
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `os-15`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## os-16 · Revisar antes de implementar

- Propósito: Una propuesta coherente requiere contrastar varios artefactos.
- Explicación: Una propuesta coherente requiere contrastar varios artefactos.
- Conclusión: Una propuesta coherente requiere contrastar varios artefactos.
- Pregunta: ¿Qué contradicción buscarían entre spec, diseño y tareas antes de aplicar?
- Estado del ejemplo: Recorrido real completo · CLI y Codex verificados
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `os-16`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## os-17 · Corregir una omisión real

- Propósito: La revisión documental descubre una prueba temporal que falta.
- Explicación: Hallazgo real R-01 del agente durante planificación. Se añadió tarea 5.4 y prueba en diseño§8; tarea de documentación se renumeró 5.5 y dependencias se alinearon. Se corrigió conteo 24→25. No cambia regla de negocio: completa su verificación. Antes y después preservados en evidence. En propuesta aún no se había ejecutado; apply posterior la comprobó con test_clock_sampled_after_real_immediate_reservation y dos conexiones reales. Mostrar snapshots previos y resultado final por separado.
- Conclusión: La revisión documental descubre una prueba temporal que falta.
- Pregunta: ¿Por qué un test con now fijo no demuestra qué ocurre mientras espera la reserva?
- Estado del ejemplo: Corrección documental real · revisión del agente
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `os-17`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## os-18 · Implementar el cambio revisado

- Propósito: Skill real de Codex CLI · 25 tareas ejecutadas en la copia independiente.
- Explicación: PD-06, etapa apply. Partir del checkpoint OpenSpec preimplementación, puerto 8012/proyecto sdd-openspec y datos ficticios; no tocar base del alumno. El agente CLI recibió la skill instalada $openspec-apply-change y implementó realmente. Primer intento se detuvo por cuota antes de código; reintento autorizado completó 25 tareas, migración, servicio, consultas, UI/CSRF, tests y documentos. Registrar errores/correcciones del propio recorrido sin fingir aprobación humana. Recuperación: 03-apply-reintento.jsonl, artefactos/previo, artefactos/final y openspec-final.tar.gz; volver os18/19. Entrada de pantalla resumida, registro completo conserva contexto.
- Conclusión: Skill real de Codex CLI · 25 tareas ejecutadas en la copia independiente.
- Pregunta: ¿Qué evidencia exige marcar una tarea como terminada?
- Estado del ejemplo: Recorrido real completo · CLI y Codex verificados
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `os-18`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## os-19 · Verificar comportamiento y coherencia

- Propósito: Terminal y aplicación · misma aceptación que la solución docente.
- Explicación: Verificación real local/Docker: 56 tests OK, Django check y ausencia de migraciones pendientes; migración0001→0002 conserva filas previas; concurrencia usa SQLite archivo y conexiones distintas. 16 observaciones de navegador por cada entorno complementan dominio/HTTP. Docker 8012, local temporal8014, ambos propios. Fronteras exactas y espera IMMEDIATE se comprueban con reloj controlado; número de tests no mide superioridad entre herramientas. Abrir local-suite.stderr.txt y docker-suite.stderr.txt completos; volver os19.
- Conclusión: Terminal y aplicación · misma aceptación que la solución docente.
- Pregunta: ¿Qué resultado de pruebas necesita además una comprobación visible de la aplicación?
- Estado del ejemplo: Recorrido real completo · CLI y Codex verificados
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `os-19`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## os-19a · El resultado en la aplicación real

- Propósito: Captura Docker8012 · complementa las pruebas con reloj controlado.
- Explicación: PD-06 aplicación: iniciar sesiónAna, Taller de agentes confirmado. GET muestra consecuencia sin escritura; POST cancela y libera un cupo; repetir conserva fecha. El recorrido también verificó ajena/inexistente indistinguibles, plazo12 h rechazado, laboratorio completo→cupo liberado para nuevo alumno y persistencia. 16 observaciones por entorno documentadas; capturas permiten exponer sin agente. La hora de captura 2026es resultado previo, no supuesto del reloj actual. El volumen conserva modificaciones; reset docente explícito antes de nueva clase, después de leerREADME. Abrir imagen completa si se necesita leer detalle; volver os19a.
- Conclusión: Captura Docker8012 · complementa las pruebas con reloj controlado.
- Pregunta: ¿Qué podemos observar en esta pantalla y qué demuestra sólo la prueba con reloj controlado?
- Estado del ejemplo: Captura real · Docker y código OpenSpec
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `os-19a`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## os-20 · Archivar y actualizar el sistema

- Propósito: Archivo ejecutado por el coordinador con la CLI nativa, después de verificar.
- Explicación: Después de tests 56 local/Docker y revisión del coordinador, se ejecutó CLI openspec archive cancelar-inscripcion --yes --json. Esta ejecución NO fue una invocación del agente externo a $openspec-archive-change, aunque esa skill está disponible en la integración. CLI sincronizó 9 ADDED/6 MODIFIED y archivó 2026-10-01-cancelar-inscripcion. El coordinador contrastó título/Purpose durable, 8 escenarios previos,15 delta requirements presentes,16 totales y0 changes activos; main strict válida con INFO de descripciones largas, sin errores. Leer04-archive.json/04-sync-comprobacion.json y spec vigente. No cerrar sólo porque se movió carpeta.
- Conclusión: Archivo ejecutado por el coordinador con la CLI nativa, después de verificar.
- Pregunta: ¿Qué debe verificarse antes de trasladar el delta a las specs vigentes?
- Estado del ejemplo: Recorrido real completo · CLI y Codex verificados
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `os-20`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## os-21 · Antes y después del cierre

- Propósito: El delta pasa a comportamiento vigente; el cambio queda como historia.
- Explicación: Árboles seleccionados de snapshots previos y finales exactos. El archivo no borra research, decisiones, revisión o evidence; se omitieron del árbol para proyectar. Specs de sistema ahora contienen F1; el delta archivado conserva la intención histórica. Cambios activos0, archive2026-10-01-cancelar-inscripcion. Abrir artefactos/final/openspec/specs/inscripciones/spec.md y seguir con os21a para ver fragmento vigente.
- Conclusión: El delta pasa a comportamiento vigente; el cambio queda como historia.
- Pregunta: ¿Cómo sabemos que F1 pasó a referencia vigente y no quedó sólo en historia?
- Estado del ejemplo: Recorrido real completo · CLI y Codex verificados
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `os-21`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## os-21a · F1 ya pertenece a la spec vigente

- Propósito: Fragmento del sistema tras sincronización y archivo, no sólo del delta.
- Explicación: Fragmento literal de spec vigente final, requisitoD-F1-02. El mismo texto del delta se integra en sistema, sin perder title/Purpose ni8 escenariosde base. Verificar sincronización más allá del movimiento de carpeta:16 requirements totales,9added/6modified y0 changes activos. Snapshots previos/finales permiten contrastar. No atribuir a init inferencia de código ni a archive validación funcional por sí solo.
- Conclusión: Fragmento del sistema tras sincronización y archivo, no sólo del delta.
- Pregunta: ¿Por qué conservar tanto la spec vigente como el delta histórico que produjo este comportamiento?
- Estado del ejemplo: Documento vigente real · después de archivo
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `os-21a`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## os-22 · Recuperar el recorrido

- Propósito: Restaurar esta copia sin alterar la base ni el otro recorrido.
- Explicación: PD-06 recuperación: elegir previo para conducir pasos y final para mostrar resultados guardados. Paquetes excluyen SQLite/env/caches/secretos; raízopenspec/. Extraer en carpeta nueva, uv sync --locked, migrate, seed_demo, check y test desde copia; confirmar8012/sdd-openspec y su volumen. El origen de ambos es base-v1 SHA d01f06…; final419330… contiene archivo y código propio. Consultar README y manifiestos antes de comandos; no sobrescribir ejercicios anteriores. Si el agente no está disponible, documentos/capturas locales permiten continuar; volver os22.
- Conclusión: Restaurar esta copia sin alterar la base ni el otro recorrido.
- Pregunta: ¿Qué carpeta, base de datos, puerto y proyecto Compose estamos recuperando?
- Estado del ejemplo: Recorrido real completo · CLI y Codex verificados
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `os-22`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## os-23 · Problemas de preparación y revisión

- Propósito: Dos clases de problema requieren respuestas diferentes.
- Explicación: Dos problemas reales distintos. Entorno: puertos8001/2/4/5/6 ya usados por ejemplos anteriores; se eligió8012 sin modificar proyectos previos. Artefactos: status/validate estructural no detectan cobertura temporal omitida; revisión agregó task5.4 y diseño§8, luego test real pasó. Además primer apply agotó cuota antes de código; el usuario pidió continuar y reintento completó, logs de ambos preservados. No afirmar fracaso externo permanente ni simular revisión humana. Abrir README/revision.md y comparar os17/19.
- Conclusión: Dos clases de problema requieren respuestas diferentes.
- Pregunta: ¿Qué problema exige corregir entorno y cuál exige revisar artefactos?
- Estado del ejemplo: Recorrido real completo · CLI y Codex verificados
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `os-23`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.


## os-24 · Referencia del recorrido

- Propósito: El mismo F1, con artefactos propios de OpenSpec.
- Explicación: Recapitulación del recorrido real: initCLI, propose/apply por skill CodexCLI, revisión de artefactos por agente/coordinador,56 tests local/Docker+16 observacionesUIcadauno, archivoCLI nativo. Skills disponibles y registro de ejecución son cosas diferentes; el README conserva método exacto y recuperación. F2 queda conceptual. Volver fundamentos o abrir SpecKit para comparar mismos criterios y formatos distintos.
- Conclusión: El mismo F1, con artefactos propios de OpenSpec.
- Pregunta: ¿Qué documento permite reconstruir el recorrido si el agente no está disponible?
- Estado del ejemplo: Recorrido ejecutado · archivo CLI coordinador
- Puente y recuperación: abrir documento enlazado en otra pestaña; volver a `os-24`. En puntos PD, usar checkpoint y evidencia guardada si la ejecución en vivo no está disponible.

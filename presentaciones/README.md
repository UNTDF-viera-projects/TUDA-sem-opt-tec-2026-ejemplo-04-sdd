# Presentaciones SDD · UNTDF 2026

[Índice](index.html) · [Fundamentos](fundamentos.html) · [OpenSpec](openspec.html) · [Spec Kit](spec-kit.html)

La entrega contiene 50 diapositivas de fundamentos, 27 de OpenSpec y 28 de Spec Kit, con notas docentes para cada ID. Los desdoblamientos conservan los IDs del storyboard y permiten proyectar documentos sin reducir la letra. F2 es una extensión conceptual, sin implementación.

## Apertura y navegación

Abrir `index.html` en un navegador de escritorio. El paquete funciona directamente con `file://`, sin fetch, CDN, imports ni fuentes remotas.

Alternativa desde `sdd/`:

```sh
python3 -m http.server 8090
```

Abrir `http://localhost:8090/presentaciones/`. Servir la carpeta sdd completa conserva los enlaces a documentos y recursos docentes.

Flechas, Page Up/Page Down y Espacio recorren diapositivas y fragmentos. Home/End van a los extremos. Los controles enfocados conservan su comportamiento normal. Secciones abre el índice; Escape lo cierra. Pantalla completa requiere una acción del usuario. La URL guarda el ID y fragmento: `fundamentos.html#sdd-22/1`.

Notas abre el guion del ID actual. Los documentos y demos se abren en otra pestaña; volver conserva la posición. Las notas también están en Markdown en `notas/`.

## Clase y fuentes

Consultar [secuencia docente](../material-docente/secuencia-clase.md) antes de exponer. Los puntos PD-01…07 incluyen estado inicial, acción, resultado y recuperación en las notas. Base del alumno:8000; solución docente F1:8011; OpenSpec:8012; Spec Kit:8013. Cada copia tiene SQLite y proyecto Compose independientes; leer sus README antes de cargar o restablecer datos.

Ambas herramientas partieron realmente de `base-v1.tar.gz` (21 pruebas). La base del alumno final es v2 (22 pruebas) tras corregir el reloj de inscripción bajo IMMEDIATE; la procedencia histórica se conserva. Resultados finales: F1 37 pruebas, OpenSpec 56, Spec Kit 39, cada suite ejecutada localmente y con Docker. No se compara calidad por cantidad de tests: los criterios F1 comunes definen la aceptación.

Las entradas resumidas llevan rótulo y enlace al registro completo usado. Los fragmentos de spec/plan/tasks son reales y comentados; los [20 cotejos de fuentes](verificacion/fragmentos.md) distinguen selección de texto, salidas y celdas reorganizadas. OpenSpec archive fue ejecutado por el coordinador con CLI nativa; las skills disponibles de la integración se distinguen de las invocaciones realmente ejecutadas.

## Verificación y mantenimiento

[Registro visual](verificacion/revision-visual.md), [cobertura](verificacion/cobertura.md), [entorno](verificacion/entorno.md), capturas completas en `verificacion/capturas/` y mosaicos en `verificacion/mosaicos/`.

424 estados capturados: todas las diapositivas y el fragmento progresivo de sdd-22, en1280×720,1920×1080,1440×900 y1280×640. La auditoría auxiliar no detectó desbordes; se inspeccionaron las capturas. QA independiente final:186 comprobaciones de navegación,306 enlaces locales y11 recursos, todos correctos por HTTP/file y sin errores JavaScript.

La consulta de los decks, notas, documentos y resultados guardados no requiere Internet. Preparar herramientas o ejecutar un modelo requiere el entorno y acceso correspondientes; las guías registran las versiones usadas y los resultados previos. No quedan verificaciones pendientes de esta entrega.

Para editar, modificar `assets/content.json` y regenerar con `python3 presentaciones/assets/build.py` desde sdd. No hace falta ejecutar el generador para exponer. Diagramas editables en HTML/CSS; [inventario](assets/diagrams/README.md). API auxiliar: `deck.states()`, `deck.set(id,fragment)` y `deck.audit()`. La inspección visual sigue siendo necesaria tras cambios.

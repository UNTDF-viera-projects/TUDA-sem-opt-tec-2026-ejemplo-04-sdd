# Entorno de revisión de presentaciones

2026-10-01, macOS arm64. Playwright bundled con Chrome Headless Shell 152.0.7977.42 para capturas/auditoría; QA independiente del agente Demo en Google Chrome 154.0.8037.93.

Áreas útiles exactas:1280×720,1920×1080,1440×900 y1280×640. Movimiento reducido activado en captura integral; navegación también ensayada sin esa preferencia.

HTML/CSS/JavaScript local. A1280: cuerpo24px, código20px, título40px y secundarios16px; a1920 se amplían coherentemente. A640 de alto se reduce espaciado, manteniendo tipografía esencial. No hay descargas necesarias para consultar el paquete ya preparado.

`audit-final.json` registra424estados; `funcional-file.json` registra prueba propia. QA independiente HTTP/file: [navegacion-presentaciones-final.md](../../material-docente/cancelacion/evidencia/navegacion-presentaciones-final.md),186/186checks,306/306links,11/11recursos y0errores JS. Revisión independiente adicional: [funcional-independiente.json](../../revision/funcional-independiente.json),19/19checks con espera de fullscreen.

Herramientas:OpenSpec1.14.0,Node24.21.0,CodexCLI0.159.2; SpecKit1.0.14.dev0 commit838f1184d1b2ed254a99e8b818dbc23aa80a7f1f. Aplicación:Django5.2.17,Python3.12.14,uv0.12.19,Docker29.4.0/Compose5.1.2. Logs y métodos reales en [recorridos](../../material-docente/recorridos/). Sus resultados no se deducen de la auditoría HTML.

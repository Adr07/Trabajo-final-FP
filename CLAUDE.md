# Reglas del proyecto

## Mantener la documentación sincronizada

Este proyecto tiene una memoria de documentación en `docs/memoria_proyecto.html` (fuente) y
`docs/memoria_proyecto.pdf` (entregable generado a partir del HTML).

**Regla:** cada vez que se haga una modificación relevante al proyecto principal (app Android,
agente Python, addon de Odoo) — nueva funcionalidad, cambio de arquitectura, problema
encontrado y resuelto, cambio de herramientas/tecnologías, etc. — hay que actualizar la sección
correspondiente de `docs/memoria_proyecto.html` y regenerar el PDF.

Para regenerar el PDF tras editar el HTML:

```powershell
$html = (Resolve-Path "docs\memoria_proyecto.html").Path
& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless --disable-gpu --no-pdf-header-footer --print-to-pdf="docs\memoria_proyecto.pdf" "file:///$($html -replace '\\','/')"
```

No hace falta preguntar antes de aplicar esta actualización — es una tarea rutinaria de
mantenimiento de la documentación, a realizar como parte de cualquier cambio significativo.

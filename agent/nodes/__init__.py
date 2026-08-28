"""
Paquete de nodos del agente.

Cada archivo de este paquete es un "nodo" independiente, en el mismo sentido
que un nodo de n8n: una unidad con una única responsabilidad, una entrada y
una salida bien definidas, que se conecta con otros nodos desde
`agent/workflow.py` (el "canvas" que dibuja las conexiones entre nodos).

Ningún nodo debe saltarse esta separación (p. ej. una tool no debe hablar con
Odoo directamente; siempre pasa por `odoo_connector`). Ver el diagrama del
workflow y `agent/README.md` para el mapa completo.
"""

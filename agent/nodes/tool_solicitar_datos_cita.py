"""
Nodo: Tool — solicitar_datos_cita

No es una tool de datos: no toca odoo_connector ni current_partner. Su único
propósito es servir de SEÑAL ESTRUCTURAL para workflow.py — cuando el LLM la
llama, `workflow.py` lo detecta inspeccionando qué tools se ejecutaron en el
turno (ver `ToolCallItem` del SDK) y se lo indica a la app por el campo
`requires_form` de la respuesta HTTP, para que muestre un formulario en vez
de que el LLM tenga que redactar en texto libre qué datos faltan (redacción
que no sería fiable de detectar del lado de la app).

Conecta hacia: nada (no llama a Odoo) ← agent_core (la registra como tool) →
workflow.py (detecta si se llamó, vía result.new_items).
"""

from agents.decorators import tool


@tool
def solicitar_datos_cita() -> str:
    """
    Llama a esta tool cuando necesites que el usuario complete motivo, fecha
    y hora de inicio, y duración para agendar_cita, en vez de pedírselos en
    texto libre — la app le mostrará un formulario con esos campos. Después
    de llamarla, responde con una frase muy breve (no repitas tú los campos,
    el formulario ya los muestra).
    """
    return "Se le mostrará al usuario un formulario para completar los datos de la reserva."

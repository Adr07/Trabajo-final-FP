"""
Nodo: Tool — consultar_citas

Tool de lectura expuesta al LLM. No contiene lógica de acceso a Odoo: delega
siempre en `odoo_connector`.

Ya no acepta un cliente por parámetro: siempre consulta las reservas del
cliente autenticado (current_partner). Busca por el nombre del cliente
dentro del texto del evento (ver nota de diseño en `tool_agendar_cita.py`
sobre por qué no se usa `partner_ids`).

Conecta hacia: odoo_connector, current_partner (entrada) ← agent_core (salida).
"""

from agents.decorators import tool

from agent.nodes import current_partner, odoo_connector


@tool
def consultar_citas() -> str:
    """Consulta las reservas/citas agendadas del cliente autenticado en Odoo (calendar.event)."""
    partner_id = current_partner.get()
    clientes = odoo_connector.search_read("res.partner", [("id", "=", partner_id)], ["name"])
    nombre = clientes[0]["name"] if clientes else "tu cuenta"

    citas = odoo_connector.search_read(
        "calendar.event",
        [("description", "ilike", f"(ID {partner_id})")],
        ["id", "name", "start", "stop"],
    )

    if not citas:
        return f"'{nombre}' no tiene ninguna reserva/cita agendada."

    detalle = "; ".join(f"{c['name']} (ID {c['id']}, {c['start']} a {c['stop']})" for c in citas)
    return f"Tus reservas: {detalle}."

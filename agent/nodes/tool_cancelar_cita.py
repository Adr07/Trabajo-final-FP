"""
Nodo: Tool — cancelar_cita

Tool de escritura (destructiva) expuesta al LLM. No contiene lógica de
acceso a Odoo: delega siempre en `odoo_connector`.

La búsqueda de la cita ya viene acotada al cliente autenticado (filtro en el
propio dominio, no una verificación posterior) — así ni siquiera aparece en
el listado de "varias coincidencias" una cita de otro cliente.

Conecta hacia: odoo_connector, current_partner, cita_permissions (entrada) ←
agent_core (salida).
"""

from agents.decorators import tool

from agent.nodes import cita_permissions, current_partner, odoo_connector


@tool
def cancelar_cita(cita: str) -> str:
    """
    Cancela (elimina) una reserva/cita del cliente autenticado en Odoo
    (calendar.event). Es una acción destructiva e irreversible — el agente
    debe confirmar con el usuario antes de llamar a esta tool.

    Args:
        cita: ID de Odoo de la cita, o texto que coincida con su motivo.
    """
    partner_id = current_partner.get()
    citas = odoo_connector.find_records(
        "calendar.event",
        cita,
        ["id", "name", "start"],
        extra_domain=[("description", "ilike", f"(ID {partner_id})")],
    )

    if not citas:
        return f"No encontré ninguna reserva/cita tuya que coincida con '{cita}'."
    if len(citas) > 1:
        opciones = "; ".join(f"{c['name']} (ID {c['id']}, {c['start']})" for c in citas)
        return f"Hay varias reservas que coinciden con '{cita}': {opciones}. ¿Cuál de ellas quieres cancelar?"

    evento = citas[0]

    try:
        cita_permissions.check("cancelar", partner_id)
    except cita_permissions.PermissionDenied as exc:
        return str(exc)

    odoo_connector.unlink_record("calendar.event", evento["id"])
    return f"Reserva '{evento['name']}' (ID {evento['id']}) cancelada."

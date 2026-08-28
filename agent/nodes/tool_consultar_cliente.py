"""
Nodo: Tool — consultar_cliente

Tool de lectura expuesta al LLM. No contiene lógica de acceso a Odoo: delega
siempre en `odoo_connector`.

Ya no acepta un identificador de cliente: siempre devuelve los datos del
cliente autenticado (current_partner), nunca los de un nombre que venga en
el mensaje — así ningún usuario puede pedir los datos de otro.

Conecta hacia: odoo_connector, current_partner (entrada) ← agent_core (salida).
"""

from agents.decorators import tool

from agent.nodes import current_partner, odoo_connector

_FIELDS = ["name", "email", "phone", "vat", "city"]


def _format(cliente: dict) -> str:
    partes = [f"Cliente: {cliente['name']} (ID {cliente['id']})"]
    if cliente.get("email"):
        partes.append(f"Email: {cliente['email']}")
    if cliente.get("phone"):
        partes.append(f"Teléfono: {cliente['phone']}")
    if cliente.get("vat"):
        partes.append(f"NIF/CIF: {cliente['vat']}")
    if cliente.get("city"):
        partes.append(f"Ciudad: {cliente['city']}")
    return " · ".join(partes)


@tool
def consultar_cliente() -> str:
    """Consulta los datos del cliente autenticado en Odoo (res.partner)."""
    registros = odoo_connector.search_read(
        "res.partner", [("id", "=", current_partner.get())], _FIELDS
    )
    if not registros:
        return "No pude encontrar tus datos de cliente en Odoo."
    return _format(registros[0])

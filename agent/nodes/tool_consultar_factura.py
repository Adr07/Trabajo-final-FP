"""
Nodo: Tool — consultar_factura

Tool de lectura expuesta al LLM. No contiene lógica de acceso a Odoo: delega
siempre en `odoo_connector`.

Conecta hacia: odoo_connector (entrada) ← agent_core (salida).
"""

from agents.decorators import tool

from agent.nodes import current_partner, odoo_connector

_ESTADO_PAGO = {
    "not_paid": "sin pagar",
    "in_payment": "en proceso de pago",
    "paid": "pagada",
    "partial": "pagada parcialmente",
    "reversed": "revertida",
}

_FIELDS = ["name", "partner_id", "amount_total", "payment_state", "invoice_date"]
_MOVE_TYPES = [("move_type", "in", ["out_invoice", "in_invoice"])]


def _format(factura: dict) -> str:
    cliente = factura["partner_id"][1] if factura.get("partner_id") else "sin cliente asociado"
    estado = _ESTADO_PAGO.get(factura.get("payment_state"), factura.get("payment_state", "desconocido"))
    fecha = factura.get("invoice_date") or "sin fecha"
    return (
        f"Factura {factura.get('name')} (ID {factura['id']}): cliente {cliente}, "
        f"importe total {factura.get('amount_total', 0):.2f}, estado de pago: {estado}, fecha: {fecha}."
    )


@tool
def consultar_factura(factura: str) -> str:
    """
    Consulta una factura del cliente autenticado en Odoo (account.move). Solo
    encuentra facturas de ese cliente — nunca las de otro, aunque coincida el
    número.

    Args:
        factura: ID de Odoo de la factura, o su número (p. ej. "INV/2026/00003").
            Para ver TODAS las facturas pendientes, usa consultar_facturas_pendientes.
    """
    registros = odoo_connector.find_records(
        "account.move",
        factura,
        _FIELDS,
        extra_domain=_MOVE_TYPES + [("partner_id", "=", current_partner.get())],
    )

    if not registros:
        return f"No encontré ninguna factura que coincida con '{factura}' en Odoo."

    if len(registros) > 1:
        opciones = "; ".join(f"{r.get('name')} (ID {r['id']})" for r in registros)
        return f"Hay varias facturas que coinciden con '{factura}': {opciones}. ¿Cuál de ellas?"

    return _format(registros[0])

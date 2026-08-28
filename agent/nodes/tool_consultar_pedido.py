"""
Nodo: Tool — consultar_pedido

Tool de lectura expuesta al LLM. No contiene lógica de acceso a Odoo: delega
siempre en `odoo_connector`.

Conecta hacia: odoo_connector (entrada) ← agent_core (salida).
"""

from agents.decorators import tool

from agent.nodes import current_partner, odoo_connector

_ESTADO = {
    "draft": "presupuesto",
    "sent": "presupuesto enviado",
    "sale": "confirmado",
    "done": "bloqueado",
    "cancel": "cancelado",
}

_FIELDS = ["name", "partner_id", "amount_total", "state", "date_order"]


def _format(pedido: dict) -> str:
    cliente = pedido["partner_id"][1] if pedido.get("partner_id") else "sin cliente asociado"
    estado = _ESTADO.get(pedido.get("state"), pedido.get("state", "desconocido"))
    return (
        f"Pedido {pedido.get('name')} (ID {pedido['id']}): cliente {cliente}, "
        f"importe total {pedido.get('amount_total', 0):.2f}, estado: {estado}."
    )


@tool
def consultar_pedido(pedido: str) -> str:
    """
    Consulta un pedido de venta del cliente autenticado en Odoo (sale.order).
    Solo encuentra pedidos de ese cliente — nunca los de otro, aunque
    coincida la referencia.

    Args:
        pedido: ID de Odoo del pedido, o su referencia (p. ej. "S00024").
    """
    registros = odoo_connector.find_records(
        "sale.order", pedido, _FIELDS, extra_domain=[("partner_id", "=", current_partner.get())]
    )

    if not registros:
        return f"No encontré ningún pedido que coincida con '{pedido}' en Odoo."

    if len(registros) > 1:
        opciones = "; ".join(f"{r.get('name')} (ID {r['id']})" for r in registros)
        return f"Hay varios pedidos que coinciden con '{pedido}': {opciones}. ¿Cuál de ellos?"

    return _format(registros[0])

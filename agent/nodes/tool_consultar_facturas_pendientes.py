"""
Nodo: Tool — consultar_facturas_pendientes

Tool de lectura expuesta al LLM. No contiene lógica de acceso a Odoo: delega
siempre en `odoo_connector`.

Ya no acepta un cliente por parámetro: siempre consulta las facturas
pendientes del cliente autenticado (current_partner).

Conecta hacia: odoo_connector, current_partner (entrada) ← agent_core (salida).
"""

from agents.decorators import tool

from agent.nodes import current_partner, odoo_connector


@tool
def consultar_facturas_pendientes() -> str:
    """
    Consulta las facturas pendientes de pago del cliente autenticado en Odoo
    (account.move con payment_state distinto de "paid").
    """
    partner_id = current_partner.get()
    cliente = odoo_connector.search_read("res.partner", [("id", "=", partner_id)], ["name"])
    nombre = cliente[0]["name"] if cliente else "tu cuenta"

    registros = odoo_connector.search_read(
        "account.move",
        [
            ("partner_id", "=", partner_id),
            ("move_type", "=", "out_invoice"),
            ("payment_state", "not in", ["paid", "reversed"]),
            ("state", "=", "posted"),
        ],
        ["name", "amount_residual", "invoice_date_due"],
    )
    if not registros:
        return f"{nombre} no tiene facturas pendientes de pago en Odoo."

    total = sum(r.get("amount_residual", 0) for r in registros)
    detalle = "; ".join(
        f"{r.get('name')} (debe {r.get('amount_residual', 0):.2f}, vence {r.get('invoice_date_due') or 'sin fecha'})"
        for r in registros
    )
    return f"{nombre} debe {total:.2f} en {len(registros)} factura(s) pendiente(s): {detalle}."

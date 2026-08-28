"""
Nodo: Tool — consultar_stock

Tool de lectura expuesta al LLM. No contiene lógica de acceso a Odoo: delega
siempre en `odoo_connector`.

Conecta hacia: odoo_connector (entrada) ← agent_core (salida).
"""

from agents.decorators import tool

from agent.nodes import odoo_connector


@tool
def consultar_stock(producto: str) -> str:
    """
    Consulta el stock disponible de un producto en Odoo (stock.quant).
    Busca sobre la variante (product.product), no sobre la plantilla.

    Args:
        producto: ID de Odoo de la variante del producto, o su nombre (o
            parte de él, p. ej. "silla" o "Whiteboard Pen").
    """
    variantes = odoo_connector.find_records("product.product", producto, ["name"])

    if not variantes:
        return f"No encontré ningún producto que coincida con '{producto}' en Odoo."

    if len(variantes) > 1:
        opciones = "; ".join(f"{v['name']} (ID {v['id']})" for v in variantes)
        return f"Hay varios productos que coinciden con '{producto}': {opciones}. ¿Cuál de ellos?"

    variante = variantes[0]
    registros = odoo_connector.search_read(
        "stock.quant",
        [("product_id", "=", variante["id"])],
        ["quantity", "reserved_quantity"],
    )
    if not registros:
        return f"No encontré movimientos de stock para '{variante['name']}' (ID {variante['id']}) en Odoo."

    total = sum(r.get("quantity", 0) for r in registros)
    reservado = sum(r.get("reserved_quantity", 0) for r in registros)
    disponible = total - reservado
    return (
        f"Stock de '{variante['name']}' (ID {variante['id']}): {total:g} unidades en total, "
        f"{reservado:g} reservadas, {disponible:g} disponibles."
    )

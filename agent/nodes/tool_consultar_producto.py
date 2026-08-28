"""
Nodo: Tool — consultar_producto

Tool de lectura expuesta al LLM. No contiene lógica de acceso a Odoo: delega
siempre en `odoo_connector`.

Conecta hacia: odoo_connector (entrada) ← agent_core (salida).
"""

from agents.decorators import tool

from agent.nodes import odoo_connector

_FIELDS = ["name", "default_code", "list_price", "sale_ok"]


def _format(producto: dict) -> str:
    referencia = f" (ref. {producto['default_code']})" if producto.get("default_code") else ""
    disponible = "a la venta" if producto.get("sale_ok") else "no está a la venta actualmente"
    return (
        f"Producto: {producto['name']}{referencia} (ID {producto['id']}), "
        f"precio {producto.get('list_price', 0):.2f}, {disponible}."
    )


@tool
def consultar_producto(producto: str) -> str:
    """
    Consulta los datos de un producto en Odoo (product.template).

    Args:
        producto: ID de Odoo del producto, o su nombre (o parte de él,
            p. ej. "silla" o "Acoustic Bloc").
    """
    registros = odoo_connector.find_records("product.template", producto, _FIELDS)

    if not registros:
        return f"No encontré ningún producto que coincida con '{producto}' en Odoo."

    if len(registros) > 1:
        opciones = "; ".join(f"{r['name']} (ID {r['id']})" for r in registros)
        return f"Hay varios productos que coinciden con '{producto}': {opciones}. ¿Cuál de ellos?"

    return _format(registros[0])

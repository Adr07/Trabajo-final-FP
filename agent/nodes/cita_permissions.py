"""
Nodo: Cita Permissions

Verifica, antes de que una tool de escritura actúe, si el admin de Odoo le
ha bloqueado esa acción concreta al cliente en cuestión. Los permisos viven
en campos de `res.partner` (`assistant_can_agendar_cita`,
`assistant_can_modificar_cita`, `assistant_can_cancelar_cita`) gestionables
desde la pestaña "Agente IA" del contacto en Odoo — ver
`odoo/addons/assistant_agent/models/res_partner.py`.

Nunca decide el permiso por su cuenta: siempre lee el campo real desde Odoo
justo antes de actuar (nunca lo cachea ni lo asume).

Nota: la verificación de "esta cita es tuya" ya NO vive aquí — vive en el
propio dominio de búsqueda de tool_modificar_cita.py/tool_cancelar_cita.py
(filtran por el ID del cliente autenticado antes de traer ningún resultado,
para no listar ni de refilón las citas de otro cliente).

Conecta hacia: odoo_connector (entrada) ← tool_agendar_cita,
tool_modificar_cita, tool_cancelar_cita (salida).
"""

from agent.nodes import odoo_connector

_PERMISSION_FIELD = {
    "agendar": "assistant_can_agendar_cita",
    "modificar": "assistant_can_modificar_cita",
    "cancelar": "assistant_can_cancelar_cita",
}


class PermissionDenied(Exception):
    """El admin de Odoo le ha bloqueado esta acción a este cliente."""


def check(accion: str, partner_id: int) -> None:
    """
    Comprueba si el cliente `partner_id` tiene permitida la `accion`
    ("agendar", "modificar" o "cancelar").

    Raises:
        PermissionDenied: si el admin desmarcó la casilla correspondiente
            para este cliente en Odoo.
    """
    campo = _PERMISSION_FIELD[accion]
    registros = odoo_connector.search_read("res.partner", [("id", "=", partner_id)], [campo, "name"])
    if not registros:
        # El cliente ya no existe; deja que la tool que llamó lo reporte a su manera.
        return
    if not registros[0].get(campo, True):
        raise PermissionDenied(
            f"El administrador ha bloqueado que el agente pueda {accion} citas en nombre de "
            f"'{registros[0]['name']}'. Pídele que revise sus permisos en Odoo."
        )

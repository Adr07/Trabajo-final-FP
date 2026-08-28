from odoo import fields, models


class ResPartner(models.Model):
    """
    Extiende res.partner con los permisos que el admin de Odoo usa para
    controlar, cliente por cliente, qué acciones de escritura puede ejecutar
    el agente de IA en su nombre. Por defecto todo permitido — el admin
    desmarca la casilla del cliente concreto al que quiera restringir una
    acción.

    El agente (agent/nodes/cita_permissions.py) lee estos campos antes de
    ejecutar cualquier tool de escritura; nunca los escribe.
    """

    _inherit = "res.partner"

    assistant_can_agendar_cita = fields.Boolean(
        string="Puede agendar citas",
        default=True,
        help="Si está desmarcado, el agente de IA rechazará agendar nuevas reservas/citas para este cliente.",
    )
    assistant_can_modificar_cita = fields.Boolean(
        string="Puede modificar citas",
        default=True,
        help="Si está desmarcado, el agente de IA rechazará modificar reservas/citas de este cliente.",
    )
    assistant_can_cancelar_cita = fields.Boolean(
        string="Puede cancelar citas",
        default=True,
        help="Si está desmarcado, el agente de IA rechazará cancelar reservas/citas de este cliente.",
    )

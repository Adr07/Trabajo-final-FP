from odoo import fields, models


class AssistantConsulta(models.Model):
    """
    Registro de una conversación cerrada del chat de soporte — se crea una
    vez por cada "Finalizar consulta" que hace el cliente en la app, nunca
    mientras la conversación sigue abierta. El admin la revisa aquí, en
    Odoo; el bot de IA solo puede crearlas y leerlas (ver
    security/ir.model.access.csv), nunca modificarlas ni borrarlas — en
    particular, "state" solo lo cambia un usuario interno/admin desde Odoo,
    nunca el bot ni el cliente desde la app (que solo puede consultarlo).
    """

    _name = "assistant.consulta"
    _description = "Consulta de cliente (conversación cerrada por el chat)"
    _order = "stop desc"

    partner_id = fields.Many2one("res.partner", required=True, string="Cliente")
    start = fields.Datetime(required=True, string="Inicio")
    stop = fields.Datetime(required=True, string="Fin")
    transcript = fields.Text(string="Transcripción")
    state = fields.Selection(
        [("pendiente", "Pendiente"), ("resuelta", "Resuelta")],
        required=True, default="pendiente", string="Estado",
    )

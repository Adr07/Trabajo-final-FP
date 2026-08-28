"""
Nodo: Tool — agendar_cita

Primera tool de escritura del sistema. Reserva un turno/cita para el cliente
autenticado en Odoo (calendar.event). No contiene lógica de acceso a Odoo:
delega siempre en `odoo_connector`.

Ya no acepta un cliente por parámetro: siempre agenda a nombre del cliente
autenticado (current_partner) — así ningún usuario puede agendar (ni
consultar) a nombre de otro por más que lo escriba en el mensaje.

Nota de diseño: el evento NO usa el campo relacional `partner_ids` de
calendar.event — ese campo activa el sistema de "seguidores"/asistentes de
Odoo (mail.followers), que está restringido a nivel de campo a usuarios
internos y no es compatible con un usuario de integración de permisos
acotados. En su lugar, el cliente queda identificado en el propio texto del
evento (nombre y descripción), que es justo lo que `consultar_citas` busca
después.

Conecta hacia: odoo_connector, current_partner (entrada) ← agent_core (salida).
"""

from datetime import datetime, timedelta

from agents.decorators import tool

from agent.nodes import cita_permissions, current_partner, odoo_connector

_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


@tool
def agendar_cita(motivo: str, inicio: str, duracion_minutos: int = 60, notas: str | None = None) -> str:
    """
    Agenda una reserva/cita para el cliente autenticado en Odoo (calendar.event).

    Args:
        motivo: motivo breve de la reserva (p. ej. "Mesa para 4", "Recogida de pedido").
        inicio: fecha y hora de inicio en formato "YYYY-MM-DD HH:MM:SS".
        duracion_minutos: duración de la reserva en minutos (60 por defecto).
        notas: notas adicionales opcionales.
    """
    partner_id = current_partner.get()

    try:
        cita_permissions.check("agendar", partner_id)
    except cita_permissions.PermissionDenied as exc:
        return str(exc)

    clientes = odoo_connector.search_read("res.partner", [("id", "=", partner_id)], ["name"])
    nombre = clientes[0]["name"] if clientes else "tu cuenta"

    try:
        inicio_dt = datetime.strptime(inicio, _DATETIME_FORMAT)
    except ValueError:
        return "El formato de la fecha/hora de inicio no es válido. Usa 'YYYY-MM-DD HH:MM:SS'."

    fin_dt = inicio_dt + timedelta(minutes=duracion_minutos)

    descripcion = f"Cliente: {nombre} (ID {partner_id})"
    if notas:
        descripcion += f"\n{notas}"

    values = {
        "name": f"{motivo} — {nombre}",
        "start": inicio_dt.strftime(_DATETIME_FORMAT),
        "stop": fin_dt.strftime(_DATETIME_FORMAT),
        "description": descripcion,
    }

    event_id = odoo_connector.create_record("calendar.event", values)

    return (
        f"Reserva creada para {nombre}: '{motivo}' el {inicio_dt.strftime('%d/%m/%Y a las %H:%M')} "
        f"({duracion_minutos} min). ID de la cita: {event_id}."
    )

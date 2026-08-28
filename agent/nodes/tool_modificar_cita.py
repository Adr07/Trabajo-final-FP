"""
Nodo: Tool — modificar_cita

Tool de escritura expuesta al LLM. No contiene lógica de acceso a Odoo:
delega siempre en `odoo_connector`.

La búsqueda de la cita ya viene acotada al cliente autenticado (filtro en el
propio dominio, no una verificación posterior) — así ni siquiera aparece en
el listado de "varias coincidencias" una cita de otro cliente.

Conecta hacia: odoo_connector, current_partner, cita_permissions (entrada) ←
agent_core (salida).
"""

from datetime import datetime, timedelta

from agents.decorators import tool

from agent.nodes import cita_permissions, current_partner, odoo_connector

_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


@tool
def modificar_cita(
    cita: str,
    nuevo_inicio: str | None = None,
    nueva_duracion_minutos: int | None = None,
    nuevo_motivo: str | None = None,
) -> str:
    """
    Modifica una reserva/cita del cliente autenticado en Odoo (calendar.event).
    Solo cambia los campos que se indiquen; el resto se deja como está.

    Args:
        cita: ID de Odoo de la cita, o texto que coincida con su motivo.
        nuevo_inicio: nueva fecha/hora de inicio en formato "YYYY-MM-DD HH:MM:SS", si se cambia.
        nueva_duracion_minutos: nueva duración en minutos, si se cambia (requiere nuevo_inicio si se usa sola).
        nuevo_motivo: nuevo motivo/nombre de la reserva, si se cambia.
    """
    partner_id = current_partner.get()
    citas = odoo_connector.find_records(
        "calendar.event",
        cita,
        ["id", "name", "start", "stop", "description"],
        extra_domain=[("description", "ilike", f"(ID {partner_id})")],
    )

    if not citas:
        return f"No encontré ninguna reserva/cita tuya que coincida con '{cita}'."
    if len(citas) > 1:
        opciones = "; ".join(f"{c['name']} (ID {c['id']}, {c['start']})" for c in citas)
        return f"Hay varias reservas que coinciden con '{cita}': {opciones}. ¿Cuál de ellas?"

    evento = citas[0]

    try:
        cita_permissions.check("modificar", partner_id)
    except cita_permissions.PermissionDenied as exc:
        return str(exc)

    values: dict = {}

    if nuevo_motivo:
        values["name"] = nuevo_motivo

    if nuevo_inicio:
        try:
            inicio_dt = datetime.strptime(nuevo_inicio, _DATETIME_FORMAT)
        except ValueError:
            return "El formato de la nueva fecha/hora no es válido. Usa 'YYYY-MM-DD HH:MM:SS'."
        values["start"] = inicio_dt.strftime(_DATETIME_FORMAT)
        if nueva_duracion_minutos:
            values["stop"] = (inicio_dt + timedelta(minutes=nueva_duracion_minutos)).strftime(_DATETIME_FORMAT)
    elif nueva_duracion_minutos:
        inicio_actual = datetime.strptime(evento["start"], _DATETIME_FORMAT)
        values["stop"] = (inicio_actual + timedelta(minutes=nueva_duracion_minutos)).strftime(_DATETIME_FORMAT)

    if not values:
        return "No indicaste ningún cambio (nueva fecha, duración o motivo)."

    odoo_connector.write_record("calendar.event", evento["id"], values)
    return f"Reserva '{evento['name']}' (ID {evento['id']}) actualizada."

"""
Nodo: Auth Login

Verifica email/contraseña de un cliente contra Odoo y, si es válido y
pertenece al grupo Portal (nunca a un usuario interno/admin), abre una
sesión en `auth_session.py`. No es una tool del LLM — por eso se llama
`auth_login.py` y no `tool_login.py`, para no confundirlo con los nodos
`tool_*` que sí decide invocar el agente.

Conecta hacia: odoo_connector (verifica credenciales y lee el res.users) y
auth_session (crea el token) ← main.py (lo llama desde /auth/login).
"""

from agent.nodes import auth_session, odoo_connector

_PORTAL_GROUP_XMLID = "base.group_portal"


class AuthError(Exception):
    """Credenciales inválidas, o el usuario no es un cliente Portal."""


def login(email: str, password: str) -> tuple[str, str]:
    """
    Autentica a un cliente contra Odoo.

    Returns:
        (token, nombre) si las credenciales son correctas y el usuario es
        Portal.

    Raises:
        AuthError: credenciales inválidas, o el usuario existe pero no es
            Portal (p. ej. un usuario interno/admin) — se rechaza también en
            ese caso, para que este login nunca sirva para entrar con una
            cuenta de administración.
    """
    uid = odoo_connector.authenticate_user(email, password)
    if uid is None:
        raise AuthError("Email o contraseña incorrectos.")

    registros = odoo_connector.search_read(
        "res.users", [("id", "=", uid)], ["name", "partner_id", "groups_id"]
    )
    if not registros:
        raise AuthError("No se pudo verificar la cuenta.")

    usuario = registros[0]
    modulo, nombre_xmlid = _PORTAL_GROUP_XMLID.split(".")
    datos_xmlid = odoo_connector.search_read(
        "ir.model.data",
        [("module", "=", modulo), ("name", "=", nombre_xmlid)],
        ["res_id"],
    )
    portal_group_id = datos_xmlid[0]["res_id"] if datos_xmlid else None
    if portal_group_id is None or portal_group_id not in usuario["groups_id"]:
        raise AuthError("Esta cuenta no es una cuenta de cliente. Contacta al administrador.")

    partner_id = usuario["partner_id"][0]
    token = auth_session.store.create(partner_id)
    return token, usuario["name"]

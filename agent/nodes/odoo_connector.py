"""
Nodo: Odoo Connector

Frontera de seguridad crítica del sistema: es el ÚNICO archivo del agente con
permiso para hablar con Odoo. Habla exclusivamente con la API externa que
Odoo ya expone (XML-RPC), autenticado con las credenciales del usuario de
integración creado por el módulo `odoo/addons/assistant_agent`.

Prohibido explícitamente:
- Conectarse directamente a PostgreSQL (ni con psycopg2 ni con ningún ORM
  ajeno a Odoo). Todo el acceso a datos pasa por la estructura interna de
  Odoo (sus modelos, sus reglas de acceso `ir.rule`/`ir.model.access`), nunca
  por SQL crudo.
- Que un nodo `tool_*` importe un cliente HTTP/XML-RPC propio: todos deben
  pasar por las funciones de este archivo.

Credenciales esperadas (ver `agent/config/settings.py` y `.env.example`):
    ODOO_URL       — URL base de la instancia Odoo (p. ej. http://localhost:8069)
    ODOO_DB        — nombre de la base de datos
    ODOO_USERNAME  — usuario de integración dedicado (creado por el módulo Odoo)
    ODOO_API_KEY   — API key o contraseña de ese usuario (nunca la de un humano)

El usuario de integración solo pertenece al grupo `group_agent_readonly` del
módulo `assistant_agent`. Ese grupo es de solo lectura salvo excepciones
explícitas y muy acotadas por modelo (hoy: `calendar.event`, para poder
agendar/modificar/cancelar reservas). Este conector solo puede hacer lo que
Odoo le deje hacer — las funciones de escritura de aquí abajo fallarán con
`OdooConnectionError` en cualquier modelo sin el permiso correspondiente.

Conecta hacia: cada nodo `tool_*` lo usa como única vía de acceso a Odoo.
"""

import xmlrpc.client

from agent.config.settings import load_settings


class OdooConnectionError(Exception):
    """No se pudo autenticar o conectar con la API externa de Odoo."""


_uid_cache: int | None = None


def _authenticate() -> tuple:
    """Autentica contra Odoo y cachea el uid para no repetir el login en cada llamada."""
    global _uid_cache
    settings = load_settings()
    common = xmlrpc.client.ServerProxy(f"{settings.odoo_url}/xmlrpc/2/common")

    if _uid_cache is None:
        try:
            uid = common.authenticate(settings.odoo_db, settings.odoo_username, settings.odoo_api_key, {})
        except (xmlrpc.client.Fault, ConnectionError, OSError) as exc:
            raise OdooConnectionError(f"No se pudo conectar con Odoo en {settings.odoo_url}: {exc}") from exc
        if not uid:
            raise OdooConnectionError(
                "Odoo rechazó las credenciales del usuario de integración "
                f"({settings.odoo_username!r}). Revisa ODOO_USERNAME/ODOO_API_KEY en .env."
            )
        _uid_cache = uid

    models = xmlrpc.client.ServerProxy(f"{settings.odoo_url}/xmlrpc/2/object")
    return settings, _uid_cache, models


def authenticate_user(login: str, password: str) -> int | None:
    """
    Autentica un login/contraseña arbitrarios contra Odoo (para el login real
    de un cliente, no para el usuario de integración). No toca `_uid_cache`
    — es un uid completamente aparte del que usa el resto de este conector.

    Returns:
        El uid de Odoo si las credenciales son correctas, o None si Odoo las
        rechaza.
    """
    settings = load_settings()
    common = xmlrpc.client.ServerProxy(f"{settings.odoo_url}/xmlrpc/2/common")
    try:
        uid = common.authenticate(settings.odoo_db, login, password, {})
    except (xmlrpc.client.Fault, ConnectionError, OSError) as exc:
        raise OdooConnectionError(f"No se pudo conectar con Odoo en {settings.odoo_url}: {exc}") from exc
    return uid or None


def search_read(
    model: str,
    domain: list,
    fields: list[str],
    limit: int | None = None,
) -> list[dict]:
    """
    Envoltorio sobre `search_read` de la API externa de Odoo (XML-RPC `execute_kw`).

    Args:
        model: modelo de Odoo a consultar (p. ej. "res.partner").
        domain: dominio de búsqueda en formato Odoo (lista de tuplas).
        fields: campos a devolver.
        limit: límite opcional de resultados.

    Returns:
        Lista de dicts, uno por registro encontrado. Lista vacía si no hay
        resultados — nunca se debe inventar un resultado.

    Raises:
        OdooConnectionError: si falla la autenticación o la llamada a Odoo
            (incluye el caso de permiso denegado: el usuario de integración
            no tiene acceso de lectura a ese modelo).
    """
    settings, uid, models = _authenticate()
    kwargs: dict = {"fields": fields}
    if limit:
        kwargs["limit"] = limit
    try:
        return models.execute_kw(
            settings.odoo_db, uid, settings.odoo_api_key, model, "search_read", [domain], kwargs
        )
    except xmlrpc.client.Fault as exc:
        raise OdooConnectionError(f"Odoo rechazó la consulta a '{model}': {exc.faultString}") from exc


def find_records(
    model: str,
    identifier: str,
    fields: list[str],
    search_field: str = "name",
    extra_domain: list | None = None,
    limit: int = 6,
) -> list[dict]:
    """
    Busca registros por un identificador flexible: si es un número, busca por
    ID exacto; si no, busca por coincidencia parcial (`ilike`) en
    `search_field`. Así las tools no obligan al usuario a conocer el ID de
    Odoo — pueden dar un nombre y esto resuelve el registro real (nunca
    "adivina": es una búsqueda real contra Odoo, con sus resultados reales).

    Args:
        model: modelo de Odoo a consultar.
        identifier: ID numérico (como texto) o texto a buscar.
        fields: campos a devolver.
        search_field: campo de texto contra el que buscar cuando `identifier`
            no es numérico (p. ej. "name").
        extra_domain: condiciones adicionales (AND) a aplicar siempre.
        limit: máximo de candidatos a devolver cuando la búsqueda por texto
            da varias coincidencias (para poder listarlas y desambiguar).

    Returns:
        Lista de dicts. Puede tener 0, 1 o varios elementos — quien llama
        decide qué hacer en cada caso (no encontrado / usar el único match /
        pedir al usuario que elija entre varios).
    """
    identifier = (identifier or "").strip()
    if identifier.isdigit():
        domain = [("id", "=", int(identifier))]
    else:
        domain = [(search_field, "ilike", identifier)]
    if extra_domain:
        domain = domain + extra_domain
    return search_read(model, domain, fields, limit=limit)


# Contexto que se pasa en toda escritura para que Odoo NO dispare su
# maquinaria de chatter/actividades (mail.thread) en estas operaciones
# automatizadas. Sin esto, incluso un `write()` que solo cambia un campo de
# texto intenta recomputar campos relacionados con `mail.activity`, y un
# usuario con permisos acotados (no "Usuario Interno") no puede leer eso.
_WRITE_CONTEXT = {
    "tracking_disable": True,
    "mail_create_nolog": True,
    "mail_create_nosubscribe": True,
    "mail_notrack": True,
}


def create_record(model: str, values: dict) -> int:
    """
    Crea un registro en Odoo. Solo funciona en los modelos donde el usuario
    de integración tenga `perm_create=1` en `ir.model.access.csv` — hoy en
    día únicamente `calendar.event` (ver módulo `assistant_agent`).

    Args:
        model: modelo de Odoo donde crear el registro.
        values: campos del nuevo registro.

    Returns:
        ID del registro creado.

    Raises:
        OdooConnectionError: si Odoo deniega el permiso o falla la llamada.
    """
    settings, uid, models = _authenticate()
    try:
        return models.execute_kw(
            settings.odoo_db, uid, settings.odoo_api_key, model, "create", [values], {"context": _WRITE_CONTEXT}
        )
    except xmlrpc.client.Fault as exc:
        raise OdooConnectionError(f"Odoo rechazó crear el registro en '{model}': {exc.faultString}") from exc


def write_record(model: str, record_id: int, values: dict) -> bool:
    """
    Modifica un registro existente en Odoo. Requiere `perm_write=1` para el
    usuario de integración en ese modelo.

    Args:
        model: modelo de Odoo.
        record_id: ID del registro a modificar.
        values: campos a actualizar.

    Raises:
        OdooConnectionError: si Odoo deniega el permiso o falla la llamada.
    """
    settings, uid, models = _authenticate()
    try:
        return models.execute_kw(
            settings.odoo_db, uid, settings.odoo_api_key, model, "write", [[record_id], values],
            {"context": _WRITE_CONTEXT},
        )
    except xmlrpc.client.Fault as exc:
        raise OdooConnectionError(f"Odoo rechazó modificar el registro {record_id} de '{model}': {exc.faultString}") from exc


def unlink_record(model: str, record_id: int) -> bool:
    """
    Elimina un registro en Odoo. Requiere `perm_unlink=1` para el usuario de
    integración en ese modelo.

    Args:
        model: modelo de Odoo.
        record_id: ID del registro a eliminar.

    Raises:
        OdooConnectionError: si Odoo deniega el permiso o falla la llamada.
    """
    settings, uid, models = _authenticate()
    try:
        return models.execute_kw(
            settings.odoo_db, uid, settings.odoo_api_key, model, "unlink", [[record_id]],
            {"context": _WRITE_CONTEXT},
        )
    except xmlrpc.client.Fault as exc:
        raise OdooConnectionError(f"Odoo rechazó eliminar el registro {record_id} de '{model}': {exc.faultString}") from exc

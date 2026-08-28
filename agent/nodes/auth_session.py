"""
Nodo: Auth Session

Guarda la relación token de sesión -> partner_id autenticado, después de un
login exitoso (ver `auth_login.py`). El `/chat` de main.py resuelve el token
que manda la app contra este almacén para saber quién pregunta, antes de
tocar ninguna tool.

Placeholder de MVP, mismo criterio que memory_session.py: dict en memoria de
proceso, se pierde al reiniciar el agente. Si esto pasa a producción real,
sustituir por un backend persistente (Redis, tabla en Postgres) sin cambiar
la forma en que main.py lo usa.

Conecta hacia: auth_login.py (crea el token) y main.py (lo resuelve en cada /chat).
"""

import secrets


class SessionStore:
    def __init__(self) -> None:
        self._tokens: dict[str, int] = {}

    def create(self, partner_id: int) -> str:
        token = secrets.token_urlsafe(32)
        self._tokens[token] = partner_id
        return token

    def resolve(self, token: str) -> int | None:
        return self._tokens.get(token)


store = SessionStore()

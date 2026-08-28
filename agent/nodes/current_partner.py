"""
Nodo: Current Partner

Guarda el partner_id del cliente autenticado para el request en curso, en un
`ContextVar` — no en un argumento de función. Esto es deliberado: si el
identificador del cliente fuera un parámetro normal de una tool (como
`cliente: str` antes de este cambio), el LLM podría llegar a pasarlo o
sobreescribirlo a partir de lo que diga el usuario en el mensaje. Un
ContextVar que solo `workflow.py` escribe (una vez, al principio del
request) y que las tools solo leen, no es algo que el LLM pueda ver ni tocar
de ninguna forma — la identidad queda fijada del lado del servidor.

Conecta hacia: workflow.py (lo fija al empezar cada request) y las tools
que necesitan saber "quién pregunta" (consultar_cliente, agendar_cita, etc.).
"""

import contextvars

_current_partner_id: contextvars.ContextVar[int | None] = contextvars.ContextVar(
    "current_partner_id", default=None
)


def set(partner_id: int) -> None:
    _current_partner_id.set(partner_id)


def get() -> int:
    partner_id = _current_partner_id.get()
    if partner_id is None:
        raise RuntimeError("No hay ningún cliente autenticado en este contexto.")
    return partner_id

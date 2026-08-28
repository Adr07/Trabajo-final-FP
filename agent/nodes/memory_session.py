"""
Nodo: Memory / Session

Mantiene el contexto de la conversación en curso (memoria de corto plazo, ver
la skill `python-ai-agent` → references/memory-and-persistence.md). No
implementa memoria de largo plazo ni memoria vectorial: eso solo se añade si
aparece una necesidad real, y entonces vía PostgreSQL, no aquí.

El OpenAI Agents SDK expone el historial de una conversación como la lista
que devuelve `result.to_input_list()`; este nodo solo guarda y recupera esa
lista por `conversation_id`, sin interpretarla.

Conecta hacia: agent_core (le entrega el historial) y recibe de workflow.py
el resultado para guardarlo tras cada turno.
"""


class SessionStore:
    """
    Almacén de historiales en memoria de proceso.

    Placeholder de MVP: se pierde al reiniciar el proceso. Cuando exista la
    Fase 4 del roadmap (PostgreSQL + sesiones), sustituir por un backend
    persistente sin cambiar la forma en que workflow.py lo usa.
    """

    def __init__(self) -> None:
        self._histories: dict[str, list] = {}

    def get_history(self, conversation_id: str) -> list | None:
        return self._histories.get(conversation_id)

    def set_history(self, conversation_id: str, items: list) -> None:
        self._histories[conversation_id] = items


store = SessionStore()

"""
Nodo: Output Response

Última parada del workflow: da forma a la respuesta final que se devuelve al
llamador (la API en `agent/main.py`). No decide contenido — solo formatea lo
que ya decidió agent_core.

Conecta hacia: recibe de workflow.py, entrega a agent/main.py (API).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentResponse:
    conversation_id: str
    response: str
    requires_form: str | None = None


def format_response(conversation_id: str, final_output: str, requires_form: str | None = None) -> AgentResponse:
    """Da forma final a la respuesta del agente antes de devolverla por la API."""
    texto = (final_output or "").strip()
    if not texto:
        texto = "No tengo una respuesta para eso."
    return AgentResponse(conversation_id=conversation_id, response=texto, requires_form=requires_form)

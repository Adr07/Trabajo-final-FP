"""
Nodo: Input Trigger

Equivalente al nodo "Webhook" / "Chat Trigger" de n8n: es la puerta de entrada
del workflow. No contiene lógica de negocio ni habla con el LLM ni con Odoo —
solo recibe la petición cruda (desde `agent/main.py`, vía FastAPI) y la
normaliza a la forma que el resto del workflow espera.

Conecta hacia: agent_core.
"""

from dataclasses import dataclass

MAX_MESSAGE_LENGTH = 2000


@dataclass(frozen=True)
class IncomingMessage:
    """Forma normalizada de una petición entrante al agente."""

    conversation_id: str
    message: str


def normalize(conversation_id: str, message: str) -> IncomingMessage:
    """
    Valida y normaliza la petición entrante.

    Args:
        conversation_id: identificador de la conversación (para memoria de sesión).
        message: texto del usuario.

    Raises:
        ValueError: si el mensaje está vacío o el conversation_id no es válido.
    """
    conversation_id = (conversation_id or "").strip()
    message = (message or "").strip()

    if not conversation_id:
        raise ValueError("conversation_id no puede estar vacío.")
    if not message:
        raise ValueError("El mensaje no puede estar vacío.")
    if len(message) > MAX_MESSAGE_LENGTH:
        raise ValueError(f"El mensaje supera el límite de {MAX_MESSAGE_LENGTH} caracteres.")

    return IncomingMessage(conversation_id=conversation_id, message=message)

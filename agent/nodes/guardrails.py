"""
Nodo: Guardrails

Frontera de validación de entrada del workflow. En este alcance (agente de
solo lectura) no hay operaciones de escritura que autorizar — eso se añadirá
aquí mismo el día que existan tools de escritura reales (ver skill
`python-ai-agent` → references/security-and-guardrails.md).

Lo que sí vive aquí en el MVP: rechazar entradas degeneradas (vacías,
desmesuradamente largas) antes de gastar una llamada al LLM. La validación
semántica de dominio ("esto no es una pregunta sobre Odoo") se deja para
cuando el propio agente la resuelva vía instructions + guardrails nativos del
SDK — no se aproxima aquí con listas de palabras clave, porque eso es
exactamente el anti-patrón que este proyecto evita.

Conecta hacia: se invoca desde workflow.py antes de llamar a agent_core.
"""


class InvalidInputError(Exception):
    """La entrada del usuario no es válida para procesar."""


def validate_input(message: str) -> None:
    """
    Guardrail de entrada: se ejecuta sobre el mensaje del usuario antes de
    pasarlo al agente.

    Raises:
        InvalidInputError: si el mensaje está vacío tras limpiar espacios.
    """
    if not message or not message.strip():
        raise InvalidInputError("El mensaje está vacío.")

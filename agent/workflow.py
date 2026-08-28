"""
Workflow — el "canvas" del agente.

Este archivo es el equivalente al JSON de un workflow de n8n: no implementa
lógica propia de negocio, solo declara en qué orden se conectan los nodos.
Cualquier cambio en el orden/las conexiones del pipeline se hace aquí, no
dentro de un nodo concreto.

Conexiones actuales:

    current_partner.set(partner_id) ── fija quién pregunta, antes que nada
         │
         ▼
    input_trigger
         │
         ▼
    guardrails
         │
         ▼
    memory_session ──(historial previo)──► agent_core
         │                                     │
         │                           tool_consultar_* (una por archivo)
         │                                     │
         │                              odoo_connector
         │                                     │
         │                          Odoo (API externa,
         │                           nunca DB directa)
         │                                     │
         └──────(guarda historial nuevo)───────┤
                                                ▼
                                         output_response
"""

from agents import Runner
from agents.items import ToolCallItem

from agent.nodes import agent_core, current_partner, guardrails, input_trigger, memory_session, output_response

_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        _agent = agent_core.build_agent()
    return _agent


def run(conversation_id: str, message: str, partner_id: int) -> output_response.AgentResponse:
    """
    Ejecuta el workflow completo para un turno de conversación.

    `partner_id` es el cliente autenticado que hace la pregunta (resuelto por
    main.py a partir del session_token) — se fija en el ContextVar de
    current_partner antes de tocar cualquier tool, para que "quién pregunta"
    quede decidido del lado del servidor y no sea algo que el LLM pueda leer
    ni cambiar.
    """
    current_partner.set(partner_id)

    incoming = input_trigger.normalize(conversation_id, message)
    guardrails.validate_input(incoming.message)

    historial = memory_session.store.get_history(incoming.conversation_id)
    if historial:
        agent_input = historial + [{"role": "user", "content": incoming.message}]
    else:
        agent_input = incoming.message

    result = Runner.run_sync(_get_agent(), agent_input)

    memory_session.store.set_history(incoming.conversation_id, result.to_input_list())

    # Señal estructural, no heurística de texto: si el LLM llamó a
    # solicitar_datos_cita este turno, la app debe mostrar el formulario en
    # vez del texto libre que haya escrito el LLM.
    requires_form = (
        "agendar_cita"
        if any(
            isinstance(item, ToolCallItem) and item.tool_name == "solicitar_datos_cita"
            for item in result.new_items
        )
        else None
    )

    return output_response.format_response(incoming.conversation_id, result.final_output, requires_form)

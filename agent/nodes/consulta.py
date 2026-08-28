"""
Nodo: Consulta

Cierra una consulta: arma la transcripción a partir del historial que ya
tiene memory_session para esa conversation_id, la guarda en Odoo
(assistant.consulta) y libera esa conversación de la memoria del proceso.

No es una tool del LLM — lo dispara main.py directamente desde
`/consulta/finalizar`, nunca el propio agente.

Conecta hacia: memory_session (lee el historial), odoo_connector (crea el
registro) ← main.py (lo llama al recibir la petición de finalizar).
"""

from datetime import datetime

from agent.nodes import memory_session, odoo_connector


def _extract_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        partes = []
        for parte in content:
            if isinstance(parte, dict):
                texto = parte.get("text") or parte.get("output_text")
                if texto:
                    partes.append(texto)
        return " ".join(partes)
    return ""


def build_transcript(history: list) -> str:
    """
    Arma una transcripción legible a partir del historial crudo del SDK.
    Ignora deliberadamente cualquier item que no sea un turno de usuario o
    asistente (tool calls, tool outputs, reasoning) — el admin solo necesita
    leer la conversación, no la mecánica interna de las tools.
    """
    lineas = []
    for item in history:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        if role not in ("user", "assistant"):
            continue
        texto = _extract_text(item.get("content"))
        if not texto:
            continue
        etiqueta = "Cliente" if role == "user" else "Asistente"
        lineas.append(f"{etiqueta}: {texto}")
    return "\n".join(lineas)


def finalizar(partner_id: int, conversation_id: str, started_at: str) -> None:
    """Cierra la consulta `conversation_id` del cliente `partner_id` y la guarda en Odoo."""
    historial = memory_session.store.get_history(conversation_id) or []
    transcript = build_transcript(historial)

    odoo_connector.create_record(
        "assistant.consulta",
        {
            "partner_id": partner_id,
            "start": started_at,
            "stop": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "transcript": transcript,
        },
    )

    memory_session.store.set_history(conversation_id, [])


def listar(partner_id: int) -> list[dict]:
    """Devuelve las consultas ya cerradas del cliente `partner_id`, más recientes primero."""
    return odoo_connector.search_read(
        "assistant.consulta",
        domain=[("partner_id", "=", partner_id)],
        fields=["start", "stop", "transcript", "state"],
    )

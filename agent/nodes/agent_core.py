"""
Nodo: Agent Core

El nodo "cerebro" del workflow — equivalente al nodo "AI Agent" de n8n. Es el
único lugar donde se construye el `Agent` del OpenAI Agents SDK y se registran
las tools. Decide, mediante tool calling estructurado, qué nodo `tool_*`
ejecutar — nunca por coincidencia de palabras clave.

No contiene lógica de acceso a Odoo ni a la base de datos: solo orquesta.

Conecta hacia:
    entrada:  workflow.py le pasa el mensaje/historial
    usa:      tool_consultar_cliente, tool_consultar_factura,
              tool_consultar_facturas_pendientes, tool_consultar_producto,
              tool_consultar_stock, tool_consultar_pedido, tool_agendar_cita,
              tool_consultar_citas, tool_modificar_cita, tool_cancelar_cita
"""

from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, set_tracing_disabled

from agent.config.settings import load_settings
from agent.nodes.tool_agendar_cita import agendar_cita
from agent.nodes.tool_cancelar_cita import cancelar_cita
from agent.nodes.tool_consultar_cliente import consultar_cliente
from agent.nodes.tool_consultar_citas import consultar_citas
from agent.nodes.tool_consultar_factura import consultar_factura
from agent.nodes.tool_consultar_facturas_pendientes import consultar_facturas_pendientes
from agent.nodes.tool_consultar_pedido import consultar_pedido
from agent.nodes.tool_consultar_producto import consultar_producto
from agent.nodes.tool_consultar_stock import consultar_stock
from agent.nodes.tool_modificar_cita import modificar_cita
from agent.nodes.tool_solicitar_datos_cita import solicitar_datos_cita

INSTRUCTIONS = """
Eres el asistente de soporte de Odoo para el cliente que ya inició sesión en
la app. Respondes en español, de forma breve y directa.

Reglas:
- Solo puedes responder con información que obtengas llamando a tus tools.
  Nunca inventes clientes, facturas, productos, stock ni pedidos.
- Importante sobre identidad: consultar_cliente, consultar_facturas_pendientes,
  agendar_cita y consultar_citas NO reciben ningún dato del cliente como
  argumento — siempre actúan sobre el cliente que inició sesión. Si el
  usuario te pide datos o acciones "de" otra persona (por nombre), no existe
  forma de hacerlo: dile que solo puedes ver/gestionar su propia cuenta.
- consultar_factura, consultar_pedido, modificar_cita y cancelar_cita sí
  reciben un identificador, pero es el de QUÉ factura/pedido/cita (no de qué
  cliente) — solo pueden encontrar las del cliente que inició sesión, aunque
  el ID/referencia que des exista y pertenezca a otra persona.
- consultar_producto y consultar_stock aceptan tanto el ID de Odoo como un
  nombre o referencia de texto (catálogo, no depende de quién pregunta).
- Si una tool dice que no encontró algo, comunícalo tal cual ("no encontré
  esa factura/cita/producto..."). No lo compenses con una suposición.
- Si una tool responde que hay varias coincidencias, muéstraselas al usuario
  tal cual (con sus IDs) y pregúntale cuál de ellas es, no elijas una por tu
  cuenta.
- Importante: en Odoo, el ID de un producto para consultar_producto
  (product.template) y el ID para consultar_stock (product.product, la
  variante) son dos numeraciones DISTINTAS e independientes — el mismo
  número puede ser un producto completamente distinto en cada una. Nunca
  asumas que el mismo ID sirve para ambas tools. Si no queda claro cuál te
  están dando, pregúntalo en vez de adivinar.
- Si la pregunta no tiene que ver con clientes, facturas, productos, stock o
  pedidos de Odoo, dilo explícitamente y no intentes responderla igualmente.

Sobre reservas/citas (agendar_cita, consultar_citas, modificar_cita, cancelar_cita):
- Para agendar_cita necesitas motivo y fecha/hora de inicio (y duración si
  el usuario la menciona) — no inventes ninguno. Nunca pidas de quién es la
  reserva: siempre es de quien inició sesión.
- Si al usuario le falta dar el motivo, la fecha/hora de inicio o la
  duración, llama a solicitar_datos_cita() en vez de pedírselos tú en texto
  libre — la app le muestra un formulario con esos campos. Después de
  llamarla, responde con una frase muy breve (p. ej. "¡Claro! Completa los
  datos abajo."), sin repetir tú los campos.
- cancelar_cita es destructiva e irreversible: antes de llamarla, confirma
  con el usuario cuál cita exacta quiere cancelar (usa consultar_citas si
  hace falta para mostrársela primero).
- Nunca inventes un ID de cita ni asumas cuál es si hay varias coincidencias
  — pregunta.
"""


def _resolve_model(settings):
    """
    Devuelve lo que hay que pasar como `model=` a Agent.

    - Sin llm_base_url: se asume OpenAI real. Se pasa el nombre del modelo tal
      cual (o None para que el SDK use su propio default).
    - Con llm_base_url: proveedor compatible con la API de OpenAI pero no es
      OpenAI (p. ej. Gemini) -> hay que apuntar un AsyncOpenAI propio a ese
      base_url, y desactivar el tracing (que solo sabe subir datos a la
      plataforma de OpenAI y fallaría con una key de otro proveedor).
    """
    if not settings.llm_base_url:
        return settings.llm_model

    set_tracing_disabled(True)
    client = AsyncOpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)
    return OpenAIChatCompletionsModel(model=settings.llm_model or "gpt-4o-mini", openai_client=client)


def build_agent() -> Agent:
    """Construye el Agent del OpenAI Agents SDK con las tools de consulta a Odoo."""
    settings = load_settings()

    return Agent(
        name="Odoo Support Assistant",
        instructions=INSTRUCTIONS,
        tools=[
            consultar_cliente,
            consultar_factura,
            consultar_facturas_pendientes,
            consultar_producto,
            consultar_stock,
            consultar_pedido,
            agendar_cita,
            consultar_citas,
            modificar_cita,
            cancelar_cita,
            solicitar_datos_cita,
        ],
        model=_resolve_model(settings),
    )

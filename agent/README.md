# Agente de soporte Odoo (patrón de nodos estilo n8n)

Agente de IA conversacional que atiende consultas de clientes apoyándose en Odoo
como única fuente de datos. Expone una API con FastAPI (`main.py`) consumida por
la app Android — ver el [README principal](../README.md) para cómo instalar y
ejecutar todo el proyecto junto (Odoo + agente + app).

## El patrón: cada archivo es un nodo

Igual que en un workflow de n8n, cada archivo en `nodes/` es una unidad
independiente con una única responsabilidad, una entrada y una salida claras.
`workflow.py` es el "canvas": el único lugar donde se declara cómo se
conectan los nodos entre sí.

| Nodo (archivo) | Equivalente en n8n | Responsabilidad |
|---|---|---|
| `nodes/input_trigger.py` | Webhook / Chat Trigger | Recibe y normaliza la petición entrante |
| `nodes/auth_login.py` | Nodo de autenticación | Valida email/contraseña contra Odoo (usuario de portal) |
| `nodes/auth_session.py` | — (estado de sesión) | Guarda el token de sesión → `partner_id`, en memoria |
| `nodes/current_partner.py` | — (contexto de ejecución) | `ContextVar` con la identidad del cliente que pregunta, inaccesible para el LLM |
| `nodes/memory_session.py` | — (estado del workflow) | Historial de la conversación (corto plazo) |
| `nodes/guardrails.py` | Validación / IF | Valida entrada y argumentos de tools |
| `nodes/agent_core.py` | Nodo "AI Agent" | Decide qué tool llamar (tool calling del LLM, OpenAI Agents SDK) |
| `nodes/cita_permissions.py` | Validación / IF | Comprueba los permisos por cliente (`assistant_can_*`) antes de ejecutar una tool de citas |
| `nodes/tool_consultar_cliente.py` | Nodo de acción | Consulta `res.partner` |
| `nodes/tool_consultar_factura.py` | Nodo de acción | Consulta `account.move` |
| `nodes/tool_consultar_facturas_pendientes.py` | Nodo de acción | Consulta facturas impagadas de un cliente |
| `nodes/tool_consultar_producto.py` | Nodo de acción | Consulta `product.template` |
| `nodes/tool_consultar_stock.py` | Nodo de acción | Consulta `stock.quant` |
| `nodes/tool_consultar_pedido.py` | Nodo de acción | Consulta `sale.order` |
| `nodes/tool_consultar_citas.py` | Nodo de acción | Consulta `calendar.event` del cliente |
| `nodes/tool_solicitar_datos_cita.py` | Nodo de acción | Señala a la app que muestre el formulario de agendar cita |
| `nodes/tool_agendar_cita.py` | Nodo de acción | Crea la reserva en `calendar.event` |
| `nodes/tool_modificar_cita.py` | Nodo de acción | Modifica una reserva existente |
| `nodes/tool_cancelar_cita.py` | Nodo de acción | Cancela una reserva existente |
| `nodes/consulta.py` | Nodo de acción | Cierra una consulta (transcripción → `assistant.consulta`) y lista las del cliente |
| `nodes/odoo_connector.py` | Nodo "Odoo" / credencial | Único punto de acceso a la API externa de Odoo |
| `nodes/output_response.py` | Respond to Webhook | Da forma a la respuesta final |
| `workflow.py` | El canvas del workflow | Conecta los nodos anteriores en orden |
| `main.py` | — | Expone el workflow vía FastAPI (`/auth/login`, `/chat`, `/consulta/finalizar`, `/consulta/listar`) |

## Regla de seguridad no negociable

`odoo_connector.py` es el **único** archivo con permiso para hablar con Odoo,
y lo hace exclusivamente contra la API externa que Odoo expone (XML-RPC) —
**nunca contra PostgreSQL directamente**. Ningún nodo `tool_*` abre su propia
conexión a Odoo. El agente se conecta con un usuario de integración de solo
lectura (`group_agent_readonly`, definido en `odoo/addons/assistant_agent`),
con permisos de escritura habilitados de forma explícita y mínima solo donde
el negocio lo requiere (citas de calendario, registro de consultas).

La identidad del cliente que pregunta la resuelve siempre el servidor a
partir de su token de sesión (`current_partner.py`) — el LLM nunca puede
pasar un `partner_id` arbitrario a una tool.

## Pruebas

Ver `tests/README.md` para las pruebas existentes.

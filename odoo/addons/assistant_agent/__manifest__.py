{
    "name": "Asistente IA — Integración",
    "version": "17.0.1.0.0",
    "summary": "Usuario de integración y permisos de solo lectura para el agente de IA externo.",
    "description": """
Crea un usuario de integración dedicado para el agente de IA (carpeta `agent/`
en la raíz del repo) y un grupo de seguridad de SOLO LECTURA sobre los
modelos que ese agente necesita consultar: res.partner, account.move,
product.template, product.product, sale.order y stock.quant.

El agente nunca se conecta a PostgreSQL directamente: siempre pasa por la
External API de Odoo (XML-RPC) autenticado como este usuario, así que lo
único que puede ver (o modificar) es exactamente lo que este módulo le
concede aquí.

Excepción de escritura: el usuario de integración tiene permiso completo
(lectura/creación/modificación/borrado) sobre calendar.event únicamente,
para poder agendar/consultar/modificar/cancelar reservas — todo lo demás
sigue siendo estrictamente de solo lectura.

Este módulo también trae datos de ejemplo de un negocio ficticio ("Café
Aroma"): productos de cafetería, clientes de ejemplo y reservas de
calendario, listos para probar el flujo de agendar_cita de punta a punta.

Permisos por cliente: cada contacto (res.partner) tiene una pestaña "Agente
IA" con casillas para permitir/bloquear que el agente agende, modifique o
cancele citas en su nombre — todo permitido por defecto, el admin desmarca
la casilla del cliente concreto al que quiera restringir.

Login real: los 3 clientes de demo tienen usuario Portal (base.group_portal)
para poder probar la autenticación real de la app (ver agent/nodes/auth_login.py),
contraseña de prueba "demo12345" para los tres.

Registro de consultas: cada vez que un cliente cierra una conversación en el
chat ("Finalizar consulta"), queda un registro en Asistente IA > Consultas
con la transcripción completa — el bot solo puede crear estos registros,
nunca leerlos ni modificarlos.

Credenciales para agent/.env:
    ODOO_URL=http://localhost:8069
    ODOO_DB=odoo_test
    ODOO_USERNAME=agente.ia@integracion.local
    ODOO_API_KEY=<ver nota de seguridad más abajo>

Nota de seguridad: este módulo fija una contraseña de arranque para poder
probar el agente de inmediato. Antes de usar esto fuera de un entorno de
pruebas local, entra en Ajustes > Usuarios > Agente IA (integración) >
Seguridad de la cuenta > Nueva clave API, genera una API key real, y
sustitúyela en agent/.env — así la contraseña de la cuenta deja de ser
necesaria y la clave se puede revocar sin tocar el usuario.
""",
    "category": "Tools",
    "depends": ["base", "contacts", "account", "sale_management", "stock", "calendar"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/integration_user.xml",
        "data/demo_products.xml",
        "data/demo_partners.xml",
        "data/demo_portal_users.xml",
        "data/demo_reservations.xml",
        "views/res_partner_views.xml",
        "views/consulta_views.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}

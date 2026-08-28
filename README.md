# Asistente de Soporte con IA — Café Aroma

Proyecto Fin de Ciclo (2º DAM Dual). Asistente conversacional de atención al
cliente para un negocio de hostelería ficticio ("Café Aroma"), construido
sobre tres piezas independientes:

- **`kotlin-app/`** — app Android nativa (Kotlin) con la que chatea el cliente.
- **`agent/`** — agente de IA en Python (FastAPI + OpenAI Agents SDK + Gemini) que entiende el lenguaje natural y ejecuta acciones reales sobre Odoo.
- **`odoo/`** — Odoo 17 (Docker), ERP y única fuente de datos. Incluye el addon propio `assistant_agent` (permisos, modelo de consultas, datos de demo).

La documentación completa del proyecto (estudio de mercado, arquitectura,
diagramas, pruebas, problemas y soluciones, manuales…) está en
**[`docs/memoria_proyecto.pdf`](docs/memoria_proyecto.pdf)**. Este README solo
cubre cómo instalar y ejecutar el proyecto.

## Arquitectura

```
App Android  ──HTTPS/JSON──►  Agente (FastAPI)  ──XML-RPC──►  Odoo 17  ──►  PostgreSQL
(Kotlin)                      (Python, LLM)                   (Docker)
```

La app nunca habla directamente con Odoo: todo pasa por el agente, que
resuelve la identidad del cliente por su sesión (nunca por lo que diga el
LLM) y solo puede escribir en Odoo donde el módulo `assistant_agent` se lo
permite explícitamente.

## Requisitos previos

- **Docker Desktop** (para Odoo + PostgreSQL).
- **Python 3.11+** con `pip`.
- **Android Studio** (con un SDK de Android instalado) para compilar/ejecutar la app.
- Una **clave de API de Google Gemini** (capa gratuita válida) — o cualquier otro proveedor compatible con la API de OpenAI.

## 1. Puesta en marcha de Odoo

```powershell
cd odoo
docker compose up -d
```

Esto crea la base de datos `odoo_test` y arranca Odoo con sus módulos base.
Después hay que instalar el addon propio del proyecto:

1. Entra en `http://localhost:8069` (usuario `admin`, contraseña `admin` — son las credenciales por defecto de esta base de datos local de pruebas).
2. Ve a **Apps**, quita el filtro "Apps" de la búsqueda, busca **"Asistente IA"** e instálalo.

Esto deja creados automáticamente: el usuario de integración del agente, los
permisos de solo lectura, los datos de demo de "Café Aroma" (productos,
clientes, reservas) y 3 clientes con usuario de **Portal** para poder probar
el login real desde la app (ver credenciales más abajo).

> **Nota:** si en algún momento modificas ficheros Python o añades ficheros
> nuevos al addon (`odoo/addons/assistant_agent`), Odoo no los detecta en
> caliente. Hace falta reiniciar el contenedor antes de volver a actualizar
> el módulo:
> ```powershell
> docker restart odoo-odoo-1
> ```
> y luego **Apps → Asistente IA → Actualizar**.

## 2. Puesta en marcha del agente

```powershell
cd agent
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edita `agent/.env` y rellena:

```
LLM_API_KEY=<tu clave de Gemini (o del proveedor que uses)>
LLM_MODEL=gemini-3.1-flash-lite
LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/

ODOO_URL=http://localhost:8069
ODOO_DB=odoo_test
ODOO_USERNAME=agente.ia@integracion.local
ODOO_API_KEY=agente-ia-cambia-esta-clave
```

(`ODOO_USERNAME`/`ODOO_API_KEY` ya vienen fijados por el propio addon al
instalarlo — no hay que crear ese usuario a mano.)

Arranca el servidor:

```powershell
fastapi dev main.py --host 0.0.0.0 --port 8000
```

La API queda en `http://localhost:8000`, con documentación interactiva en
`http://localhost:8000/docs`.

> **Nota:** las sesiones de login y el historial de conversación viven en
> memoria del proceso — reiniciar el servidor obliga a todos los clientes a
> iniciar sesión de nuevo en la app.

## 3. Puesta en marcha de la app Android

1. Abre la carpeta `kotlin-app/` en Android Studio y deja que sincronice Gradle.
2. Ejecuta la app en un emulador o dispositivo físico.
3. En la pantalla de login, entra en **"Ajustes del servidor"** e indica la URL del agente:
   - Desde el **emulador**: `http://10.0.2.2:8000/` (ya viene puesta por defecto — `10.0.2.2` es el alias que usa el emulador para el `localhost` de la máquina anfitriona).
   - Desde un **dispositivo físico** en la misma red: `http://<IP de tu PC>:8000/`.
4. Inicia sesión con uno de los usuarios de prueba de abajo.

## Credenciales de prueba

| Cliente (app / portal Odoo) | Email | Contraseña |
|---|---|---|
| Ana Beltrán | `ana.beltran@example.com` | `demo12345` |
| Luis Mendoza | `luis.mendoza@example.com` | `demo12345` |
| María Ferreiro | `maria.ferreiro@example.com` | `demo12345` |

| Backoffice de Odoo | Usuario | Contraseña |
|---|---|---|
| Administrador | `admin` | `admin` |

## Probar el flujo completo

1. Entra en la app con un cliente de prueba.
2. En la pestaña **Chat**, pulsa **"Comenzar consulta"** y escribe algo como *"quiero agendar una mesa para el sábado a las 20:00"* o *"¿cuál es el estado de mi último pedido?"*.
3. Pulsa **"Finalizar consulta"** al terminar.
4. En la pestaña **Consultas**, verás el historial real (filtrable por Pendiente/Resuelta).
5. Desde Odoo (**Asistente IA → Consultas**), como admin, puedes ver la transcripción completa de cualquier cliente y marcar la consulta como "Resuelta"; en **Calendario** verás las citas reales que el agente haya creado.

## Estructura del repositorio

```
agent/          Agente Python (FastAPI + OpenAI Agents SDK)
  nodes/        Cada archivo es un "nodo" con una única responsabilidad (ver agent/README.md)
  config/       Carga de configuración (.env)
kotlin-app/     App Android (Kotlin)
  app/src/main/java/.../ui/      Pantallas (Chat, Consultas, Login, Ajustes)
  app/src/main/java/.../data/    Repositorio de datos (Retrofit + implementación real)
odoo/
  docker-compose.yml
  addons/assistant_agent/        Addon propio: permisos, modelo de consultas, datos de demo
docs/
  memoria_proyecto.pdf           Memoria completa del proyecto
  memoria_proyecto.html          Fuente editable de la memoria
```

## Limitaciones conocidas

- Las sesiones (login, historial de chat) se guardan en memoria del proceso del agente — no sobreviven a un reinicio.
- No hay tests automatizados; la verificación se hizo de forma manual y end-to-end (documentado en la memoria).
- Pensado para desarrollo local — no incluye configuración de despliegue en producción (HTTPS, backups, etc.).

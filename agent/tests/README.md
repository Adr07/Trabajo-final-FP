# Tests

No hay tests automatizados todavía — la verificación de cada funcionalidad se
hizo de forma manual y end-to-end (`curl`/API, consultas SQL directas sobre
Postgres, y pruebas reales en el emulador Android), documentada en el
apartado "Pruebas y validaciones realizadas" de `docs/memoria_proyecto.pdf`.

Como línea de mejora, si se añaden tests automatizados deberían seguir las
categorías de la skill `python-ai-agent` (`references/testing.md`):

- Un test por nodo `tool_*`: input válido, input inválido, caso "no encontrado".
- Un test para `odoo_connector`, mockeando la API externa de Odoo (sin pegarle
  a un Odoo real en el test unitario).
- Tests de comportamiento del agente (`agent_core` + `workflow`): elige la tool
  correcta, no inventa datos cuando Odoo no devuelve nada, maneja el fallo de
  una tool sin crashear.

Sin llamar al LLM real salvo en un puñado de tests de humo/integración aparte.

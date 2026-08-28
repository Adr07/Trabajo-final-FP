"""
Configuración del agente, cargada desde variables de entorno (`.env`).

Nunca hardcodear aquí API keys, contraseñas ni URLs privadas — ver
`.env.example` para las variables esperadas.
"""

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv

_ENV_LOADED = False


@dataclass(frozen=True)
class Settings:
    # LLM — agnóstico de proveedor. Si llm_base_url está vacío se usa el
    # cliente por defecto del SDK (OpenAI). Si tiene valor, se construye un
    # cliente AsyncOpenAI apuntando ahí (p. ej. el endpoint compatible con
    # OpenAI de Gemini), con llm_api_key como credencial de ESE proveedor.
    llm_api_key: str
    llm_model: str | None
    llm_base_url: str | None

    # Odoo — credenciales del usuario de integración creado por el módulo
    # odoo/addons/assistant_agent, nunca un usuario humano.
    odoo_url: str
    odoo_db: str
    odoo_username: str
    odoo_api_key: str


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Falta la variable de entorno {name}. Revisa agent/.env (copia agent/.env.example)."
        )
    return value


def load_settings() -> Settings:
    """Carga y valida la configuración desde variables de entorno."""
    global _ENV_LOADED
    if not _ENV_LOADED:
        load_dotenv(Path(__file__).resolve().parent.parent / ".env")
        _ENV_LOADED = True

    return Settings(
        llm_api_key=_require("LLM_API_KEY"),
        llm_model=os.getenv("LLM_MODEL") or None,
        llm_base_url=os.getenv("LLM_BASE_URL") or None,
        odoo_url=_require("ODOO_URL").rstrip("/"),
        odoo_db=_require("ODOO_DB"),
        odoo_username=_require("ODOO_USERNAME"),
        odoo_api_key=_require("ODOO_API_KEY"),
    )

package com.odooassistant.support.config

import android.content.Context
import com.odooassistant.support.AsistenteOdooApp

/**
 * Configuración editable desde la app: a qué servidor del agente conectarse.
 * Persistida en SharedPreferences para poder cambiarla sin recompilar (p. ej.
 * pasar de un agente local en `10.0.2.2` a uno real en producción, o a otro
 * entorno de Odoo).
 */
object AgentSettings {

    // 10.0.2.2 es el alias del emulador de Android hacia el localhost de la
    // máquina anfitriona, donde corre `uvicorn agent.main:app` en desarrollo.
    const val DEFAULT_BASE_URL = "http://10.0.2.2:8000/"

    private const val PREFS_NAME = "agent_settings"
    private const val KEY_BASE_URL = "agent_base_url"

    private fun prefs() =
        AsistenteOdooApp.instance.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    fun getBaseUrl(): String = prefs().getString(KEY_BASE_URL, DEFAULT_BASE_URL) ?: DEFAULT_BASE_URL

    fun setBaseUrl(url: String) {
        val normalized = url.trim().let { if (it.endsWith("/")) it else "$it/" }
        prefs().edit().putString(KEY_BASE_URL, normalized).apply()
    }

    fun resetToDefault() {
        prefs().edit().remove(KEY_BASE_URL).apply()
    }
}

package com.odooassistant.support.config

import android.content.Context
import com.odooassistant.support.AsistenteOdooApp

/**
 * Sesión del cliente autenticado: el token que devuelve /auth/login y el
 * nombre a mostrar. Persistida en SharedPreferences (mismo patrón que
 * AgentSettings) para que la sesión sobreviva a cerrar la app.
 */
object SessionManager {

    private const val PREFS_NAME = "session"
    private const val KEY_TOKEN = "session_token"
    private const val KEY_USER_NAME = "session_user_name"

    private fun prefs() =
        AsistenteOdooApp.instance.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    fun getToken(): String? = prefs().getString(KEY_TOKEN, null)

    fun getUserName(): String? = prefs().getString(KEY_USER_NAME, null)

    fun isLoggedIn(): Boolean = !getToken().isNullOrBlank()

    fun setSession(token: String, name: String) {
        prefs().edit()
            .putString(KEY_TOKEN, token)
            .putString(KEY_USER_NAME, name)
            .apply()
    }

    fun clear() {
        prefs().edit().clear().apply()
    }
}

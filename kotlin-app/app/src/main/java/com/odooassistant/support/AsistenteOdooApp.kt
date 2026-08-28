package com.odooassistant.support

import android.app.Application

/**
 * Solo existe para dar acceso a un Application Context estático a
 * [com.odooassistant.support.config.AgentSettings] (necesario para leer
 * SharedPreferences) sin tener que pasar Context por toda la cadena de
 * repositorio/fragments.
 */
class AsistenteOdooApp : Application() {

    companion object {
        lateinit var instance: AsistenteOdooApp
            private set
    }

    override fun onCreate() {
        super.onCreate()
        instance = this
    }
}

package com.odooassistant.support.model

/** Una consulta (conversación) ya cerrada del cliente, tal y como quedó registrada en Odoo. */
data class Consulta(
    val start: String,
    val stop: String,
    val transcript: String,
    /** "pendiente" o "resuelta". Solo lo cambia el admin desde Odoo; la app únicamente lo muestra. */
    val state: String,
)

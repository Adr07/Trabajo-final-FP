package com.odooassistant.support.model

data class ChatMessage(
    val who: String,
    val text: String,
    val time: String,
    /** true si el mensaje lo escribe el agente (asistente) */
    val fromAgent: Boolean,
    /** "agendar_cita" si el agente pide mostrar el formulario de reserva en vez de texto libre */
    val requiresForm: String? = null,
)

package com.odooassistant.support.data

import com.odooassistant.support.model.ChatMessage
import com.odooassistant.support.model.Company
import com.odooassistant.support.model.Consulta

/**
 * Implementación en memoria de [AssistantRepository]. Sin consultas de ejemplo: arranca vacía
 * hasta que el módulo Odoo que expondría los endpoints reales exista.
 */
object MockAssistantRepository : AssistantRepository {

    private val companies = listOf(
        Company("La Parrilla del Centro", "odoo17-prod"),
        Company("La Parrilla — Sucursal Norte", "odoo17-prod"),
        Company("Entorno de pruebas", "odoo17-staging"),
    )

    private val chat = mutableListOf<ChatMessage>()

    override suspend fun login(email: String, password: String): Result<String> = Result.success("Cliente de prueba")

    override fun getCompanies(): List<Company> = companies

    override fun getChatMessages(): List<ChatMessage> = chat

    private var consultaActiva = true

    override fun hasActiveConsulta(): Boolean = consultaActiva

    override fun iniciarConsulta() {
        chat.clear()
        consultaActiva = true
    }

    override suspend fun finalizarConsulta(): Result<Unit> {
        consultaActiva = false
        return Result.success(Unit)
    }

    override suspend fun getConsultas(): Result<List<Consulta>> = Result.success(emptyList())

    override suspend fun sendMessage(text: String): List<ChatMessage> {
        chat.add(ChatMessage(who = "Tú · soporte", fromAgent = false, time = "11:06", text = text))
        chat.add(
            ChatMessage(
                who = "Asistente", fromAgent = true, time = "11:06",
                text = "Recibido. En cuanto tenga una acción para proponerte, te aviso aquí.",
            ),
        )
        return chat
    }
}

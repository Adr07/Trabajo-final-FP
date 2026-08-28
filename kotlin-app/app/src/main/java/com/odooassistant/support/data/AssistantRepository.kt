package com.odooassistant.support.data

import com.odooassistant.support.model.ChatMessage
import com.odooassistant.support.model.Company
import com.odooassistant.support.model.Consulta

/**
 * Contrato de acceso a datos del asistente. Hoy lo implementa [MockAssistantRepository]
 * con datos en memoria; más adelante se puede sustituir por una implementación Retrofit
 * contra el módulo Odoo (POST /assistant/session, GET /assistant/requests, etc.) sin
 * tocar las Vistas ni los Controladores.
 */
interface AssistantRepository {

    /** Autentica al cliente contra Odoo (usuario Portal). Devuelve su nombre si tiene éxito. */
    suspend fun login(email: String, password: String): Result<String>

    fun getCompanies(): List<Company>

    fun getChatMessages(): List<ChatMessage>

    /** Añade el mensaje del usuario y una respuesta del agente al historial, y lo devuelve completo. */
    suspend fun sendMessage(text: String): List<ChatMessage>

    /** true si hay una consulta (conversación) abierta ahora mismo. */
    fun hasActiveConsulta(): Boolean

    /** Abre una consulta nueva: limpia el historial local y arranca un conversation_id nuevo. */
    fun iniciarConsulta()

    /** Cierra la consulta activa: se guarda en Odoo con su transcripción y se limpia el estado local. */
    suspend fun finalizarConsulta(): Result<Unit>

    /** Consultas ya cerradas del cliente autenticado, más recientes primero. */
    suspend fun getConsultas(): Result<List<Consulta>>
}

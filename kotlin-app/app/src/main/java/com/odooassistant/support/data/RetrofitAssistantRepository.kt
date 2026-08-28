package com.odooassistant.support.data

import com.odooassistant.support.config.SessionManager
import com.odooassistant.support.data.remote.AgentApiClient
import com.odooassistant.support.data.remote.ChatRequestDto
import com.odooassistant.support.data.remote.FinalizarConsultaRequestDto
import com.odooassistant.support.data.remote.ListarConsultasRequestDto
import com.odooassistant.support.data.remote.LoginRequestDto
import com.odooassistant.support.model.ChatMessage
import com.odooassistant.support.model.Company
import com.odooassistant.support.model.Consulta
import java.io.IOException
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.UUID

/**
 * Implementación real para el Chat y las Consultas: habla por HTTP con
 * `agent/main.py` (el agente Python de soporte Odoo, ver `agent/README.md`).
 * `getCompanies()` sigue delegando en [MockAssistantRepository] al no tener
 * todavía un backend propio ni consumidor real en la UI.
 */
object RetrofitAssistantRepository : AssistantRepository {

    // El conversation_id cambia cada vez que se inicia una consulta nueva
    // (ver iniciarConsulta/finalizarConsulta) — el historial real vive en
    // agent/nodes/memory_session.py, aquí solo hace falta reenviarlo tal cual.
    private var conversationId = UUID.randomUUID().toString()

    // null = no hay consulta abierta. Cuando hay una, guarda el instante en
    // que se abrió (lo necesita el backend para el campo "start" del
    // registro de la consulta al finalizar).
    private var consultaIniciadaEn: String? = null

    private val chatHistory = mutableListOf<ChatMessage>()

    private val fechaHoraFormato = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.US)

    override fun hasActiveConsulta(): Boolean = consultaIniciadaEn != null

    override fun iniciarConsulta() {
        conversationId = UUID.randomUUID().toString()
        chatHistory.clear()
        consultaIniciadaEn = fechaHoraFormato.format(Date())
    }

    override suspend fun finalizarConsulta(): Result<Unit> {
        val startedAt = consultaIniciadaEn
        val token = SessionManager.getToken()
        val resultado = if (startedAt == null || token.isNullOrBlank()) {
            Result.success(Unit)
        } else {
            try {
                AgentApiClient.api.finalizarConsulta(
                    FinalizarConsultaRequestDto(conversationId, token, startedAt),
                )
                Result.success(Unit)
            } catch (e: IOException) {
                Result.failure(Exception("No pude conectar con el agente para cerrar la consulta."))
            } catch (e: retrofit2.HttpException) {
                Result.failure(Exception("El agente respondió con un error (${e.code()}) al cerrar la consulta."))
            }
        }
        // Aunque falle la llamada de red, la consulta se da por cerrada del
        // lado de la app: no tiene sentido dejar al cliente atrapado en una
        // consulta que ya no puede cerrar.
        consultaIniciadaEn = null
        chatHistory.clear()
        return resultado
    }

    override suspend fun login(email: String, password: String): Result<String> {
        return try {
            val result = AgentApiClient.api.login(LoginRequestDto(email, password))
            SessionManager.setSession(result.token, result.name)
            Result.success(result.name)
        } catch (e: retrofit2.HttpException) {
            Result.failure(Exception("Email o contraseña incorrectos."))
        } catch (e: IOException) {
            Result.failure(Exception("No pude conectar con el agente. ¿Está corriendo `uvicorn agent.main:app`?"))
        }
    }

    override fun getCompanies(): List<Company> = MockAssistantRepository.getCompanies()

    override fun getChatMessages(): List<ChatMessage> = chatHistory

    override suspend fun sendMessage(text: String): List<ChatMessage> {
        chatHistory.add(ChatMessage(who = "Tú · soporte", fromAgent = false, time = "", text = text))

        val token = SessionManager.getToken()
        var requiresForm: String? = null
        val respuesta = if (token.isNullOrBlank()) {
            "No hay una sesión activa. Vuelve a iniciar sesión."
        } else {
            try {
                val result = AgentApiClient.api.chat(ChatRequestDto(conversationId, text, token))
                requiresForm = result.requiresForm
                result.response
            } catch (e: IOException) {
                "No pude conectar con el agente. ¿Está corriendo `uvicorn agent.main:app` en tu máquina?"
            } catch (e: retrofit2.HttpException) {
                "El agente respondió con un error (${e.code()}). Revisa los logs de uvicorn."
            }
        }

        chatHistory.add(
            ChatMessage(who = "Asistente", fromAgent = true, time = "", text = respuesta, requiresForm = requiresForm),
        )
        return chatHistory
    }

    override suspend fun getConsultas(): Result<List<Consulta>> {
        val token = SessionManager.getToken()
        if (token.isNullOrBlank()) {
            return Result.failure(Exception("No hay una sesión activa. Vuelve a iniciar sesión."))
        }
        return try {
            val result = AgentApiClient.api.listarConsultas(ListarConsultasRequestDto(token))
            Result.success(
                result.map { Consulta(start = it.start, stop = it.stop, transcript = it.transcript, state = it.state) },
            )
        } catch (e: IOException) {
            Result.failure(Exception("No pude conectar con el agente para cargar tus consultas."))
        } catch (e: retrofit2.HttpException) {
            Result.failure(Exception("El agente respondió con un error (${e.code()}) al cargar tus consultas."))
        }
    }

}

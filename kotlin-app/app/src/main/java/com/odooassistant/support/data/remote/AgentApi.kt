package com.odooassistant.support.data.remote

import com.google.gson.annotations.SerializedName
import com.odooassistant.support.config.AgentSettings
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.POST
import java.util.concurrent.TimeUnit
import okhttp3.OkHttpClient

/**
 * Contrato HTTP contra `agent/main.py` (FastAPI). El campo `conversation_id`
 * mantiene el historial de la conversación en el propio agente (ver
 * `agent/nodes/memory_session.py`) — la app solo necesita reenviarlo tal cual.
 * `session_token` es el que devuelve /auth/login — el agente lo resuelve al
 * cliente autenticado (ver `agent/nodes/auth_session.py`) antes de tocar
 * ninguna tool.
 */
data class ChatRequestDto(
    @SerializedName("conversation_id") val conversationId: String,
    @SerializedName("message") val message: String,
    @SerializedName("session_token") val sessionToken: String,
)

data class ChatResponseDto(
    @SerializedName("conversation_id") val conversationId: String,
    @SerializedName("response") val response: String,
    @SerializedName("requires_form") val requiresForm: String? = null,
)

data class LoginRequestDto(
    @SerializedName("email") val email: String,
    @SerializedName("password") val password: String,
)

data class LoginResponseDto(
    @SerializedName("token") val token: String,
    @SerializedName("name") val name: String,
)

data class FinalizarConsultaRequestDto(
    @SerializedName("conversation_id") val conversationId: String,
    @SerializedName("session_token") val sessionToken: String,
    @SerializedName("started_at") val startedAt: String,
)

data class ListarConsultasRequestDto(
    @SerializedName("session_token") val sessionToken: String,
)

data class ConsultaDto(
    @SerializedName("start") val start: String,
    @SerializedName("stop") val stop: String,
    @SerializedName("transcript") val transcript: String,
    @SerializedName("state") val state: String,
)

interface AgentApi {
    @POST("chat")
    suspend fun chat(@Body request: ChatRequestDto): ChatResponseDto

    @POST("auth/login")
    suspend fun login(@Body request: LoginRequestDto): LoginResponseDto

    @POST("consulta/finalizar")
    suspend fun finalizarConsulta(@Body request: FinalizarConsultaRequestDto)

    @POST("consulta/listar")
    suspend fun listarConsultas(@Body request: ListarConsultasRequestDto): List<ConsultaDto>
}

/**
 * Reconstruye el cliente Retrofit cada vez que la URL guardada en
 * [AgentSettings] cambia (p. ej. tras editarla en Ajustes), sin necesidad de
 * reiniciar la app.
 */
object AgentApiClient {
    private var cachedBaseUrl: String? = null
    private var cachedApi: AgentApi? = null

    val api: AgentApi
        get() {
            val baseUrl = AgentSettings.getBaseUrl()
            if (baseUrl != cachedBaseUrl || cachedApi == null) {
                cachedApi = build(baseUrl)
                cachedBaseUrl = baseUrl
            }
            return cachedApi!!
        }

    private fun build(baseUrl: String): AgentApi {
        val client = OkHttpClient.Builder()
            .connectTimeout(10, TimeUnit.SECONDS)
            .readTimeout(60, TimeUnit.SECONDS) // el LLM puede tardar más que una API normal
            .build()

        return Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(AgentApi::class.java)
    }
}

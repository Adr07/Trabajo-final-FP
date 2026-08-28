package com.odooassistant.support.ui.chat

import android.animation.Animator
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.google.android.material.datepicker.MaterialDatePicker
import com.google.android.material.timepicker.MaterialTimePicker
import com.google.android.material.timepicker.TimeFormat
import com.odooassistant.support.R
import com.odooassistant.support.data.RetrofitAssistantRepository
import com.odooassistant.support.databinding.FragmentChatBinding
import com.odooassistant.support.ui.common.applyPressAnimation
import com.odooassistant.support.ui.common.startTyping
import com.odooassistant.support.ui.common.stopTyping
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.Calendar
import java.util.Locale
import java.util.TimeZone

/** Controlador de la pestaña Chat: conversación real con el agente (agent/main.py). */
class ChatFragment : Fragment() {

    private var _binding: FragmentChatBinding? = null
    private val binding get() = _binding!!

    private val repository = RetrofitAssistantRepository
    private lateinit var adapter: ChatAdapter
    private var typingAnimators: List<Animator> = emptyList()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?,
    ): View {
        _binding = FragmentChatBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.header.headerKicker.text = getString(R.string.chat_kicker)
        binding.header.headerTitle.text = getString(R.string.chat_title)
        binding.header.btnAvatar.visibility = View.VISIBLE
        binding.header.btnAvatar.setOnClickListener { openLogin() }

        adapter = ChatAdapter(
            repository.getChatMessages(),
            onPickDateTime = { onPicked -> pickDateTime(onPicked) },
            onSubmitForm = { motivo, inicioIso, duracionMinutos -> submitAgendarForm(motivo, inicioIso, duracionMinutos) },
        )
        binding.recyclerChat.layoutManager = LinearLayoutManager(requireContext())
        binding.recyclerChat.adapter = adapter

        binding.quickReplies.visibility = View.GONE

        binding.btnSend.applyPressAnimation()
        binding.btnSend.setOnClickListener { sendTypedMessage() }
        binding.inputMessage.setOnEditorActionListener { _, actionId, _ ->
            if (actionId == android.view.inputmethod.EditorInfo.IME_ACTION_SEND) {
                sendTypedMessage()
                true
            } else {
                false
            }
        }

        binding.btnComenzarConsulta.applyPressAnimation()
        binding.btnComenzarConsulta.setOnClickListener {
            repository.iniciarConsulta()
            adapter.submitList(repository.getChatMessages())
            refreshConsultaState()
        }

        binding.btnFinalizarConsulta.applyPressAnimation()
        binding.btnFinalizarConsulta.setOnClickListener {
            binding.btnFinalizarConsulta.isEnabled = false
            viewLifecycleOwner.lifecycleScope.launch {
                repository.finalizarConsulta()
                binding.btnFinalizarConsulta.isEnabled = true
                refreshConsultaState()
            }
        }

        refreshConsultaState()
    }

    private fun refreshConsultaState() {
        val activa = repository.hasActiveConsulta()
        binding.activeConsultaContainer.visibility = if (activa) View.VISIBLE else View.GONE
        binding.idleConsultaContainer.visibility = if (activa) View.GONE else View.VISIBLE
        binding.btnFinalizarConsulta.visibility = if (activa) View.VISIBLE else View.GONE
        if (activa) {
            adapter.submitList(repository.getChatMessages())
            scrollToBottom()
        }
    }

    private fun sendTypedMessage() {
        val text = binding.inputMessage.text?.toString()?.trim().orEmpty()
        if (text.isEmpty()) return
        binding.inputMessage.text?.clear()
        sendMessage(text)
    }

    private fun submitAgendarForm(motivo: String, inicioIso: String, duracionMinutos: Int?) {
        val texto = buildString {
            append("Motivo: ").append(motivo).append(". ")
            append("Fecha y hora de inicio: ").append(inicioIso).append(".")
            if (duracionMinutos != null) {
                append(" Duración: ").append(duracionMinutos).append(" minutos.")
            }
        }
        sendMessage(texto)
    }

    private fun sendMessage(text: String) {
        binding.btnSend.isEnabled = false
        showTyping()

        viewLifecycleOwner.lifecycleScope.launch {
            val historial = repository.sendMessage(text)
            hideTyping()
            adapter.submitList(historial)
            scrollToBottom()
            binding.btnSend.isEnabled = true
        }
    }

    private fun pickDateTime(onPicked: (String) -> Unit) {
        val datePicker = MaterialDatePicker.Builder.datePicker()
            .setTitleText(getString(R.string.chat_form_fecha_hint))
            .build()
        datePicker.addOnPositiveButtonClickListener { selectionUtcMillis ->
            val utcCal = Calendar.getInstance(TimeZone.getTimeZone("UTC"))
            utcCal.timeInMillis = selectionUtcMillis
            val year = utcCal.get(Calendar.YEAR)
            val month = utcCal.get(Calendar.MONTH)
            val day = utcCal.get(Calendar.DAY_OF_MONTH)

            val timePicker = MaterialTimePicker.Builder()
                .setTimeFormat(TimeFormat.CLOCK_24H)
                .setTitleText(getString(R.string.chat_form_fecha_hint))
                .build()
            timePicker.addOnPositiveButtonClickListener {
                val localCal = Calendar.getInstance()
                localCal.set(year, month, day, timePicker.hour, timePicker.minute, 0)
                val formato = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.US)
                onPicked(formato.format(localCal.time))
            }
            timePicker.show(childFragmentManager, "agendar_time_picker")
        }
        datePicker.show(childFragmentManager, "agendar_date_picker")
    }

    private fun showTyping() {
        binding.typingIndicator.visibility = View.VISIBLE
        typingAnimators = startTyping(
            listOf(binding.typingDot1, binding.typingDot2, binding.typingDot3),
        )
    }

    private fun hideTyping() {
        stopTyping(typingAnimators)
        typingAnimators = emptyList()
        binding.typingIndicator.visibility = View.GONE
    }

    private fun scrollToBottom() {
        binding.recyclerChat.post {
            binding.recyclerChat.scrollToPosition(adapter.itemCount - 1)
        }
    }

    private fun openLogin() {
        com.odooassistant.support.config.SessionManager.clear()
        startActivity(android.content.Intent(requireContext(), com.odooassistant.support.ui.login.LoginActivity::class.java))
    }

    override fun onDestroyView() {
        stopTyping(typingAnimators)
        super.onDestroyView()
        _binding = null
    }
}

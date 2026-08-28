package com.odooassistant.support.ui.chat

import android.view.Gravity
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.RecyclerView
import com.odooassistant.support.R
import com.odooassistant.support.databinding.ItemChatBubbleBinding
import com.odooassistant.support.model.ChatMessage
import com.odooassistant.support.ui.common.applyPressAnimation

class ChatAdapter(
    private var messages: List<ChatMessage>,
    private val onPickDateTime: ((String) -> Unit) -> Unit,
    private val onSubmitForm: (motivo: String, inicioIso: String, duracionMinutos: Int?) -> Unit,
) : RecyclerView.Adapter<ChatAdapter.ViewHolder>() {

    inner class ViewHolder(val binding: ItemChatBubbleBinding) : RecyclerView.ViewHolder(binding.root)

    fun submitList(newMessages: List<ChatMessage>) {
        messages = newMessages
        notifyDataSetChanged()
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemChatBubbleBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return ViewHolder(binding)
    }

    override fun getItemCount(): Int = messages.size

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val message = messages[position]
        val context = holder.itemView.context
        val binding = holder.binding

        binding.who.text = "${message.who} · ${message.time}"
        binding.text.text = message.text

        val params = binding.bubbleContainer.layoutParams as android.widget.FrameLayout.LayoutParams
        params.gravity = if (message.fromAgent) Gravity.START else Gravity.END
        binding.bubbleContainer.layoutParams = params

        binding.bubbleContainer.setBackgroundResource(
            if (message.fromAgent) R.drawable.bg_bubble_agent else R.drawable.bg_bubble_user,
        )
        binding.who.setTextColor(
            ContextCompat.getColor(
                context,
                if (message.fromAgent) R.color.color_accent_700 else R.color.color_neutral_700,
            ),
        )
        binding.text.setTextColor(
            ContextCompat.getColor(
                context,
                if (message.fromAgent) R.color.color_accent_900 else R.color.color_text,
            ),
        )

        if (message.requiresForm == "agendar_cita") {
            binding.formAgendarContainer.visibility = View.VISIBLE
            binding.formInputMotivo.setText("")
            binding.formInputFechaHora.setText("")
            binding.formInputDuracion.setText("")

            binding.formInputFechaHora.setOnClickListener {
                onPickDateTime { iso -> binding.formInputFechaHora.setText(iso) }
            }
            binding.btnSubmitForm.applyPressAnimation()
            binding.btnSubmitForm.setOnClickListener {
                val motivo = binding.formInputMotivo.text?.toString()?.trim().orEmpty()
                val inicioIso = binding.formInputFechaHora.text?.toString()?.trim().orEmpty()
                val duracion = binding.formInputDuracion.text?.toString()?.trim()?.toIntOrNull()
                if (motivo.isNotEmpty() && inicioIso.isNotEmpty()) {
                    onSubmitForm(motivo, inicioIso, duracion)
                }
            }
        } else {
            binding.formAgendarContainer.visibility = View.GONE
        }
    }
}

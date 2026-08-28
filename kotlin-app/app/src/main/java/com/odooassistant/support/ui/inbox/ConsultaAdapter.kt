package com.odooassistant.support.ui.inbox

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.RecyclerView
import com.odooassistant.support.R
import com.odooassistant.support.databinding.ItemConsultaBinding
import com.odooassistant.support.model.Consulta
import java.text.SimpleDateFormat
import java.util.Locale

class ConsultaAdapter(
    private var consultas: List<Consulta>,
    private val onClick: (Consulta) -> Unit,
) : RecyclerView.Adapter<ConsultaAdapter.ViewHolder>() {

    inner class ViewHolder(val binding: ItemConsultaBinding) : RecyclerView.ViewHolder(binding.root)

    fun submitList(newConsultas: List<Consulta>) {
        consultas = newConsultas
        notifyDataSetChanged()
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemConsultaBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return ViewHolder(binding)
    }

    override fun getItemCount(): Int = consultas.size

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val consulta = consultas[position]
        val context = holder.itemView.context
        holder.binding.dateRange.text = formatRange(consulta.start, consulta.stop)
        holder.binding.preview.text = previewOf(consulta.transcript)
        holder.binding.stateBadge.text = context.getString(stateLabelRes(consulta.state))
        holder.binding.stateBadge.backgroundTintList =
            ContextCompat.getColorStateList(context, stateBackgroundColorRes(consulta.state))
        holder.binding.stateBadge.setTextColor(ContextCompat.getColor(context, stateTextColorRes(consulta.state)))
        holder.binding.rowContent.setOnClickListener { onClick(consulta) }
    }

    companion object {
        private val ODOO_FORMAT = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.US)
        private val DATE_FORMAT = SimpleDateFormat("dd/MM/yyyy", Locale.US)
        private val TIME_FORMAT = SimpleDateFormat("HH:mm", Locale.US)

        fun stateLabelRes(state: String): Int =
            if (state == "resuelta") R.string.consulta_state_resuelta else R.string.consulta_state_pendiente

        fun stateBackgroundColorRes(state: String): Int =
            if (state == "resuelta") R.color.color_neutral_200 else R.color.color_accent_100

        fun stateTextColorRes(state: String): Int =
            if (state == "resuelta") R.color.color_neutral_700 else R.color.color_accent_700

        fun formatRange(start: String, stop: String): String {
            val startDate = runCatching { ODOO_FORMAT.parse(start) }.getOrNull()
            val stopDate = runCatching { ODOO_FORMAT.parse(stop) }.getOrNull()
            if (startDate == null || stopDate == null) return "$start – $stop"
            return "${DATE_FORMAT.format(startDate)} · ${TIME_FORMAT.format(startDate)} – ${TIME_FORMAT.format(stopDate)}"
        }

        fun previewOf(transcript: String): String {
            val primeraLinea = transcript.lineSequence().firstOrNull { it.isNotBlank() }.orEmpty()
            return primeraLinea.ifBlank { "(sin transcripción)" }
        }
    }
}

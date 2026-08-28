package com.odooassistant.support.ui.inbox

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.core.content.ContextCompat
import androidx.core.os.bundleOf
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.LinearLayoutManager
import com.odooassistant.support.R
import com.odooassistant.support.data.RetrofitAssistantRepository
import com.odooassistant.support.databinding.FragmentInboxBinding
import com.odooassistant.support.model.Consulta
import com.odooassistant.support.ui.common.applyPressAnimation
import com.odooassistant.support.ui.common.slideNavOptions
import com.odooassistant.support.ui.login.LoginActivity
import kotlinx.coroutines.launch

/** Controlador de la pestaña Consultas: historial real de conversaciones cerradas del cliente. */
class InboxFragment : Fragment() {

    private var _binding: FragmentInboxBinding? = null
    private val binding get() = _binding!!

    private val repository = RetrofitAssistantRepository
    private lateinit var adapter: ConsultaAdapter

    private var todasLasConsultas: List<Consulta> = emptyList()
    private var filter = "pendiente"

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?,
    ): View {
        _binding = FragmentInboxBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.header.headerKicker.text = getString(R.string.inbox_kicker)
        binding.header.headerTitle.text = getString(R.string.inbox_title)
        binding.header.btnAvatar.visibility = View.VISIBLE
        binding.header.btnAvatar.setOnClickListener {
            com.odooassistant.support.config.SessionManager.clear()
            startActivity(android.content.Intent(requireContext(), LoginActivity::class.java))
        }

        adapter = ConsultaAdapter(emptyList()) { consulta -> openConsulta(consulta) }
        binding.recyclerConsultas.layoutManager = LinearLayoutManager(requireContext())
        binding.recyclerConsultas.adapter = adapter

        binding.filterPending.applyPressAnimation()
        binding.filterResolved.applyPressAnimation()
        binding.filterPending.setOnClickListener { setFilter("pendiente") }
        binding.filterResolved.setOnClickListener { setFilter("resuelta") }

        refresh()
    }

    override fun onResume() {
        super.onResume()
        refresh()
    }

    private fun setFilter(newFilter: String) {
        filter = newFilter
        applyFilter()
    }

    private fun refresh() {
        viewLifecycleOwner.lifecycleScope.launch {
            todasLasConsultas = repository.getConsultas().getOrElse {
                binding.idleMessage.text = getString(R.string.inbox_error)
                emptyList()
            }
            applyFilter()
        }
    }

    private fun applyFilter() {
        val pendingSelected = filter == "pendiente"
        styleFilter(binding.filterPending, pendingSelected)
        styleFilter(binding.filterResolved, !pendingSelected)

        val visibles = todasLasConsultas.filter { it.state == filter }
        if (visibles.isEmpty()) {
            binding.recyclerConsultas.visibility = View.GONE
            binding.idleContainer.visibility = View.VISIBLE
            binding.idleMessage.text = if (todasLasConsultas.isEmpty()) {
                getString(R.string.inbox_empty)
            } else {
                getString(R.string.inbox_empty_filtered)
            }
        } else {
            binding.idleContainer.visibility = View.GONE
            binding.recyclerConsultas.visibility = View.VISIBLE
            adapter.submitList(visibles)
        }
    }

    private fun styleFilter(view: android.widget.TextView, selected: Boolean) {
        if (selected) {
            view.setBackgroundResource(R.drawable.bg_pill_dark)
        } else {
            view.setBackgroundResource(android.R.color.transparent)
        }
        view.setTextColor(
            ContextCompat.getColor(requireContext(), if (selected) R.color.color_bg else R.color.color_neutral_700),
        )
    }

    private fun openConsulta(consulta: Consulta) {
        findNavController().navigate(
            R.id.consultaDetailFragment,
            bundleOf(
                "start" to consulta.start,
                "stop" to consulta.stop,
                "transcript" to consulta.transcript,
                "state" to consulta.state,
            ),
            slideNavOptions,
        )
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}

package com.odooassistant.support.ui.inbox

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.navigation.fragment.findNavController
import com.odooassistant.support.R
import com.odooassistant.support.databinding.FragmentConsultaDetailBinding

/** Muestra la transcripción completa de una consulta ya cerrada (datos recibidos por argumentos, sin red). */
class ConsultaDetailFragment : Fragment() {

    private var _binding: FragmentConsultaDetailBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?,
    ): View {
        _binding = FragmentConsultaDetailBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val start = requireArguments().getString("start").orEmpty()
        val stop = requireArguments().getString("stop").orEmpty()
        val transcript = requireArguments().getString("transcript").orEmpty()
        val state = requireArguments().getString("state").orEmpty()

        binding.header.headerKicker.text = getString(R.string.consulta_detail_kicker)
        binding.header.headerTitle.text = ConsultaAdapter.formatRange(start, stop)
        binding.header.btnBack.visibility = View.VISIBLE
        binding.header.btnBack.setOnClickListener { findNavController().popBackStack() }

        binding.stateBadge.text = getString(ConsultaAdapter.stateLabelRes(state))
        binding.stateBadge.backgroundTintList =
            ContextCompat.getColorStateList(requireContext(), ConsultaAdapter.stateBackgroundColorRes(state))
        binding.stateBadge.setTextColor(
            ContextCompat.getColor(requireContext(), ConsultaAdapter.stateTextColorRes(state)),
        )

        binding.transcript.text = transcript.ifBlank { getString(R.string.consulta_detail_empty) }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}

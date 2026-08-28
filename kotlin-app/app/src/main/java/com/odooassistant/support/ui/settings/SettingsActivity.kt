package com.odooassistant.support.ui.settings

import android.os.Bundle
import android.view.View
import androidx.appcompat.app.AppCompatActivity
import com.odooassistant.support.R
import com.odooassistant.support.config.AgentSettings
import com.odooassistant.support.databinding.ActivitySettingsBinding
import com.odooassistant.support.ui.common.applyNavigationBarBottomPadding
import com.odooassistant.support.ui.common.applyPressAnimation

/**
 * Permite cambiar a qué servidor del agente se conecta la app (útil para
 * pasar de un agente local en el emulador a uno real, o a otro entorno de
 * Odoo) sin tener que recompilar.
 */
class SettingsActivity : AppCompatActivity() {

    private lateinit var binding: ActivitySettingsBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivitySettingsBinding.inflate(layoutInflater)
        setContentView(binding.root)
        binding.root.applyNavigationBarBottomPadding()

        binding.inputBaseUrl.setText(AgentSettings.getBaseUrl())

        binding.btnBack.applyPressAnimation()
        binding.btnBack.setOnClickListener { closeWithTransition() }

        binding.btnSave.applyPressAnimation()
        binding.btnSave.setOnClickListener {
            val url = binding.inputBaseUrl.text?.toString()?.trim().orEmpty()
            if (url.isNotEmpty()) {
                AgentSettings.setBaseUrl(url)
                binding.inputBaseUrl.setText(AgentSettings.getBaseUrl())
                showSavedNote()
            }
        }

        binding.btnResetDefault.applyPressAnimation()
        binding.btnResetDefault.setOnClickListener {
            AgentSettings.resetToDefault()
            binding.inputBaseUrl.setText(AgentSettings.getBaseUrl())
            showSavedNote()
        }
    }

    private fun closeWithTransition() {
        finish()
        @Suppress("DEPRECATION")
        overridePendingTransition(R.anim.activity_fade_in, R.anim.activity_fade_out)
    }

    private fun showSavedNote() {
        binding.textSavedNote.visibility = View.VISIBLE
        binding.textSavedNote.postDelayed({ binding.textSavedNote.visibility = View.INVISIBLE }, 2000)
    }
}

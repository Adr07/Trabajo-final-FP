package com.odooassistant.support.ui.login

import android.content.Intent
import android.os.Bundle
import android.view.View
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.odooassistant.support.R
import com.odooassistant.support.data.RetrofitAssistantRepository
import com.odooassistant.support.databinding.ActivityLoginBinding
import com.odooassistant.support.ui.common.applyNavigationBarBottomPadding
import com.odooassistant.support.ui.common.applyPressAnimation
import com.odooassistant.support.ui.main.MainActivity
import com.odooassistant.support.ui.settings.SettingsActivity
import kotlinx.coroutines.launch

/** Controlador de la pantalla de acceso: login real de cliente contra Odoo (usuario Portal). */
class LoginActivity : AppCompatActivity() {

    private lateinit var binding: ActivityLoginBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityLoginBinding.inflate(layoutInflater)
        setContentView(binding.root)
        binding.root.applyNavigationBarBottomPadding()

        binding.btnEnter.applyPressAnimation()
        binding.btnEnter.setOnClickListener { attemptLogin() }

        binding.btnOpenSettings.setOnClickListener {
            startActivity(Intent(this, SettingsActivity::class.java))
            @Suppress("DEPRECATION")
            overridePendingTransition(R.anim.activity_fade_in, R.anim.activity_fade_out)
        }
    }

    private fun attemptLogin() {
        val email = binding.inputEmail.text?.toString()?.trim().orEmpty()
        val password = binding.inputPassword.text?.toString().orEmpty()

        if (email.isEmpty() || password.isEmpty()) {
            showError(getString(R.string.login_error_generic))
            return
        }

        binding.btnEnter.isEnabled = false
        binding.textLoginError.visibility = View.GONE

        lifecycleScope.launch {
            val resultado = RetrofitAssistantRepository.login(email, password)
            binding.btnEnter.isEnabled = true

            resultado.onSuccess {
                startActivity(Intent(this@LoginActivity, MainActivity::class.java))
                @Suppress("DEPRECATION")
                overridePendingTransition(R.anim.activity_fade_in, R.anim.activity_fade_out)
                finish()
            }.onFailure { error ->
                showError(error.message ?: getString(R.string.login_error_generic))
            }
        }
    }

    private fun showError(message: String) {
        binding.textLoginError.text = message
        binding.textLoginError.visibility = View.VISIBLE
    }
}

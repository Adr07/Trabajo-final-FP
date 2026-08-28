package com.odooassistant.support.ui.main

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.Fragment
import androidx.navigation.fragment.NavHostFragment
import androidx.navigation.fragment.findNavController
import com.odooassistant.support.R
import com.odooassistant.support.databinding.ActivityMainBinding
import com.odooassistant.support.ui.common.applyNavigationBarBottomPadding
import com.odooassistant.support.ui.common.fadeTabNavOptions

/** Host de la navegación por tabs: Chat y Consultas. */
class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        binding.bottomNav.applyNavigationBarBottomPadding()

        val navHostFragment = supportFragmentManager
            .findFragmentById(R.id.navHostFragment) as NavHostFragment
        val navController = navHostFragment.navController

        // No usamos NavigationUI.setupWithNavController: así podemos aplicar
        // nuestra propia animación de fundido al cambiar de pestaña en vez
        // del corte instantáneo por defecto.
        binding.bottomNav.setOnItemSelectedListener { item ->
            navController.navigate(item.itemId, null, fadeTabNavOptions(navController))
            true
        }
        navController.addOnDestinationChangedListener { _, destination, _ ->
            binding.bottomNav.menu.findItem(destination.id)?.isChecked = true
        }
    }
}

/** Extensión compartida por los fragments para navegar "a una pestaña", limpiando lo que haya encima. */
fun Fragment.goToTab(destinationId: Int) {
    val navController = findNavController()
    if (!navController.popBackStack(destinationId, false)) {
        navController.navigate(destinationId, null, fadeTabNavOptions(navController))
    }
}

package com.odooassistant.support.ui.common

import android.view.View
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.updatePadding

/**
 * El proyecto compila con targetSdk 36, que fuerza el modo "edge-to-edge":
 * el contenido se dibuja por detrás de las barras del sistema (barra de
 * estado, barra de navegación) a menos que cada pantalla le deje el espacio
 * explícitamente. Sin esto, la fila inferior de cualquier layout que llegue
 * hasta el borde de la pantalla queda tapada por la barra de navegación.
 *
 * Añade el alto real de la barra de navegación como padding inferior extra
 * (sumado al que ya tuviera la vista), respetando el padding original si el
 * dispositivo cambia de orientación o de barra de navegación.
 */
fun View.applyNavigationBarBottomPadding() {
    val initialPaddingBottom = paddingBottom
    ViewCompat.setOnApplyWindowInsetsListener(this) { view, insets ->
        val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
        view.updatePadding(bottom = initialPaddingBottom + systemBars.bottom)
        insets
    }
}

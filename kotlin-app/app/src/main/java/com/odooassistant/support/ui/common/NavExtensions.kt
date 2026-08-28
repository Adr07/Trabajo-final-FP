package com.odooassistant.support.ui.common

import androidx.navigation.NavController
import androidx.navigation.NavOptions
import com.odooassistant.support.R

/**
 * [NavOptions] compartidas para que todas las navegaciones "hacia adelante"
 * (Consultas→detalle de consulta) usen la misma transición deslizante con
 * desaceleración ("ease out"), en vez del corte instantáneo por defecto de
 * Navigation Component.
 */
val slideNavOptions: NavOptions = NavOptions.Builder()
    .setEnterAnim(R.anim.nav_enter)
    .setExitAnim(R.anim.nav_exit)
    .setPopEnterAnim(R.anim.nav_pop_enter)
    .setPopExitAnim(R.anim.nav_pop_exit)
    .build()

/**
 * NavOptions para el cambio de pestañas del bottom nav: fundido en vez de
 * deslizamiento (las pestañas no forman una pila), conservando el estado de
 * cada una (patrón estándar de BottomNavigationView + Navigation Component).
 */
fun fadeTabNavOptions(navController: NavController): NavOptions =
    NavOptions.Builder()
        .setLaunchSingleTop(true)
        .setRestoreState(true)
        .setPopUpTo(navController.graph.startDestinationId, inclusive = false, saveState = true)
        .setEnterAnim(R.anim.tab_fade_in)
        .setExitAnim(R.anim.tab_fade_out)
        .setPopEnterAnim(R.anim.tab_fade_in)
        .setPopExitAnim(R.anim.tab_fade_out)
        .build()

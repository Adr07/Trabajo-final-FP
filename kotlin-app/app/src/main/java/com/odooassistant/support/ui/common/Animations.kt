package com.odooassistant.support.ui.common

import android.animation.Animator
import android.animation.ObjectAnimator
import android.view.MotionEvent
import android.view.View
import android.view.animation.DecelerateInterpolator

private const val BOUNCE_HEIGHT_DP = 6f
private const val BOUNCE_DURATION_MS = 350L
private const val BOUNCE_STAGGER_MS = 130L

/**
 * Arranca la animación de "escribiendo…" (los 3 puntos que rebotan en
 * cascada, como en las apps de mensajería). Devuelve los animators activos
 * para poder cancelarlos con [stopTyping] cuando llega la respuesta real.
 */
fun startTyping(dots: List<View>): List<Animator> {
    val density = dots.firstOrNull()?.resources?.displayMetrics?.density ?: 1f
    val distance = -BOUNCE_HEIGHT_DP * density

    return dots.mapIndexed { index, dot ->
        dot.translationY = 0f
        ObjectAnimator.ofFloat(dot, View.TRANSLATION_Y, 0f, distance, 0f).apply {
            duration = BOUNCE_DURATION_MS * 2
            startDelay = index * BOUNCE_STAGGER_MS
            repeatCount = ObjectAnimator.INFINITE
            interpolator = DecelerateInterpolator()
            start()
        }
    }
}

fun stopTyping(animators: List<Animator>) {
    animators.forEach { it.cancel() }
}

/**
 * Feedback táctil "ease out" para cualquier vista clicable: un ligero
 * encogimiento al presionar y una vuelta suave al soltar. Se aplica además
 * del click listener normal — no lo reemplaza.
 */
fun View.applyPressAnimation() {
    setOnTouchListener { view, event ->
        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                view.animate()
                    .scaleX(0.96f)
                    .scaleY(0.96f)
                    .setDuration(120)
                    .setInterpolator(DecelerateInterpolator())
                    .start()
            }
            MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                view.animate()
                    .scaleX(1f)
                    .scaleY(1f)
                    .setDuration(180)
                    .setInterpolator(DecelerateInterpolator())
                    .start()
            }
        }
        false // no consumir el evento: el click listener normal sigue funcionando
    }
}

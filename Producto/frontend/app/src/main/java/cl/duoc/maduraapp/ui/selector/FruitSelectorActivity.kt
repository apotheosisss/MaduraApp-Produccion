package cl.duoc.maduraapp.ui.selector

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import cl.duoc.maduraapp.MainActivity
import cl.duoc.maduraapp.databinding.ActivityFruitSelectorBinding

/**
 * Pantalla inicial — el usuario elige qué fruta va a escanear antes de
 * abrir la cámara. Esto le pasa un filtro al backend que solo considera
 * predicciones de esa fruta, mejorando drásticamente la precisión.
 */
class FruitSelectorActivity : AppCompatActivity() {

    private lateinit var binding: ActivityFruitSelectorBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityFruitSelectorBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setSupportActionBar(binding.toolbar)

        // Cada card lanza MainActivity con el fruit_type como extra
        binding.cardAguacate.setOnClickListener { openScanner(FRUIT_AGUACATE) }
        binding.cardPlatano.setOnClickListener  { openScanner(FRUIT_PLATANO) }
        binding.cardTomate.setOnClickListener   { openScanner(FRUIT_TOMATE) }
        binding.cardMango.setOnClickListener    { openScanner(FRUIT_MANGO) }
    }

    private fun openScanner(fruitType: String) {
        startActivity(
            Intent(this, MainActivity::class.java).apply {
                putExtra(EXTRA_FRUIT_TYPE, fruitType)
            }
        )
    }

    companion object {
        /** Extra clave que pasa el fruit_type a [MainActivity]. */
        const val EXTRA_FRUIT_TYPE = "fruit_type"

        // Valores que espera el backend en el endpoint POST /v1/predict
        const val FRUIT_AGUACATE = "aguacate_hass"
        const val FRUIT_PLATANO  = "platano"
        const val FRUIT_TOMATE   = "tomate_usda"
        const val FRUIT_MANGO    = "mango"
    }
}

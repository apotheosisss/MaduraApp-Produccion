package cl.duoc.maduraapp.ui.feedback

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.lifecycle.lifecycleScope
import cl.duoc.maduraapp.data.api.ApiClient
import cl.duoc.maduraapp.data.dto.FeedbackRequestDto
import cl.duoc.maduraapp.databinding.FragmentRatingBottomSheetBinding
import com.google.android.material.bottomsheet.BottomSheetDialogFragment
import kotlinx.coroutines.launch

/**
 * Bottom sheet que aparece después de un escaneo exitoso para recoger
 * la calificación del usuario (1-5 estrellas).
 *
 * Los datos se envían al backend para mejorar el modelo en futuras
 * iteraciones de entrenamiento.
 *
 * Uso:
 * ```kotlin
 * RatingBottomSheet.newInstance(scanId).show(supportFragmentManager, RatingBottomSheet.TAG)
 * ```
 */
class RatingBottomSheet : BottomSheetDialogFragment() {

    private var _binding: FragmentRatingBottomSheetBinding? = null
    private val binding get() = _binding!!

    private lateinit var scanId: String

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        scanId = arguments?.getString(ARG_SCAN_ID)
            ?: error("RatingBottomSheet requires scan_id argument")
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?,
    ): View {
        _binding = FragmentRatingBottomSheetBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        // Habilitar el botón solo cuando el usuario elige una estrella
        binding.ratingBar.setOnRatingBarChangeListener { _, rating, _ ->
            binding.btnSubmitRating.isEnabled = rating >= 1f
        }

        binding.btnSkip.setOnClickListener { dismiss() }

        binding.btnSubmitRating.setOnClickListener {
            val rating = binding.ratingBar.rating.toInt()
            submitFeedback(rating)
        }
    }

    private fun submitFeedback(rating: Int) {
        binding.btnSubmitRating.isEnabled = false
        binding.btnSkip.isEnabled = false

        lifecycleScope.launch {
            runCatching {
                ApiClient.service.submitFeedback(
                    FeedbackRequestDto(scanId = scanId, rating = rating)
                )
            }.onSuccess {
                Toast.makeText(requireContext(), "¡Gracias por tu feedback! 🌟", Toast.LENGTH_SHORT).show()
                dismiss()
            }.onFailure {
                // Si falla el envío, no bloquear al usuario
                Toast.makeText(requireContext(), "No se pudo enviar el feedback.", Toast.LENGTH_SHORT).show()
                dismiss()
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }

    companion object {
        const val TAG = "RatingBottomSheet"
        private const val ARG_SCAN_ID = "scan_id"

        fun newInstance(scanId: String): RatingBottomSheet =
            RatingBottomSheet().apply {
                arguments = Bundle().apply { putString(ARG_SCAN_ID, scanId) }
            }
    }
}

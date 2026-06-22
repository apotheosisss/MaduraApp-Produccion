package cl.duoc.maduraapp.data.dto

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class FeedbackRequestDto(
    @SerialName("scan_id") val scanId: String,
    val rating: Int,
)

@Serializable
data class FeedbackResponseDto(
    val success: Boolean,
    @SerialName("feedback_id") val feedbackId: Int,
    val message: String = "¡Gracias por tu feedback!",
)

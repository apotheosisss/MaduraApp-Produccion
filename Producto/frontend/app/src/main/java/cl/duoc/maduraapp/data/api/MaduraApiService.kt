package cl.duoc.maduraapp.data.api

import cl.duoc.maduraapp.data.dto.AuthResponseDto
import cl.duoc.maduraapp.data.dto.FeedbackRequestDto
import cl.duoc.maduraapp.data.dto.FeedbackResponseDto
import cl.duoc.maduraapp.data.dto.HistoryResponseDto
import cl.duoc.maduraapp.data.dto.LoginRequestDto
import cl.duoc.maduraapp.data.dto.PredictResponseDto
import cl.duoc.maduraapp.data.dto.RegisterRequestDto
import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part
import retrofit2.http.Query

/**
 * Cliente Retrofit del backend FastAPI.
 *
 * El token JWT se agrega automáticamente en cada request via [AuthInterceptor].
 * No es necesario pasarlo manualmente en cada llamada.
 */
interface MaduraApiService {

    // ── Autenticación ──────────────────────────────────────────────────────────

    @POST("v1/auth/register")
    suspend fun register(@Body body: RegisterRequestDto): AuthResponseDto

    @POST("v1/auth/login")
    suspend fun login(@Body body: LoginRequestDto): AuthResponseDto

    // ── Inferencia ─────────────────────────────────────────────────────────────

    @Multipart
    @POST("v1/predict")
    suspend fun predict(
        @Part file: MultipartBody.Part,
        @Part("fruit_type") fruitType: RequestBody? = null,
    ): PredictResponseDto

    // ── Historial ──────────────────────────────────────────────────────────────

    @GET("v1/history")
    suspend fun history(
        @Query("limit") limit: Int = 50,
        @Query("offset") offset: Int = 0,
    ): HistoryResponseDto

    // ── Feedback ───────────────────────────────────────────────────────────────

    @POST("v1/feedback")
    suspend fun submitFeedback(@Body body: FeedbackRequestDto): FeedbackResponseDto

    // ── Health ─────────────────────────────────────────────────────────────────

    @GET("v1/health")
    suspend fun health(): Map<String, Any>
}

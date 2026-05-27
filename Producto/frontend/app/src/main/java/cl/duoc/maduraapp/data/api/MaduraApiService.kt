package cl.duoc.maduraapp.data.api

import cl.duoc.maduraapp.data.dto.HistoryResponseDto
import cl.duoc.maduraapp.data.dto.PredictResponseDto
import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part
import retrofit2.http.Query

/**
 * Cliente Retrofit del backend FastAPI.
 *
 * Endpoints:
 *  - POST /v1/predict   → multipart/form-data (file + fruit_type opcional)
 *  - GET  /v1/history   → list paginado del usuario autenticado
 *  - GET  /v1/health    → ping del servicio
 */
interface MaduraApiService {

    @Multipart
    @POST("v1/predict")
    suspend fun predict(
        @Part file: MultipartBody.Part,
        @Part("fruit_type") fruitType: RequestBody? = null,
        @Header("Authorization") bearerToken: String? = null,
    ): PredictResponseDto

    @GET("v1/history")
    suspend fun history(
        @Query("limit") limit: Int = 50,
        @Query("offset") offset: Int = 0,
        @Header("Authorization") bearerToken: String? = null,
    ): HistoryResponseDto

    @GET("v1/health")
    suspend fun health(): Map<String, Any>
}

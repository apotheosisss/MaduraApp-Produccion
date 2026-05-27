package cl.duoc.maduraapp.data.repository

import cl.duoc.maduraapp.MaduraApp
import cl.duoc.maduraapp.data.api.ApiClient
import cl.duoc.maduraapp.data.api.MaduraApiService
import cl.duoc.maduraapp.data.dto.HistoryResponseDto
import cl.duoc.maduraapp.data.dto.PredictResponseDto
import cl.duoc.maduraapp.data.dto.ScanResultDto
import cl.duoc.maduraapp.data.local.LocalScanDataSource
import kotlinx.coroutines.flow.Flow
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.MultipartBody.Companion.FORM

/**
 * Capa de repositorio: encapsula el acceso a la API y al cache local Room.
 *
 * El token JWT se agrega automáticamente via [AuthInterceptor] — no es
 * necesario pasarlo explícitamente en ningún método.
 *
 * Estrategia:
 *  - El backend es la fuente de verdad del historial.
 *  - Tras una predicción exitosa el resultado se cachea en Room para historial offline.
 */
class FruitRepository(
    private val api: MaduraApiService = ApiClient.service,
    private val local: LocalScanDataSource = LocalScanDataSource(MaduraApp.get().scanDao),
) {

    // ------------------------------------------------------------------ Predict

    suspend fun predict(
        imageBytes: ByteArray,
        fruitType: String? = null,
    ): Result<PredictResponseDto> = runCatching {
        val mediaType = "image/jpeg".toMediaTypeOrNull()
        val requestBody = imageBytes.toRequestBody(mediaType)
        val part = MultipartBody.Part.createFormData(
            name = "file",
            filename = "scan.jpg",
            body = requestBody,
        )
        val fruitTypeBody = fruitType?.toRequestBody(FORM)

        val response = api.predict(part, fruitTypeBody)

        // Cachear localmente solo si hubo detección
        response.data?.let { local.cache(it) }

        response
    }

    // ----------------------------------------------------------------- History

    suspend fun refreshHistory(
        limit: Int = 50,
        offset: Int = 0,
    ): Result<HistoryResponseDto> = runCatching {
        val response = api.history(limit, offset)

        if (offset == 0) {
            local.clear()
            response.items.forEach { local.cache(it) }
        }

        response
    }

    /** Stream reactivo del cache local. */
    fun observeLocalHistory(limit: Int = 50): Flow<List<ScanResultDto>> =
        local.observeRecent(limit)

    suspend fun localHistoryCount(): Int = local.count()

    // ------------------------------------------------------------------- Health

    suspend fun isBackendHealthy(): Boolean = runCatching {
        val response = api.health()
        response["status"] == "ok"
    }.getOrDefault(false)
}

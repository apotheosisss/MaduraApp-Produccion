package cl.duoc.maduraapp.ui

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import cl.duoc.maduraapp.data.repository.FruitRepository
import kotlinx.coroutines.launch

/**
 * ViewModel del flujo principal de escaneo.
 *
 * Responsabilidades:
 *  - Disparar la inferencia contra el backend cuando llegan bytes desde CameraX
 *    o desde la galería.
 *  - Pasar el `fruitType` seleccionado al backend para filtrar predicciones
 *    a esa fruta (mejora precisión vs el modo libre).
 *  - Exponer un único [LiveData] de [ScanState] para que la Activity actualice
 *    el semáforo de madurez sin lógica de negocio.
 */
class ScanViewModel(
    private val repository: FruitRepository = FruitRepository(),
) : ViewModel() {

    private val _state = MutableLiveData<ScanState>(ScanState.Idle)
    val state: LiveData<ScanState> = _state

    /**
     * Fruta seleccionada en la pantalla inicial (FruitSelectorActivity).
     * Si es null, el backend predice entre las 12 clases libres.
     */
    var fruitType: String? = null

    /** Reinicia la UI tras un escaneo (botón "Volver a escanear"). */
    fun reset() {
        _state.value = ScanState.Idle
    }

    /** Envía la imagen al backend y publica el resultado. */
    fun submitImage(imageBytes: ByteArray, bearerToken: String? = null) {
        _state.value = ScanState.Loading

        viewModelScope.launch {
            repository.predict(
                imageBytes = imageBytes,
                fruitType = fruitType,
                bearerToken = bearerToken,
            )
                .onSuccess { response ->
                    _state.value = when {
                        response.success && response.data != null ->
                            ScanState.Success(response.data)

                        else ->
                            ScanState.NoDetection(
                                response.error ?: "No se detectó ninguna fruta soportada"
                            )
                    }
                }
                .onFailure { throwable ->
                    _state.value = ScanState.Error(throwable)
                }
        }
    }
}

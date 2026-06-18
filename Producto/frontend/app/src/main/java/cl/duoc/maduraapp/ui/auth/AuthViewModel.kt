package cl.duoc.maduraapp.ui.auth

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import cl.duoc.maduraapp.MaduraApp
import cl.duoc.maduraapp.data.auth.AuthPreferences
import cl.duoc.maduraapp.data.auth.AuthRepository
import kotlinx.coroutines.launch

class AuthViewModel(
    private val repository: AuthRepository = AuthRepository(
        AuthPreferences(MaduraApp.get())
    ),
) : ViewModel() {

    private val _state = MutableLiveData<AuthState>(AuthState.Idle)
    val state: LiveData<AuthState> = _state

    fun login(email: String, password: String) {
        if (email.isBlank() || password.isBlank()) {
            _state.value = AuthState.Error("Completa todos los campos.")
            return
        }
        _state.value = AuthState.Loading
        viewModelScope.launch {
            repository.login(email.trim(), password)
                .onSuccess { resp ->
                    _state.value = AuthState.Success(resp.username)
                }
                .onFailure { e ->
                    _state.value = AuthState.Error(friendlyError(e.message))
                }
        }
    }

    fun register(username: String, email: String, password: String, confirmPassword: String) {
        when {
            username.isBlank() || email.isBlank() || password.isBlank() ->
                _state.value = AuthState.Error("Completa todos los campos.")
            password != confirmPassword ->
                _state.value = AuthState.Error("Las contraseñas no coinciden.")
            password.length < 8 ->
                _state.value = AuthState.Error("La contraseña debe tener al menos 8 caracteres.")
            !password.any { it.isLetter() } || !password.any { it.isDigit() } ->
                _state.value = AuthState.Error("La contraseña debe incluir letras y números.")
            else -> {
                _state.value = AuthState.Loading
                viewModelScope.launch {
                    repository.register(username.trim(), email.trim(), password)
                        .onSuccess { resp ->
                            _state.value = AuthState.Success(resp.username)
                        }
                        .onFailure { e ->
                            _state.value = AuthState.Error(friendlyError(e.message))
                        }
                }
            }
        }
    }

    fun reset() { _state.value = AuthState.Idle }

    private fun friendlyError(raw: String?): String = when {
        raw == null -> "Error desconocido."
        "409" in raw || "en uso" in raw || "registrado" in raw ->
            "El usuario o correo ya están registrados."
        "401" in raw || "Credenciales" in raw ->
            "Correo o contraseña incorrectos."
        "connect" in raw.lowercase() || "timeout" in raw.lowercase() ->
            "No se pudo conectar al servidor. Verifica tu internet."
        else -> "Error: $raw"
    }
}

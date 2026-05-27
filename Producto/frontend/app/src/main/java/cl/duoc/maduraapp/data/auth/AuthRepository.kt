package cl.duoc.maduraapp.data.auth

import cl.duoc.maduraapp.data.api.ApiClient
import cl.duoc.maduraapp.data.dto.AuthResponseDto
import cl.duoc.maduraapp.data.dto.LoginRequestDto
import cl.duoc.maduraapp.data.dto.RegisterRequestDto

/**
 * Repositorio de autenticación.
 * Gestiona register/login/logout manteniendo sincronizados [TokenManager] y [AuthPreferences].
 */
class AuthRepository(
    private val authPrefs: AuthPreferences,
    private val api: cl.duoc.maduraapp.data.api.MaduraApiService = ApiClient.service,
) {

    suspend fun register(username: String, email: String, password: String): Result<AuthResponseDto> =
        runCatching {
            val response = api.register(RegisterRequestDto(username, email, password))
            authPrefs.saveSession(response.accessToken, response.userId, response.username)
            response
        }

    suspend fun login(email: String, password: String): Result<AuthResponseDto> =
        runCatching {
            val response = api.login(LoginRequestDto(email, password))
            authPrefs.saveSession(response.accessToken, response.userId, response.username)
            response
        }

    suspend fun logout() {
        authPrefs.clearSession()
    }

    /** Intenta restaurar la sesión desde el disco. True si había una guardada. */
    suspend fun restoreSession(): Boolean = authPrefs.loadSession()
}

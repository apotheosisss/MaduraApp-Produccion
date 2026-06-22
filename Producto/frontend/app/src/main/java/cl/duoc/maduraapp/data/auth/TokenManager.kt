package cl.duoc.maduraapp.data.auth

/**
 * Singleton en memoria que guarda el JWT activo durante la sesión.
 *
 * La persistencia en disco es manejada por [AuthPreferences].
 * Al arrancar la app, [MaduraApp] carga el token guardado en este manager.
 */
object TokenManager {

    @Volatile
    private var _token: String? = null

    @Volatile
    private var _userId: String? = null

    @Volatile
    private var _username: String? = null

    val token: String? get() = _token
    val userId: String? get() = _userId
    val username: String? get() = _username

    val isLoggedIn: Boolean get() = _token != null

    fun saveSession(token: String, userId: String, username: String) {
        _token = token
        _userId = userId
        _username = username
    }

    fun clearSession() {
        _token = null
        _userId = null
        _username = null
    }
}

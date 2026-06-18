package cl.duoc.maduraapp.data.auth

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * Persistencia **cifrada** de la sesión JWT entre cierres de la app.
 *
 * Usa [EncryptedSharedPreferences] (AES-256): tanto las claves como los valores
 * se cifran con una clave maestra resguardada en el Android Keystore. El token
 * y los datos de sesión quedan ilegibles en reposo aunque alguien extraiga el
 * archivo del dispositivo (OWASP M9 / A02 — protección de datos en reposo).
 *
 * La API pública (suspend) se mantiene idéntica a la versión anterior basada en
 * DataStore, por lo que los consumidores no requieren cambios.
 */
class AuthPreferences(context: Context) {

    private val prefs: SharedPreferences by lazy {
        val appContext = context.applicationContext
        val masterKey = MasterKey.Builder(appContext)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()
        EncryptedSharedPreferences.create(
            appContext,
            PREFS_NAME,
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM,
        )
    }

    /** Carga la sesión guardada y la pone en [TokenManager]. True si había sesión. */
    suspend fun loadSession(): Boolean = withContext(Dispatchers.IO) {
        val token = prefs.getString(KEY_TOKEN, null)
        val userId = prefs.getString(KEY_USER_ID, null)
        val username = prefs.getString(KEY_USERNAME, null)

        if (token != null && userId != null && username != null) {
            TokenManager.saveSession(token, userId, username)
            true
        } else {
            false
        }
    }

    suspend fun saveSession(token: String, userId: String, username: String) {
        withContext(Dispatchers.IO) {
            prefs.edit()
                .putString(KEY_TOKEN, token)
                .putString(KEY_USER_ID, userId)
                .putString(KEY_USERNAME, username)
                .apply()
        }
        TokenManager.saveSession(token, userId, username)
    }

    suspend fun clearSession() {
        withContext(Dispatchers.IO) {
            prefs.edit().clear().apply()
        }
        TokenManager.clearSession()
    }

    private companion object {
        const val PREFS_NAME = "auth_prefs_secure"
        const val KEY_TOKEN = "jwt_token"
        const val KEY_USER_ID = "user_id"
        const val KEY_USERNAME = "username"
    }
}

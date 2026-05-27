package cl.duoc.maduraapp.data.auth

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map

/** DataStore para persistir la sesión entre cierres de app. */
private val Context.authDataStore: DataStore<Preferences> by preferencesDataStore(name = "auth_prefs")

class AuthPreferences(private val context: Context) {

    private object Keys {
        val TOKEN    = stringPreferencesKey("jwt_token")
        val USER_ID  = stringPreferencesKey("user_id")
        val USERNAME = stringPreferencesKey("username")
    }

    /** Carga la sesión guardada y la pone en [TokenManager]. True si había sesión. */
    suspend fun loadSession(): Boolean {
        val prefs = context.authDataStore.data.first()
        val token    = prefs[Keys.TOKEN]
        val userId   = prefs[Keys.USER_ID]
        val username = prefs[Keys.USERNAME]

        return if (token != null && userId != null && username != null) {
            TokenManager.saveSession(token, userId, username)
            true
        } else {
            false
        }
    }

    suspend fun saveSession(token: String, userId: String, username: String) {
        context.authDataStore.edit { prefs ->
            prefs[Keys.TOKEN]    = token
            prefs[Keys.USER_ID]  = userId
            prefs[Keys.USERNAME] = username
        }
        TokenManager.saveSession(token, userId, username)
    }

    suspend fun clearSession() {
        context.authDataStore.edit { it.clear() }
        TokenManager.clearSession()
    }
}

package cl.duoc.maduraapp

import android.app.Application
import cl.duoc.maduraapp.data.auth.AuthPreferences
import cl.duoc.maduraapp.data.local.MaduraDatabase
import cl.duoc.maduraapp.data.local.ScanDao
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch

/**
 * Application class — punto de inicialización temprana.
 *
 * Al arrancar carga la sesión JWT desde DataStore para que [TokenManager]
 * tenga el token disponible antes de que cualquier Activity haga requests.
 */
class MaduraApp : Application() {

    val scanDao: ScanDao by lazy { MaduraDatabase.get(this).scanDao() }

    // Scope para operaciones de inicialización (DataStore es async)
    private val appScope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    override fun onCreate() {
        super.onCreate()
        instance = this

        // Pre-cargar el token en memoria para que el AuthInterceptor lo encuentre
        appScope.launch {
            AuthPreferences(this@MaduraApp).loadSession()
        }
    }

    companion object {
        @Volatile
        private var instance: MaduraApp? = null

        fun get(): MaduraApp =
            instance ?: error("MaduraApp todavía no se ha inicializado")
    }
}

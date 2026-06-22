package cl.duoc.maduraapp.ui.auth

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.view.inputmethod.EditorInfo
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import cl.duoc.maduraapp.MaduraApp
import cl.duoc.maduraapp.data.auth.AuthPreferences
import cl.duoc.maduraapp.data.auth.TokenManager
import cl.duoc.maduraapp.databinding.ActivityLoginBinding
import cl.duoc.maduraapp.ui.selector.FruitSelectorActivity
import kotlinx.coroutines.launch

/**
 * Pantalla inicial de autenticación.
 *
 * Flujo de arranque:
 *  1. Si hay token guardado en DataStore → redirige directamente a FruitSelectorActivity.
 *  2. Si no hay token → muestra el formulario de login.
 */
class LoginActivity : AppCompatActivity() {

    private lateinit var binding: ActivityLoginBinding
    private val viewModel: AuthViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityLoginBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Intentar restaurar sesión guardada antes de mostrar el formulario
        lifecycleScope.launch {
            val restored = AuthPreferences(MaduraApp.get()).loadSession()
            if (restored && TokenManager.isLoggedIn) {
                goToApp()
                return@launch
            }
            setupUI()
        }
    }

    private fun setupUI() {
        // Teclado: Enter en contraseña → lanzar login
        binding.etPassword.setOnEditorActionListener { _, actionId, _ ->
            if (actionId == EditorInfo.IME_ACTION_DONE) {
                submitLogin()
                true
            } else false
        }

        binding.btnLogin.setOnClickListener { submitLogin() }

        binding.tvGoRegister.setOnClickListener {
            startActivity(Intent(this, RegisterActivity::class.java))
        }

        viewModel.state.observe(this) { state ->
            when (state) {
                is AuthState.Idle -> renderIdle()
                is AuthState.Loading -> renderLoading()
                is AuthState.Success -> goToApp()
                is AuthState.Error -> renderError(state.message)
            }
        }
    }

    private fun submitLogin() {
        val email = binding.etEmail.text?.toString().orEmpty()
        val pass  = binding.etPassword.text?.toString().orEmpty()
        viewModel.login(email, pass)
    }

    private fun renderIdle() = with(binding) {
        progressBar.visibility = View.GONE
        btnLogin.isEnabled = true
        tvError.visibility = View.GONE
    }

    private fun renderLoading() = with(binding) {
        progressBar.visibility = View.VISIBLE
        btnLogin.isEnabled = false
        tvError.visibility = View.GONE
    }

    private fun renderError(message: String) = with(binding) {
        progressBar.visibility = View.GONE
        btnLogin.isEnabled = true
        tvError.text = message
        tvError.visibility = View.VISIBLE
    }

    private fun goToApp() {
        startActivity(Intent(this, FruitSelectorActivity::class.java))
        finish()
    }
}

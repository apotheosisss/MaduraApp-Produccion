package cl.duoc.maduraapp.ui.auth

import android.content.Intent
import android.os.Bundle
import android.view.View
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import cl.duoc.maduraapp.databinding.ActivityRegisterBinding
import cl.duoc.maduraapp.ui.selector.FruitSelectorActivity

/**
 * Pantalla de registro de nuevo usuario.
 * Tras un registro exitoso, navega directo a FruitSelectorActivity.
 */
class RegisterActivity : AppCompatActivity() {

    private lateinit var binding: ActivityRegisterBinding
    private val viewModel: AuthViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityRegisterBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setSupportActionBar(binding.toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        supportActionBar?.title = ""

        binding.btnRegister.setOnClickListener {
            val username        = binding.etUsername.text?.toString().orEmpty()
            val email           = binding.etEmail.text?.toString().orEmpty()
            val password        = binding.etPassword.text?.toString().orEmpty()
            val confirmPassword = binding.etConfirmPassword.text?.toString().orEmpty()
            viewModel.register(username, email, password, confirmPassword)
        }

        viewModel.state.observe(this) { state ->
            when (state) {
                is AuthState.Idle    -> renderIdle()
                is AuthState.Loading -> renderLoading()
                is AuthState.Success -> goToApp()
                is AuthState.Error   -> renderError(state.message)
            }
        }
    }

    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }

    private fun renderIdle() = with(binding) {
        progressBar.visibility = View.GONE
        btnRegister.isEnabled = true
        tvError.visibility = View.GONE
    }

    private fun renderLoading() = with(binding) {
        progressBar.visibility = View.VISIBLE
        btnRegister.isEnabled = false
        tvError.visibility = View.GONE
    }

    private fun renderError(message: String) = with(binding) {
        progressBar.visibility = View.GONE
        btnRegister.isEnabled = true
        tvError.text = message
        tvError.visibility = View.VISIBLE
    }

    private fun goToApp() {
        startActivity(
            Intent(this, FruitSelectorActivity::class.java)
                .addFlags(Intent.FLAG_ACTIVITY_CLEAR_TASK or Intent.FLAG_ACTIVITY_NEW_TASK)
        )
        finish()
    }
}

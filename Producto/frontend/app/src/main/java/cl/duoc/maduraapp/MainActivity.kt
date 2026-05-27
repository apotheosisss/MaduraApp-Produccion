package cl.duoc.maduraapp

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Matrix
import android.net.Uri
import android.os.Bundle
import android.util.Log
import android.view.Menu
import android.view.MenuItem
import android.view.View
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageCaptureException
import androidx.camera.core.ImageProxy
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.core.content.ContextCompat
import cl.duoc.maduraapp.data.dto.ScanResultDto
import cl.duoc.maduraapp.databinding.ActivityMainBinding
import cl.duoc.maduraapp.ui.ScanState
import cl.duoc.maduraapp.ui.ScanViewModel
import cl.duoc.maduraapp.ui.history.HistoryActivity
import cl.duoc.maduraapp.ui.selector.FruitSelectorActivity
import java.io.ByteArrayOutputStream
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

/**
 * Activity principal: permite capturar una imagen con la cámara o seleccionar
 * una desde la galería, y delega al [ScanViewModel] para enviarla al backend.
 */
class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val viewModel: ScanViewModel by viewModels()

    private var imageCapture: ImageCapture? = null
    private lateinit var cameraExecutor: ExecutorService

    // ── Launchers ──────────────────────────────────────────────────────────────

    private val requestCameraPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (granted) startCamera() else showPermissionRationale()
    }

    /** Selector de imagen desde la galería del dispositivo */
    private val galleryLauncher = registerForActivityResult(
        ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        uri ?: return@registerForActivityResult
        val bytes = uriToJpegBytes(uri) ?: run {
            Toast.makeText(this, R.string.err_unknown, Toast.LENGTH_SHORT).show()
            return@registerForActivityResult
        }
        viewModel.submitImage(bytes)
    }

    // ── Lifecycle ──────────────────────────────────────────────────────────────

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        cameraExecutor = Executors.newSingleThreadExecutor()
        setSupportActionBar(binding.toolbar)

        // Recibir la fruta seleccionada desde FruitSelectorActivity
        viewModel.fruitType = intent.getStringExtra(FruitSelectorActivity.EXTRA_FRUIT_TYPE)
        viewModel.fruitType?.let { fruit ->
            supportActionBar?.title = getString(
                R.string.title_main_with_fruit,
                fruit.toFruitDisplay(),
            )
            supportActionBar?.setDisplayHomeAsUpEnabled(true)
        }

        binding.btnScan.setOnClickListener { takePictureAndSubmit() }
        binding.btnGallery.setOnClickListener { galleryLauncher.launch("image/*") }
        binding.btnRetry.setOnClickListener { viewModel.reset() }
        binding.btnGrantPermission.setOnClickListener {
            requestCameraPermissionLauncher.launch(Manifest.permission.CAMERA)
        }

        observeState()

        if (hasCameraPermission()) startCamera()
        else requestCameraPermissionLauncher.launch(Manifest.permission.CAMERA)
    }

    override fun onDestroy() {
        super.onDestroy()
        cameraExecutor.shutdown()
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.menu_main, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean = when (item.itemId) {
        R.id.action_history -> {
            startActivity(Intent(this, HistoryActivity::class.java))
            true
        }
        android.R.id.home -> {
            // El flecha hacia atrás regresa al selector de fruta
            finish()
            true
        }
        else -> super.onOptionsItemSelected(item)
    }

    // ── Cámara ─────────────────────────────────────────────────────────────────

    private fun hasCameraPermission(): Boolean = ContextCompat.checkSelfPermission(
        this, Manifest.permission.CAMERA
    ) == PackageManager.PERMISSION_GRANTED

    private fun startCamera() {
        binding.permissionPanel.visibility = View.GONE
        binding.previewView.visibility = View.VISIBLE

        val providerFuture = ProcessCameraProvider.getInstance(this)
        providerFuture.addListener({
            val cameraProvider = providerFuture.get()
            val preview = Preview.Builder().build().also {
                it.setSurfaceProvider(binding.previewView.surfaceProvider)
            }
            imageCapture = ImageCapture.Builder()
                .setCaptureMode(ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY)
                .build()
            try {
                cameraProvider.unbindAll()
                cameraProvider.bindToLifecycle(
                    this, CameraSelector.DEFAULT_BACK_CAMERA, preview, imageCapture
                )
            } catch (exc: Exception) {
                Log.e(TAG, "No se pudo enlazar la cámara", exc)
            }
        }, ContextCompat.getMainExecutor(this))
    }

    private fun showPermissionRationale() {
        binding.previewView.visibility = View.GONE
        binding.permissionPanel.visibility = View.VISIBLE
    }

    private fun takePictureAndSubmit() {
        val capture = imageCapture ?: run {
            Toast.makeText(this, R.string.err_unknown, Toast.LENGTH_SHORT).show()
            return
        }
        capture.takePicture(
            ContextCompat.getMainExecutor(this),
            object : ImageCapture.OnImageCapturedCallback() {
                override fun onCaptureSuccess(image: ImageProxy) {
                    try {
                        viewModel.submitImage(image.toCompressedJpeg())
                    } finally {
                        image.close()
                    }
                }
                override fun onError(exception: ImageCaptureException) {
                    Log.e(TAG, "Captura falló", exception)
                    Toast.makeText(this@MainActivity, R.string.err_unknown, Toast.LENGTH_SHORT).show()
                }
            }
        )
    }

    // ── Galería ────────────────────────────────────────────────────────────────

    private fun uriToJpegBytes(uri: Uri, quality: Int = 72): ByteArray? {
        return try {
            // Primera pasada: solo leer dimensiones sin decodificar
            val opts = BitmapFactory.Options().apply { inJustDecodeBounds = true }
            contentResolver.openInputStream(uri)?.use {
                BitmapFactory.decodeStream(it, null, opts)
            }

            // Subsampling para no cargar la foto completa en RAM
            val sampleSize = maxOf(1, maxOf(opts.outWidth / 640, opts.outHeight / 640))

            // Segunda pasada: decodificar con subsampling
            val opts2 = BitmapFactory.Options().apply { inSampleSize = sampleSize }
            val bitmap = contentResolver.openInputStream(uri)?.use {
                BitmapFactory.decodeStream(it, null, opts2)
            } ?: return null

            val out = ByteArrayOutputStream()
            bitmap.compress(Bitmap.CompressFormat.JPEG, quality, out)
            bitmap.recycle()
            out.toByteArray()
        } catch (e: Exception) {
            Log.e(TAG, "Error leyendo imagen de galería", e)
            null
        }
    }

    // ── Estado ─────────────────────────────────────────────────────────────────

    private fun observeState() {
        viewModel.state.observe(this) { state ->
            when (state) {
                is ScanState.Idle -> renderIdle()
                is ScanState.Loading -> renderLoading()
                is ScanState.Success -> renderSuccess(state.result)
                is ScanState.NoDetection -> renderNoDetection(state.message)
                is ScanState.Error -> renderError(state.cause)
            }
        }
    }

    private fun renderIdle() = with(binding) {
        progressBar.visibility = View.GONE
        resultPanel.visibility = View.GONE
        actionButtons.visibility = View.VISIBLE
        btnRetry.visibility = View.GONE
    }

    private fun renderLoading() = with(binding) {
        progressBar.visibility = View.VISIBLE
        resultPanel.visibility = View.GONE
        actionButtons.visibility = View.GONE
        btnRetry.visibility = View.GONE
    }

    private fun renderSuccess(result: ScanResultDto) = with(binding) {
        progressBar.visibility = View.GONE
        resultPanel.visibility = View.VISIBLE
        actionButtons.visibility = View.GONE
        btnRetry.visibility = View.VISIBLE

        val colorRes = when (result.colorCode) {
            "green" -> R.color.ripeness_green
            "yellow" -> R.color.ripeness_yellow
            "red" -> R.color.ripeness_red
            else -> R.color.ripeness_yellow
        }
        ripenessIndicator.backgroundTintList =
            ContextCompat.getColorStateList(this@MainActivity, colorRes)

        txtFruit.text = getString(
            R.string.fmt_fruit_label,
            result.fruitType.toFruitDisplay(),
            result.maturityLabel.toMaturityDisplay(),
        )
        txtRecommendation.text = result.recommendation
        txtConfidence.text = getString(R.string.fmt_confidence, result.confidence * 100)
    }

    private fun renderNoDetection(message: String) = with(binding) {
        progressBar.visibility = View.GONE
        resultPanel.visibility = View.GONE
        actionButtons.visibility = View.GONE
        btnRetry.visibility = View.VISIBLE
        Toast.makeText(this@MainActivity, message, Toast.LENGTH_LONG).show()
    }

    private fun renderError(cause: Throwable) = with(binding) {
        Log.e(TAG, "Error al escanear", cause)
        progressBar.visibility = View.GONE
        resultPanel.visibility = View.GONE
        actionButtons.visibility = View.GONE
        btnRetry.visibility = View.VISIBLE
        Toast.makeText(this@MainActivity, R.string.err_network, Toast.LENGTH_LONG).show()
    }

    // ── Helpers ────────────────────────────────────────────────────────────────

    private fun String.toFruitDisplay(): String = when (this) {
        "aguacate_hass" -> getString(R.string.fruit_aguacate_hass)
        "platano" -> getString(R.string.fruit_platano)
        "tomate_usda" -> getString(R.string.fruit_tomate_usda)
        "mango" -> getString(R.string.fruit_mango)
        else -> this
    }

    private fun String.toMaturityDisplay(): String = when (this) {
        "INMADURO" -> getString(R.string.maturity_inmaduro)
        "OPTIMO" -> getString(R.string.maturity_optimo)
        "SOBRE_MADURO" -> getString(R.string.maturity_sobre_maduro)
        else -> this
    }

    private fun ImageProxy.toCompressedJpeg(quality: Int = 85): ByteArray {
        val buffer = planes[0].buffer
        val raw = ByteArray(buffer.remaining()).also { buffer.get(it) }
        val bitmap = BitmapFactory.decodeByteArray(raw, 0, raw.size) ?: return raw
        val rotated = if (imageInfo.rotationDegrees != 0) {
            val matrix = Matrix().apply { postRotate(imageInfo.rotationDegrees.toFloat()) }
            Bitmap.createBitmap(bitmap, 0, 0, bitmap.width, bitmap.height, matrix, true)
        } else bitmap
        val out = ByteArrayOutputStream()
        rotated.compress(Bitmap.CompressFormat.JPEG, quality, out)
        return out.toByteArray()
    }

    private companion object {
        const val TAG = "MainActivity"
    }
}

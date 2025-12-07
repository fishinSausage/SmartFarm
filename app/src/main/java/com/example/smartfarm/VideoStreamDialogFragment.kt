package com.example.smartfarm

import okio.ByteString
import androidx.appcompat.app.AlertDialog
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Matrix
import android.app.Dialog
import android.graphics.Color
import android.graphics.drawable.ColorDrawable
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageButton
import androidx.fragment.app.DialogFragment
import com.example.smartfarm.databinding.DialogVideoStreamBinding
import okhttp3.*

class VideoStreamDialogFragment : DialogFragment() {

    private var _binding: DialogVideoStreamBinding? = null
    private val binding get() = _binding!!

    private lateinit var webSocket: WebSocket

    override fun onCreateDialog(savedInstanceState: Bundle?): Dialog {
        val dialog = super.onCreateDialog(savedInstanceState)
        dialog.window?.setBackgroundDrawable(ColorDrawable(Color.TRANSPARENT))
        dialog.window?.setDimAmount(0.6f)
        return dialog
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = DialogVideoStreamBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onStart() {
        super.onStart()

        dialog?.window?.setLayout(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.MATCH_PARENT
        )

        setupWebSocket()
        setupCloseButton()
    }

    private fun setupCloseButton() {
        binding.btnClose.setOnClickListener {
            webSocket.close(1000, null)
            dismiss()
        }
    }

    private fun setupWebSocket() {
        val client = OkHttpClient()
        val request = Request.Builder()
            .url("ws://10.0.2.2:8080/api/video-stream") // 에뮬레이터에서 localhost
            .build()

        webSocket = client.newWebSocket(request, object : WebSocketListener() {

            // 🔥 1) YOLO 경고 텍스트 메시지 처리
            override fun onMessage(webSocket: WebSocket, text: String) {
                if (text.startsWith("ALERT:")) {
                    val alertMsg = text.removePrefix("ALERT:")

                    activity?.runOnUiThread {
                        AlertDialog.Builder(requireContext())
                            .setTitle("⚠️ 위험 감지!")
                            .setMessage(alertMsg)
                            .setPositiveButton("확인", null)
                            .show()
                    }
                }
            }

            // 🔥 2) 영상 스트림 (ByteString) 처리
            override fun onMessage(webSocket: WebSocket, bytes: ByteString) {
                val original = BitmapFactory.decodeByteArray(bytes.toByteArray(), 0, bytes.size)

                val matrix = Matrix()
                matrix.postRotate(90f)

                val rotated = Bitmap.createBitmap(
                    original, 0, 0,
                    original.width, original.height,
                    matrix, true
                )

                activity?.runOnUiThread {
                    binding.videoView.setImageBitmap(rotated)
                }
            }
        })

    }
    override fun onDestroyView() {
        super.onDestroyView()
        webSocket.cancel()
        _binding = null
    }
}

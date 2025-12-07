package com.example.smartfarm

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.webkit.WebChromeClient
import android.webkit.WebSettings
import android.webkit.WebView
import androidx.fragment.app.Fragment
import com.example.smartfarm.databinding.FragmentVideoStreamBinding


class VideoStreamFragment : Fragment() {

    private var _binding: FragmentVideoStreamBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentVideoStreamBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val webView: WebView = binding.videoWebView

        val settings = webView.settings
        settings.javaScriptEnabled = true
        settings.domStorageEnabled = true
        settings.mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW

        webView.webChromeClient = WebChromeClient()

        val html = """
            <!DOCTYPE html>
            <html>
            <head><title>Live Video</title></head>
            <body>
            <h3>Live Video Stream</h3>
            <canvas id="videoCanvas"></canvas>

            <script>
                const canvas = document.getElementById('videoCanvas');
                const ctx = canvas.getContext('2d');

                // Android 에뮬레이터 환경용
                const ws = new WebSocket("ws://10.0.2.2:8080/api/video-stream");
                ws.binaryType = "arraybuffer";

                ws.onmessage = (event) => {
                    const blob = new Blob([event.data], {type:'image/jpeg'});
                    const img = new Image();
                    img.onload = () => {
                        canvas.width = img.width;
                        canvas.height = img.height;
                        ctx.drawImage(img, 0, 0);
                    };
                    img.src = URL.createObjectURL(blob);
                };
            </script>
            </body>
            </html>
        """.trimIndent()

        webView.loadDataWithBaseURL(null, html, "text/html", "UTF-8", null)
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}

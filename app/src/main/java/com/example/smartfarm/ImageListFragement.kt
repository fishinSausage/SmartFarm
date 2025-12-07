package com.example.smartfarm.ui

import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.smartfarm.R
import com.example.smartfarm.adapter.ImageAdapter
import com.example.smartfarm.dto.ImageItem
import com.example.smartfarm.ImageApi
import com.jakewharton.retrofit2.converter.kotlinx.serialization.asConverterFactory
import kotlinx.coroutines.launch
import retrofit2.Retrofit
import kotlinx.serialization.json.Json
import okhttp3.MediaType.Companion.toMediaType

class ImageListFragment : Fragment() {

    private lateinit var recyclerView: RecyclerView
    private lateinit var imageApi: ImageApi

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(R.layout.fragment_image_list, container, false)
        recyclerView = view.findViewById(R.id.recyclerViewImages)
        recyclerView.layoutManager = GridLayoutManager(requireContext(), 2)

        setupApi()
        loadImages()

        return view
    }

    private fun setupApi() {
        val contentType = "application/json".toMediaType()
        val retrofit = Retrofit.Builder()
            .baseUrl("http://10.0.2.2:8080/") // 에뮬레이터에서 로컬 서버
            .addConverterFactory(Json { ignoreUnknownKeys = true }.asConverterFactory(contentType))
            .build()

        imageApi = retrofit.create(ImageApi::class.java)
    }

    private fun loadImages() {
        lifecycleScope.launch {
            try {
                val images: List<ImageItem> = imageApi.getAllImages()
                val recentImages = images.takeLast(6).reversed() // 최신 6개
                recyclerView.adapter = ImageAdapter(recentImages)
            } catch (e: Exception) {
                Log.e("ImageListFragment", "이미지 로드 실패", e)
            }
        }
    }
}

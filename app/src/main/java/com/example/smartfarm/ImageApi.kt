package com.example.smartfarm

import com.example.smartfarm.dto.ImageItem
import retrofit2.http.GET

interface ImageApi {
    @GET("/api/images/all")
    suspend fun getAllImages(): List<ImageItem>
}

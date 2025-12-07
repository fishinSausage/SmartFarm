package com.example.smartfarm.util

import retrofit2.*
import retrofit2.converter.gson.GsonConverterFactory
object RetrofitClient {
    private const val BASE_URL = "http://10.0.2.2:8080/"

    val instance: DroneApi by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(DroneApi::class.java)
    }
}
package com.example.smartfarm.util

import com.example.smartfarm.dto.DroneCommandDTO
import retrofit2.Call
import retrofit2.http.Body
import retrofit2.http.POST

interface DroneApi {
    @POST("api/drones/send-command")
    fun sendCommand(@Body command: DroneCommandDTO): Call<Void>
}
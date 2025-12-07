package com.example.smartfarm.dto

data class DroneCommandDTO(
    val deviceName: String,
    val request: String,
    val locationX: Double,
    val locationY: Double,
    val locationZ: Double
)
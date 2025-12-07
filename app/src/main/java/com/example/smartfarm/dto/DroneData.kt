package com.example.smartfarm.dto
import kotlinx.serialization.Serializable

@Serializable
data class DroneData(
    val id: Long,
    val droneId: String,
    val droneName: String? = null,
    val flightStatus: String,
    val currentLatitude: Double? = null,
    val currentLongitude: Double? = null,
    val altitude: Double? = null,
    val batteryLevel: Int? = null,
    val mappingData: String? = null,
    val missionStatus: String? = null,
    val lastUpdated: String,
    val createdAt: String
)
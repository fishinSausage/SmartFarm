package com.example.smartfarm.dto

import kotlinx.serialization.Serializable

@Serializable
data class ImageItem(
    val id: Long,
    val deviceId: String,
    val imagePath: String,
    val fileName: String,
    val fileSize: Long,
    val mimeType: String,
    val createdAt: String,
    val timestamp: String
)

typealias ImageResponse = List<ImageItem>
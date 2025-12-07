package com.example.smartfarm.util

fun toImageUrl(rawPath: String): String {
    val cleaned = rawPath
        .replace("\\", "/")
        .replace("./", "/")

    return "http://YOUR_SERVER_IP:8080$cleaned"
}
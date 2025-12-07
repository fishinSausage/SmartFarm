import kotlinx.serialization.Serializable

@Serializable
data class SensorData(
    val id: Long,
    val deviceId: String?,
    val fieldId: Long?,
    val fieldName: String?,
    val temperature: Double?,
    val humidity: Double?,
    val illuminance: Double?,
    val co2Level: Double?,
    val soilMoisture: Double?,
    val phValue: Double?,
    val integratedInfo: String?,
    val createdAt: String?,
    val light: Double?
)
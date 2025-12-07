package com.example.smartfarm

import SensorData
import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ProgressBar
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import com.example.smartfarm.dto.DroneData
import com.example.smartfarm.network.HttpClient
import io.ktor.client.call.body
import io.ktor.client.request.get
import kotlinx.coroutines.launch
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive

class DashboardFragment : Fragment() {

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(R.layout.fragment_dashboard, container, false)

        val tvTemp = view.findViewById<TextView>(R.id.tv_avg_temp)
        val tvHumidity = view.findViewById<TextView>(R.id.tv_avg_humidity)
        val tvCo2 = view.findViewById<TextView>(R.id.tv_CO2)
        val tvActiveDrone = view.findViewById<TextView>(R.id.tv_active_drone)
        val tvDroneStatus = view.findViewById<TextView>(R.id.tv_drone_status)
        val tvDroneZ = view.findViewById<TextView>(R.id.tv_drone_z)
        val tvDroneSpd = view.findViewById<TextView>(R.id.tv_drone_spd)
        val pbDroneBattery = view.findViewById<ProgressBar>(R.id.pb_drone_battery)
        Log.d("DashboardFragment", "Sensor Data: $tvTemp")

        lifecycleScope.launch {
            val client = HttpClient.client
            while (isActive) {
                try {
                    val sensorData: SensorData =
                        client.get("http://10.0.2.2:8080/api/sensing/device/sensor_NO1/latest")
                            .body()
                    Log.d("DashboardFragment", "Sensor Data: $sensorData")
                    tvTemp.text = "평균 온도🌡️\n${sensorData.temperature}°C"
                    tvHumidity.text = "평균 습도🌧️\n${sensorData.humidity}%"
                    tvCo2.text = "CO2 Level\n${sensorData.co2Level} ppm"

                    val droneData : DroneData = client.get("http://10.0.2.2:8080/api/drones/drone_NO1").body()
                    tvDroneStatus.text = "드론 A (${droneData.flightStatus})"
                    tvDroneZ.text = "고도 : ${droneData.altitude}"
                    tvDroneSpd.text = "속도: "
                    if(droneData.batteryLevel != null)
                        pbDroneBattery.progress=droneData.batteryLevel

                } catch (e: Exception) {
                    e.printStackTrace()
                    Log.e("DashboardFragment", "Error fetching sensor data", e)
                }
                val drones: List<DroneData> =
                    client.get("http://10.0.2.2:8080/api/drones/active").body()
                val drone = drones.firstOrNull()
                Log.d("DashboardFragment","droneData:$drone")
                if (drone != null) {
                    tvActiveDrone.text ="활성 드론 1/2"
                } else {
                    tvActiveDrone.text ="활성 드론 0/2"
                }


                delay(1000)
            }
        }

        return view
    }
}


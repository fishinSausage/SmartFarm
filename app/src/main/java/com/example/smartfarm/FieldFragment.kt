package com.example.smartfarm;
//밭 정보

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
import com.example.smartfarm.databinding.FragmentFieldBinding
import com.example.smartfarm.network.HttpClient
import io.ktor.client.call.body
import io.ktor.client.request.get
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*


class FieldFragment : Fragment() {

    private var _binding: FragmentFieldBinding? = null
    private val binding get() = _binding!!

    // -- (예시) 번들 키 --
    companion object {
        const val ARG_FIELD_NAME = "arg_field_name"
        const val ARG_CROP = "arg_crop"
        const val ARG_AREA = "arg_area"
        const val ARG_STATUS = "arg_status"
        const val ARG_LOCATION = "arg_location"
        const val ARG_LAST_UPDATED = "arg_last_updated"

        const val ARG_TEMP = "arg_temp"
        const val ARG_HUMIDITY = "arg_humidity"
        const val ARG_SOIL_MOISTURE = "arg_soil_moisture"
        const val ARG_LIGHT = "arg_light"
        const val ARG_SOIL_PH = "arg_soil_ph"
        const val ARG_SENSOR_ID = "arg_sensor_id"
        const val ARG_SENSOR_UPDATE_TIME = "arg_sensor_update_time"

        fun newInstance(bundle: Bundle): FieldFragment {
            val f = FieldFragment()
            f.arguments = bundle
            return f
        }
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?,
    ): View {
        _binding = FragmentFieldBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // 번들에서 값 읽기(있으면) 아니면 샘플 데이터 표시
//        val args = arguments
//
//        val fieldName = args?.getString(ARG_FIELD_NAME) ?: "1번 밭 (벼)"
//        val crop = args?.getString(ARG_CROP) ?: "벼"
//        val area = args?.getString(ARG_AREA) ?: "5000㎡"
//        val status = args?.getString(ARG_STATUS) ?: "정상"
//        val location = args?.getString(ARG_LOCATION) ?: "37.5665, 126.9780"
//        val lastUpdated = args?.getString(ARG_LAST_UPDATED) ?: formattedNow()
//
//
//        val temp = args?.getString(ARG_TEMP) ?: "29.5℃"
//        val humidity = args?.getString(ARG_HUMIDITY) ?: "74.1%"
//        val soilMoisture = args?.getString(ARG_SOIL_MOISTURE) ?: "45.7%"
//        val light = args?.getString(ARG_LIGHT) ?: "54 lux"
//        val soilPh = args?.getString(ARG_SOIL_PH) ?: "7.57"
//        val sensorId = args?.getString(ARG_SENSOR_ID) ?: "sensor-field-1-23"
//        val sensorUpdateTime = args?.getString(ARG_SENSOR_UPDATE_TIME) ?: formattedNow()
//
//        // 바인딩에 값 넣기
//        binding.lastUpdated.text = "마지막 관측: $lastUpdated"
//
//        binding.soilMoistureValue.text = soilMoisture
//        binding.lightValue.text = light
//        binding.soilPhValue.text = "토양 pH: $soilPh"
//
//        binding.sensorId.text = "센서 ID: $sensorId"
//        binding.updateTime.text = "업데이트: $sensorUpdateTime"
        val tvTemp = view.findViewById<TextView>(R.id.tv_temp)
        val tvTemp2 = view.findViewById<TextView>(R.id.tv_temp2)
        val tvHumidity = view.findViewById<TextView>(R.id.tv_humidity)
        val pvHumidity = view.findViewById<ProgressBar>(R.id.pb_humidity)
        val tvCo2 = view.findViewById<TextView>(R.id.tv_co2)
        val tvLight = view.findViewById<TextView>(R.id.tv_lightValue)
        val pbCo2 = view.findViewById<ProgressBar>(R.id.pb_co2)
        val pbLight= view.findViewById<ProgressBar>(R.id.pb_lightValue)

        lifecycleScope.launch {
            val client = HttpClient.client
            while (isActive) {
                try {
                    val sensorData: SensorData =
                        client.get("http://10.0.2.2:8080/api/sensing/device/sensor_NO1/latest")
                            .body()
                    Log.d("FieldFragment", "Sensor Data: $sensorData")
                    Log.d("FieldFragment", "Light: ${sensorData.light}")
                    tvTemp.text = "평균 온도\n${sensorData.temperature}°C"
                    tvTemp2.text = "${sensorData.temperature}°C"
                    tvHumidity.text = "평균 습도\n${sensorData.humidity}%"
                    pvHumidity.progress = (sensorData.humidity ?: 0.0).toInt()
                    tvCo2.text = "CO2 \n${sensorData.co2Level} ppm"
                    pbCo2.progress = (sensorData.co2Level ?: 0.0).toInt();
                    tvLight.text = "${sensorData.light} lux"
                    pbLight.progress = (sensorData.light ?: 0.0).toInt()


                }
                catch (e: Exception) {
                    Log.e("FieldFragment", "Error updating UI", e)
                }
                delay(1000)
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }

    private fun formattedNow(): String {
        val sdf = SimpleDateFormat("yyyy. MM. dd. a hh:mm:ss", Locale.getDefault())
        return sdf.format(Date())
    }
}

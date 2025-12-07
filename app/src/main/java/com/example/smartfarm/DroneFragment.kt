package com.example.smartfarm

import SensorData
import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import com.example.smartfarm.databinding.FragmentDroneBinding
import com.example.smartfarm.dto.DroneCommandDTO
import com.example.smartfarm.dto.DroneData
import com.example.smartfarm.network.HttpClient
import com.example.smartfarm.util.RetrofitClient
import io.ktor.client.call.body
import io.ktor.client.request.get
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import retrofit2.Call

class DroneFragment : Fragment() {

    private var _binding: FragmentDroneBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentDroneBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // UI 요소 가져오기
        val tvDroneStatus = view.findViewById<TextView>(R.id.tvDroneAStatus)
        val tvAltitude = view.findViewById<TextView>(R.id.tvAltitude)
        val tvSpeed = view.findViewById<TextView>(R.id.tvSpeed)
        val pbSpeed = view.findViewById<ProgressBar>(R.id.pbSpeed)
        val tvBattery = view.findViewById<TextView>(R.id.tvBattery)
        val pbBattery = view.findViewById<ProgressBar>(R.id.barBattery)
        val tvLocation = view.findViewById<TextView>(R.id.tvLocation)
        val tvUpdated = view.findViewById<TextView>(R.id.tvUpdated)

        // ------------- 🔘 버튼 연결 (XML에 있어야 함) -------------
        binding.btnSendDroneCommand.setOnClickListener {
            sendDroneCommand()
        }
        // ----------------------------------------------------------

        // 기본 값 초기화
        tvDroneStatus.text = "로딩중"
        pbBattery.progress = 0
        pbSpeed.progress = 0
        tvBattery.text = "로딩중"
        tvLocation.text = "로딩중"
        tvAltitude.text = "로딩중"
        tvSpeed.text = "로딩중"
        tvUpdated.text = "로딩중"

        // 실시간 드론 정보 갱신
        lifecycleScope.launch {
            val client = HttpClient.client

            while (isActive) {
                try {
                    val droneData: DroneData =
                        client.get("http://10.0.2.2:8080/api/drones/drone_NO1").body()

                    Log.d("DroneFragment", "Drone Data: $droneData")

                    tvDroneStatus.text = "${droneData.flightStatus}"
                    tvAltitude.text = "고도 ${droneData.altitude} m"
                    tvSpeed.text = "속도 NULL m/s"
                    pbSpeed.progress = 0
                    tvBattery.text = "${droneData.batteryLevel}%"
                    pbBattery.progress = droneData.batteryLevel ?: 0
                    tvLocation.text = "${droneData.currentLatitude}, ${droneData.currentLongitude}"
                    tvUpdated.text = "${droneData.lastUpdated}"

                } catch (e: Exception) {
                    Log.e("DroneFragment", "Error fetching drone data", e)
                }
                delay(1000)
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }

    // 🔥 서버로 드론 명령 전송하는 함수
    private fun sendDroneCommand() {
        val command = DroneCommandDTO(
            deviceName = "drone_NO1",
            request = "MOVE",
            locationX = 10.0,
            locationY = 5.0,
            locationZ = 2.0
        )

        val call = RetrofitClient.instance.sendCommand(command)

        call.enqueue(object : retrofit2.Callback<Void> {
            override fun onResponse(
                call: Call<Void>,
                response: retrofit2.Response<Void>
            ) {
                if (response.isSuccessful) {
                    Toast.makeText(context, "드론 명령 전송 성공!", Toast.LENGTH_SHORT).show()
                } else {
                    Toast.makeText(context, "전송 실패: ${response.code()}", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<Void>, t: Throwable) {
                Toast.makeText(context, "통신 오류: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })
    }
}

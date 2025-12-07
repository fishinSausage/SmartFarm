import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.smartfarm.R
import com.example.smartfarm.SensorAdapter
import com.example.smartfarm.network.HttpClient
import io.ktor.client.call.body
import io.ktor.client.request.get
import kotlinx.coroutines.launch

class DataFragment : Fragment() {

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_data, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val rv = view.findViewById<RecyclerView>(R.id.rvSensorList)
        val tvTotal = view.findViewById<TextView>(R.id.tvTotalSensors)

        lifecycleScope.launch {
            val client = HttpClient.client
            val response = client.get("http://10.0.2.2:8080/api/sensing/all").body<List<SensorData>>()

            tvTotal.text = "총 ${response.size}개의 센서 데이터"

            rv.adapter = SensorAdapter(response)
            rv.layoutManager = LinearLayoutManager(requireContext())
        }
    }
}

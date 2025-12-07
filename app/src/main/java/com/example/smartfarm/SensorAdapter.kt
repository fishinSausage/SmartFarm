package com.example.smartfarm

import SensorData
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView

class SensorAdapter(private val items: List<SensorData>) :
    RecyclerView.Adapter<SensorAdapter.SensorViewHolder>() {

    inner class SensorViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val tvSensorId: TextView = itemView.findViewById(R.id.tvSensorId)
        val tvFieldName: TextView = itemView.findViewById(R.id.tvFieldName)
        val tvTemp: TextView = itemView.findViewById(R.id.tvTemp)
        val tvHumidity: TextView = itemView.findViewById(R.id.tvHumidity)
        val tvMoisture: TextView = itemView.findViewById(R.id.tvMoisture)
        val tvLight: TextView = itemView.findViewById(R.id.tvLight)
        val tvPH: TextView = itemView.findViewById(R.id.tvPH)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): SensorViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.sensor_item, parent, false)
        return SensorViewHolder(view)
    }

    override fun onBindViewHolder(holder: SensorViewHolder, position: Int) {
        val item = items[position]

        holder.tvSensorId.text = item.deviceId
        holder.tvFieldName.text = item.fieldName ?: "밭 정보 없음"

        holder.tvTemp.text = "${item.temperature}°C"
        holder.tvHumidity.text = "${item.humidity}%"
        holder.tvMoisture.text = item.soilMoisture?.toString() ?: "-"
        holder.tvLight.text = "${item.light} lux"
        holder.tvPH.text = item.phValue?.toString() ?: "-"
    }

    override fun getItemCount(): Int = items.size
}

package com.example.smartfarm.adapter

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.example.smartfarm.R
import com.example.smartfarm.dto.ImageItem

class ImageAdapter(
    private val items: List<ImageItem>
) : RecyclerView.Adapter<ImageAdapter.ImageViewHolder>() {

    inner class ImageViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val imageView: ImageView = view.findViewById(R.id.imageView)
        val infoView: TextView = view.findViewById(R.id.imageInfo)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ImageViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_image, parent, false)
        return ImageViewHolder(view)
    }

    override fun onBindViewHolder(holder: ImageViewHolder, position: Int) {
        val item = items[position]

        val url = "http://10.0.2.2:8080/api/images/${item.id}/file" // 에뮬레이터용 URL

        Glide.with(holder.itemView.context)
            .load(url)
            .placeholder(R.drawable.placeholder) // placeholder 이미지
            .error(R.drawable.placeholder)
            .into(holder.imageView)

        holder.infoView.text = "${item.deviceId}\n${item.fileName}\n${item.createdAt}"
    }

    override fun getItemCount() = items.size
}

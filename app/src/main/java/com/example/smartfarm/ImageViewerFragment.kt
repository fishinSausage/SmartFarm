package com.example.smartfarm

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import androidx.fragment.app.Fragment
import com.bumptech.glide.Glide
import com.example.smartfarm.R

class ImageViewerFragment : Fragment() {

    companion object {
        private const val ARG_URL = "image_url"

        fun newInstance(url: String) = ImageViewerFragment().apply {
            arguments = Bundle().apply {
                putString(ARG_URL, url)
            }
        }
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        return inflater.inflate(R.layout.fragment_image_viewer, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val url = arguments?.getString(ARG_URL)
        val imageView = view.findViewById<ImageView>(R.id.fullImage)

        Glide.with(requireContext())
            .load(url)
            .into(imageView)
    }
}

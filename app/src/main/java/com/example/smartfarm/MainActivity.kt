package com.example.smartfarm

import DataFragment
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import androidx.fragment.app.Fragment
import com.example.smartfarm.databinding.ActivityMainBinding
import com.example.smartfarm.ui.ImageListFragment

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // 기본 화면은 Dashboard
        replaceFragment(DashboardFragment())

        // 메뉴 클릭 시 페이지 이동
        binding.menuDashboard.setOnClickListener {
            replaceFragment(DashboardFragment())
        }
        binding.menuField.setOnClickListener {
            replaceFragment(FieldFragment())
        }
        binding.menuDrone.setOnClickListener {
            replaceFragment(DroneFragment())
        }
        binding.menuStats.setOnClickListener {
            replaceFragment(StatsFragment())
        }
        binding.menuImage.setOnClickListener {
            replaceFragment(ImageListFragment())
        }
        binding.menuData.setOnClickListener {
            replaceFragment(DataFragment())
        }
//        binding.menuVideo.setOnClickListener {
//            replaceFragment(VideoStreamFragment())
//        }
        binding.menuDialogVideo.setOnClickListener {
            val dialog = VideoStreamDialogFragment()
            dialog.show(supportFragmentManager, "video_stream")
        }

    }


    private fun replaceFragment(fragment: Fragment) {
        supportFragmentManager.beginTransaction()
            .replace(R.id.mainContainer, fragment)
            .commit()
    }
}

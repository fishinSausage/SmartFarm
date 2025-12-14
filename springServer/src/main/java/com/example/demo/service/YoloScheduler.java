package com.example.demo.service;

import com.example.demo.controller.VideoController;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.*;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;

@Service
public class YoloScheduler {

    private final RestTemplate restTemplate = new RestTemplate();
    private static final String PYTHON_YOLO_URL = "http://localhost:8000/detect";

    @Scheduled(fixedRate = 1000) // 1초 간격
    public void sendFrameToYOLO() {
        byte[] frame = VideoController.pollFrameForYOLO();
        if (frame == null) return;

        try {
            // multipart/form-data 바디 생성
            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            ByteArrayResource byteArrayResource = new ByteArrayResource(frame) {
                @Override
                public String getFilename() {
                    return "frame.jpg"; // 파일 이름 지정
                }
            };
            body.add("file", byteArrayResource);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.MULTIPART_FORM_DATA);

            HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);

            // Python YOLO 서버 호출
            String response = restTemplate.postForObject(PYTHON_YOLO_URL, requestEntity, String.class);

            if (response != null && (response.length() > 2)) {
                System.out.println("⚠️ YOLO Alert: " + response);
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
package com.example.demo.controller;

import com.example.demo.websocket.VideoWebSocketHandler;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

@RestController
@RequestMapping("/video")
public class VideoController {

    // YOLO 분석용 큐
    private static final BlockingQueue<byte[]> yoloQueue = new LinkedBlockingQueue<>(10);

    @PostMapping(value = "/frame", consumes = MediaType.IMAGE_JPEG_VALUE)
    public ResponseEntity<String> receiveFrame(@RequestBody byte[] frameData) {
        // 1️⃣ 브라우저 실시간 스트리밍
        VideoWebSocketHandler.broadcastFrame(frameData);

        // 2️⃣ YOLO 분석용 큐에 넣기 (offer: 큐가 차면 버림)
        yoloQueue.offer(frameData);

        return ResponseEntity.ok("Frame forwarded");
    }

    // 외부에서 YOLO 처리용 큐 접근
    public static byte[] pollFrameForYOLO() {
        return yoloQueue.poll();
    }
}

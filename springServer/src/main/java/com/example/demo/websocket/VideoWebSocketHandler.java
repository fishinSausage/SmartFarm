package com.example.demo.websocket;

import org.springframework.web.socket.*;
import org.springframework.web.socket.handler.TextWebSocketHandler;
import java.util.concurrent.CopyOnWriteArraySet;

public class VideoWebSocketHandler extends TextWebSocketHandler {
    private static CopyOnWriteArraySet<WebSocketSession> sessions = new CopyOnWriteArraySet<>();

    @Override
    public void afterConnectionEstablished(WebSocketSession session) throws Exception {
        sessions.add(session);
        System.out.println("📡 Browser connected: " + session.getId());
    }

    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) throws Exception {
        sessions.remove(session);
        System.out.println("❌ Browser disconnected: " + session.getId());
    }

    public static void broadcastFrame(byte[] frame) {
        sessions.forEach(session -> {
            try {
                session.sendMessage(new BinaryMessage(frame));
            } catch (Exception e) {
                e.printStackTrace();
            }
        });
    }
}

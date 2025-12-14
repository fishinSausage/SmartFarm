import cv2
import socket
import struct
import time

NODE_IP = "127.0.0.1"
NODE_PORT = 5001

cap = cv2.VideoCapture(0)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((NODE_IP, NODE_PORT))

print("videoTransfer has started...")

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    _, jpeg = cv2.imencode('.jpg', frame)
    data = jpeg.tobytes()

    # 먼저 길이를 4바이트로 전송
    sock.sendall(struct.pack(">L", len(data)))
    # JPEG 데이터 전송
    sock.sendall(data)

    time.sleep(0.05)

import cv2
import numpy as np
import socket
import json
import time
from ultralytics import YOLO

SERVER_IP = '127.0.0.1'
SERVER_PORT = 5000

# 서버 연결
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))
print("Connected to Server")

#YOLO 모델 로드
model = YOLO("best.pt")

#카메라 연결
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
if not ret:
    print("Cannot open camera")
    cap.release()
    client_socket.close()
    exit()

print("YOLO Detection started")

last_sent_time = 0
cooldown = 0.25   # YOLO 감지 쿨다운 (서버 과부하 방지)
last_periodic_time = time.time()
periodic_interval = 10
conf_threshold = 0.7

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        #YOLO 객체 탐지
        results = model(frame, verbose=False)
        annotated_frame = results[0].plot()

        # 감지 여부 확인
        detected = False
        for box in results[0].boxes:
            cls = int(box.cls[0])     # 클래스 번호
            conf = float(box.conf[0])
            if  conf > conf_threshold: # confidence

            # 필요하면 특정 클래스만 전송 (예: 사람만)
            # if cls != 0:   # 예: YOLO COCO 기준 '0 = person'
            #     continu

                detected = True

        if detected:
            now = time.time()
            if now - last_sent_time > cooldown:
                data = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "event": "object_detected",
                    "device_name": "camera_NO1",
                    "location_x": 2,
                    "location_y": 3
                }

                try:
                    json_data = json.dumps(data)
                    client_socket.sendall(json_data.encode('utf-8'))
                    print("Sent to server:", json_data)
                except Exception as e:
                    print("Fail to send data:", e)

                last_sent_time = now

        # 10초 주기 전송
        now = time.time()
        if now - last_periodic_time >= periodic_interval:
            periodic_data = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "event": "periodic_update",
                "device_name": "camera_NO1",
                "location_x": 2,
                "location_y": 3
            }

            try:
                json_data = json.dumps(periodic_data)
                client_socket.sendall(json_data.encode('utf-8'))
                print("10초 주기 전송:", json_data)
            except Exception as e:
                print("Fail to send periodic data:", e)

            last_periodic_time = now

        # 화면 출력
        cv2.imshow("YOLO Object Detection", annotated_frame)

        if cv2.waitKey(1) == 27:  # ESC 종료
            break

except KeyboardInterrupt:
    print("Interrupted by user")

finally:
    cap.release()
    client_socket.close()
    cv2.destroyAllWindows()
    print("Client closed")

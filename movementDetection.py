import cv2
import numpy as np
import socket
import json
import time

SERVER_IP = '127.0.0.1'  # 서버 IP 주소
SERVER_PORT = 5000       # 서버 포트 번호

# TCP 소켓 생성 및 연결
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))
print("Connected to Server")

# 카메라 연결
cap = cv2.VideoCapture(0)
ret, frame1 = cap.read()
if not ret:
    print("Cannot open camera")
    cap.release()
    client_socket.close()
    exit()

frame1_gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
frame1_gray = cv2.GaussianBlur(frame1_gray, (21, 21), 0)

print("Motion detection started")

last_sent_time = 0
cooldown = 0.25  # 움직임 감지 쿨다운
movement_count = 0

# 주기적 전송:
periodic_interval = 10
last_periodic_time = time.time()

try:
    while True:
        ret, frame2 = cap.read()
        if not ret:
            break

        # 현재 프레임 처리
        frame2_gray = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        frame2_gray = cv2.GaussianBlur(frame2_gray, (21, 21), 0)

        # 프레임 차이 계산
        diff = cv2.absdiff(frame1_gray, frame2_gray)
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
        thresh = cv2.dilate(thresh, None, iterations=2)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        motion_detected = False
        for contour in contours:
            if cv2.contourArea(contour) < 1000:
                continue
            motion_detected = True
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame2, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # 움직임 감지 시
        if motion_detected:
            movement_count = movement_count + 1
            if movement_count == 4: # 4번 연속으로 움직임 감지가 됬을때
                cv2.putText(frame2, "Motion Detected!", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                print("Movement Detected")

                now = time.time()
                if now - last_sent_time > cooldown:
                    data = {
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "event": "motion_detected",
                        "device_name": "camera_NO1",
                        "location_x": 2,
                        "location_y": 3
                    }

                    try:
                        json_data = json.dumps(data)
                        client_socket.sendall(json_data.encode('utf-8'))
                        print("📤 Sent to server:", json_data)
                    except Exception as e:
                        print("Fail to send data:", e)

                    last_sent_time = now
                movement_count = 0

        # 움직임이 없어도 10초마다 주기 전송
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
        cv2.imshow("Motion Detection", frame2)
        frame1_gray = frame2_gray.copy()

        if cv2.waitKey(10) == 27:  # ESC 키 종료
            break

except KeyboardInterrupt:
    print("Interrupted by user")

finally:
    cap.release()
    client_socket.close()
    cv2.destroyAllWindows()
    print("Client closed")

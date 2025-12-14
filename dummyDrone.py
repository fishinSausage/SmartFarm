import socket
import json
import time

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5002

def safe_json_parse(data: str):
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return None

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_IP, SERVER_PORT))
    print("Connected to server")

    buffer = ""

    while True:
        data = client.recv(1024).decode()

        if not data:
            print("server Disconnected")
            break

        buffer += data

        # 줄바꿈 단위로 패킷 분리
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)

            req = safe_json_parse(line)
            if req is None:
                print("Fail to parse Data:", line)
                continue

            print("Request from Server:", req)

            response = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "event": "drone",
                "deviceName": "drone_NO1",
                "data": {
                    "locationX": 1,
                    "locationY" : 1,
                    "batteryRemain" : 50.0,
                    "speedX" : 1,
                    "speedY" : 1,
                    "speedZ" : 1
                }
            }

            client.send((json.dumps(response) + "\n").encode())
            print("📤 드론 → 서버 응답 전송:", response)


if __name__ == "__main__":
    main()

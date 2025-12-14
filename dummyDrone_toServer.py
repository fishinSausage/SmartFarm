import time
import requests

# 데이터 전송할 URL (백엔드 API 엔드포인트)
URL = "http://localhost:8080/api/drones/receive-from-node"  

def send_data():

    data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "event": "drone",
        "deviceName": "drone_NO1",
        "data": {
            "locationX": 0,
            "locationY" : 0,
            "batteryRemain" : 57,
            "speedX" : 0,
            "speedY" : 0,
            "speedZ" : 0
        }
    }
    
    try:
        response = requests.post(URL, json=data)
        print(f"Sent: {data}")
        print(f"Response: {response.status_code} {response.text}")
    except Exception as e:
        print(f"Error sending data: {e}")

if __name__ == "__main__":
    while True:
        send_data()
        time.sleep(5)  # 5초마다 전송, 필요에 따라 조절

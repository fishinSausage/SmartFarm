import time
import random
import requests

# 데이터 전송할 URL (백엔드 API 엔드포인트)
URL = "http://localhost:8080/api/sensing/receive-from-node"  # 실제 엔드포인트로 바꿔주세요

def generate_dummy_data():
    temp = round(random.uniform(15.0, 30.0), 2)       # 온도
    hum = round(random.uniform(30.0, 80.0), 2)        # 습도
    light = random.randint(100, 1000)                 # 조도
    CO2 = random.randint(300, 2000)                   # CO2 농도
    return temp, hum, light, CO2

def send_data():
    temp, hum, light, CO2 = generate_dummy_data()
    
    data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "event": "sensor",
        "deviceName": "sensor_NO1",
        "data": {
            "temperature": temp,
            "humidity": hum,
            "light": light,
            "CO2": CO2
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

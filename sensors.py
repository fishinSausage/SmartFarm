import time
import board
import busio
import socket
import json
import adafruit_sht31d

from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)

SERVER_IP = '127.0.0.1'
SERVER_PORT = 5000

# 서버 연결
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client_socket.connect((SERVER_IP, SERVER_PORT))
    print("Connected to Server")
except Exception as e:
    print("Server connection failed:", e)
    exit(1)

# ============ SHT30 초기화 =============
try:
    sht30 = adafruit_sht31d.SHT31D(i2c)
    print("SHT30 detected")
    sht_available = True
except Exception as e:
    print("SHT30 not found:", e)
    sht_available = False
    sht30 = None

# ============ ADS1115 초기화 =============
try:
    ads = ADS1115(i2c)
    chan_A0 = AnalogIn(ads, 0) #MG811
    chan_A1 = AnalogIn(ads, 1) #TEMT6000
    print("ADS1115 detected")
    ads_available = True
except Exception as e:
    print("ADS1115 not found:", e)
    ads_available = False
    chan_A0 = chan_A1 = None

print("\nStarting Sensor reading...")

try:
    while True:
        print("----------")

        # SHT30 데이터
        if sht_available:
            try:
                temp = round(sht30.temperature, 2)
                hum = round(sht30.relative_humidity, 2)
                print(f"SHT30 Temperature: {temp:.2f} C")
                print(f"SHT30 Humidity: {hum:.2f} %")
            except Exception as e:
                print("SHT30 read error:", e)
                temp = hum = None
        else:
            temp = hum = None

        # ADS1115 데이터
        if ads_available:
            try:
                temt_raw = chan_A1.value
                temt_volt = chan_A1.voltage
                mg811_raw = chan_A0.value
                mg811_volt = chan_A0.voltage

                print(f"TEMT6000 Raw: {temt_raw}, Voltage: {temt_volt:.3f} V")
                print(f"MG811 Raw: {mg811_raw}, Voltage: {mg811_volt:.3f} V")
            except Exception as e:
                print("ADS1115 read error:", e)
                temt_raw = mg811_raw = None
        else:
            temt_raw = mg811_raw = None

        # JSON 데이터 구성
        data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "event": "sensor_data",
            "device_name": "sensor_NO1",
            "data" : {
                "temperature": temp,
                "humidity": hum,
                "light": temt_raw,
                "CO2": mg811_raw
            }
        }

        # 서버 전송
        try:
            json_data = json.dumps(data)
            client_socket.sendall(json_data.encode('utf-8'))
            print("Sent to server:", json_data)
        except Exception as e:
            print("Fail to send data:", e)

        time.sleep(10)

except KeyboardInterrupt:
    print("Program stopped manually.")

finally:
    client_socket.close()
    print("Socket closed.")

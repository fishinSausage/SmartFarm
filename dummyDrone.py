import socket
import json
import last as vision_module
from datetime import datetime
import threading
import time

SERVER_IP = "192.168.68.103"
SERVER_PORT = 5002

def safe_json_parse(data: str):
    try:
        parsed = json.loads(data)
        print("recved: ")
        print(json.dumps(parsed, indent=2))
        return parsed.get("event")
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
            if req == "inspect":
                control_thread = threading.Thread(target=vision_module.main, daemon=True)
                control_thread.start() 
                while(control_thread.is_alive()):
                    time.sleep(10)
                    print("inside loop")
                    # Get GPS coordinates from the shared vision_module
                    gps_pos = vision_module.get_current_gps()
                    
                    if gps_pos is None:
                        gps_pos = (0, 0, 0)


                    response = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "event": "coordinate",
                        "device_name": "drone",
                        "data": {
                            "latitude": gps_pos[0],
                            "longitude": gps_pos[1],
                            "altitude": gps_pos[2],
                        }
                    }
                    print(json.dumps(response, indent=2))
                    client.send((json.dumps(response) + "\n").encode())

                control_thread.join(timeout=2.0)
                # if not drone_unfinished:
                #     #TODO send finshed repsonse jsson


if __name__ == "__main__":
    main()

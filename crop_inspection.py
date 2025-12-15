# crop_inspection_main.py
import cv2
import json
import base64
import os
from datetime import datetime
from detect_lettuce import get_lettuce_mask
from crop_inspection_v2 import analyze_plants, visualize_results

def crop_inspection(image_path, gps_pos, socket_client=None):
    frame = cv2.imread(image_path)
    if frame is None:
        raise RuntimeError(f"Could not read {image_path}")

    # 1) Run YOLO – get only pixels the model treated as lettuce
    lettuce_mask, boxes = get_lettuce_mask(frame)

    # 2) Run ExG / stress only on those pixels
    resized, exg_img, plant_mask_total, mask_green, plants = analyze_plants(
        frame, lettuce_mask=lettuce_mask
    )

    vis = visualize_results(resized, plants)

    # Encode visualization image as JPEG in memory
    _, buffer = cv2.imencode('.jpg', vis)
    vis_base64 = base64.b64encode(buffer).decode('utf-8')

    # Check for bad lettuces
    bad_plants = []
    for p in plants:
        label = p["label"]
        # Check if plant is stressed or tiny/missing
        if "stressed" in label or "tiny" in label or "missing" in label:
            bad_plants.append(p)
            print(f"[WARNING] Bad lettuce detected! ID={p['id']}, "
                  f"label={label}, green_ratio={p['green_ratio']:.2f}, "
                  f"area={p['area_total']}")
    

    # Save the detected image locally
    detected_dir = "detected_images"
    os.makedirs(detected_dir, exist_ok=True)
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = os.path.join(detected_dir, f"detected_{timestamp_str}.jpg")
    cv2.imwrite(save_path, vis)
    print(f"[INFO] Detected image saved to {save_path}")
    if bad_plants:
        print(f"[ALERT] Total bad lettuces found: {len(bad_plants)}/{len(plants)}")
        
        # Send alert to server if socket_client is provided
        if socket_client is None:
            try:
                # Handle case where gps_pos is None
                if gps_pos is None:
                    gps_pos = (0.0, 0.0, 0.0)
                
                alert_data = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "event": "bad_lettuce_alert",
                    "device_name": "drone",
                    "data": {
                        "latitude": gps_pos[0],
                        "longitude": gps_pos[1],
                        "altitude": gps_pos[2],
                        "visualization": vis_base64
                    }
                }
                message = json.dumps(alert_data) + "\n"
                socket_client.send(message.encode())
                print(f"[INFO] Alert with visualization sent to server")
                

            except Exception as e:
                print(f"[ERROR] Failed to send alert: {e}")
    else:
        print(f"[INFO] All {len(plants)} lettuces are healthy")

    return plants



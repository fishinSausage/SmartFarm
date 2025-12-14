import json
import os

# 클래스 이름 리스트
class_names = ["scrofa", "inermis", "procyonoides", "sibirica", "coreanus", "pygargus"]

# YOLO bbox 변환 함수
def convert_bbox_to_yolo(bbox, img_width, img_height):
    if bbox is None:
        return None
    x_min, y_min = bbox[0]
    x_max, y_max = bbox[1]
    x_center = (x_min + x_max) / 2 / img_width
    y_center = (y_min + y_max) / 2 / img_height
    width = (x_max - x_min) / img_width
    height = (y_max - y_min) / img_height
    return x_center, y_center, width, height

# JSON 파일 읽고 YOLO txt 생성
def json_to_yolo(json_path, output_dir):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for image in data.get("images", []):
        img_filename = image["file_name"]
        img_width = image["width"]
        img_height = image["height"]
        txt_filename = os.path.splitext(img_filename)[0] + ".txt"
        txt_path = os.path.join(output_dir, txt_filename)

        lines = []
        # 해당 이미지의 annotation 찾기
        for ann in data.get("annotations", []):
            bbox = ann.get("bbox")
            yolo_bbox = convert_bbox_to_yolo(bbox, img_width, img_height)
            if yolo_bbox is None:
                continue  # bbox 없는 경우 건너뜀

            class_name = ann.get("category_name")
            if class_name not in class_names:
                continue  # 리스트에 없는 클래스면 건너뜀

            class_id = class_names.index(class_name)
            x, y, w, h = yolo_bbox
            line = f"{class_id} {x:.6f} {y:.6f} {w:.6f} {h:.6f}"
            lines.append(line)

        # txt 파일로 저장
        if lines:
            os.makedirs(output_dir, exist_ok=True)
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(lines))
            print(f"Saved {txt_path}")

# 예시 사용
json_folder = "Validation"  # JSON 파일들이 있는 폴더
output_dir = "Validation_label"      # YOLO txt 저장 폴더

for json_file in os.listdir(json_folder):
    if json_file.endswith(".json"):
        json_to_yolo(os.path.join(json_folder, json_file), output_dir)

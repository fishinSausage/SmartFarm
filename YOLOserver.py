from fastapi import FastAPI, File
from PIL import Image
import io
from ultralytics import YOLO

app = FastAPI()
model = YOLO("best.pt")

@app.post("/detect")
async def detect(file: bytes = File(...)):
    img = Image.open(io.BytesIO(file))
    results = model(img)

    alert_messages = []

    for box in results[0].boxes:  # 첫 번째 이미지
        conf = float(box.conf[0])
        cls = int(box.cls[0])
        if conf > 0.5:
            alert_messages.append(f"Object {cls} detected ({conf:.2f})")

    return "".join(alert_messages)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

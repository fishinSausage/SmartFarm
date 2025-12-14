from ultralytics import YOLO
import cv2

#학습코드

def main():
    model = YOLO("yolo11n.pt")
    model.train(
        data="data.yaml",
        epochs=18,
        imgsz=640,
        save=True,
        device=0
    )

if __name__ == "__main__":
    main()

"""
cap = cv2.VideoCapture(0)


model = YOLO("best.pt")

while True:
    ret, frame = cap.read()
    if not ret:
        break

     #YOLO 객체 검출
    results = model(frame)

    # 결과 그리기
    annotated_frame = results[0].plot()  # detect.py처럼 bounding box 표시

    # 화면에 출력
    cv2.imshow("YOLOv11n Detection", annotated_frame)

    # 'q' 키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

#
# pip install -U ultralytics
#
#
"""

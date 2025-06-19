import numpy as np
from ultralytics import YOLO
import cv2

class YOLODetector:
    def __init__(self,model_path="yolov8n.pt",conf_threshold=0.3):
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold

    def detect(self,frame):
        results = self.model.predict(frame, conf=self.conf_threshold, classes=[0], verbose=False)
        boxes = results[0].boxes

        if boxes is None or len(boxes) == 0:
            return None, frame
        
        max_box = max(boxes,key=lambda b: (b.xyxy[0][2] - b.xyxy[0][0]) * (b.xyxy[0][3] - b.xyxy[0][1]))
        x1,y1,x2,y2 = max_box.xyxy[0]
        cx, cy = int((x1+x2)/2), int((y1+y2)/2)

        if(cx < THRESHOLD_X):
            #invia comando per spo

        conf = max_box.conf[0].item() 
        cls_id = int(max_box.cls[0].item()) 
        cls_name = self.model.names[cls_id] 

        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0,255,0), 2)
        cv2.circle(frame, (cx, cy), 5, (0,0,255), -1)                                               #PUò ESSERE CONSIDERATO COME "PUNTATORE"

        text = f"{cls_name} {conf:.2f}"
        cv2.putText(frame, text, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        return (cx, cy), frame
    
'''
def main():
    detector = YOLODetector()
    cap = cv2.VideoCapture(0)  # Usa la webcam

    if not cap.isOpened():
        print("Cannot open webcam")
        return

    print("Webcam opened, press 'q' to quit")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        center, output_frame = detector.detect(frame)

        cv2.imshow("YOLOv8 Person Detection", output_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
'''

import numpy as np
from ultralytics import YOLO
import cv2

class YOLODetector:
    def __init__(self,model_path="yolov8n.pt",conf_threshold=0.3):
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold

    def detect(self,frame,frame_counter):
        if frame_counter % 3 != 0:
            # Non elaboriamo questo frame, restituiamo None per la posizione e il frame originale
            return None, frame, None

        width = 640
        height = 360

        small_frame = cv2.resize(frame, (width, height))

        results = self.model.predict(small_frame, conf=self.conf_threshold, classes=[0], verbose=False)
        boxes = results[0].boxes

        if boxes is None or len(boxes) == 0:
            return None, frame, len(boxes)
        
        detections = len(boxes)
        
        max_box = max(boxes,key=lambda b: (b.xyxy[0][2] - b.xyxy[0][0]) * (b.xyxy[0][3] - b.xyxy[0][1]))
        x1,y1,x2,y2 = max_box.xyxy[0]

        scale_x = frame.shape[1] / width
        scale_y = frame.shape[0] / height

        x1 = int(x1 * scale_x)
        y1 = int(y1 * scale_y)
        x2 = int(x2 * scale_x)
        y2 = int(y2 * scale_y)

        cx, cy = int((x1+x2)/2), int((y1+y2)/2)

        return (cx, cy), small_frame, detections
   
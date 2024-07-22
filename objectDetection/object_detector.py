import cv2
import cv2.aruco as aruco
import numpy as np # type: ignore
from ultralytics import YOLO

from data_class import Photoformat
from data_class import detectionBoxFormat
class objectDetector:
    def __init__(self,modelName:str) -> None:
        self.model=YOLO(f"config/{modelName}")
        # self.model.to('cuda')
        self.class_names=self.model.names

    def detect(self,frames,times):
        detectionResults=[]
        if len(frames)>0:
            # detect all frames at once to reduce memory usage
            results = self.model(frames)
        #convert yolo format to list of [x center, y bottom, width, height,class id,confidence,time when the frame was taken]
        for i, result in enumerate(results):
            boxes=[]
            for box in result.boxes:
                # YOLO format (center x, center y, width, height)
                x_center, y_center, width, height = box.xywh[0].tolist()
                y_bottom=y_center+(height/2)

                box_id=float(box.cls)
                conf=float(box.conf)
                boxes.append([x_center,y_bottom,width,height,box_id,conf,times[i]])
            detectionResults.append(boxes)
        # detectionResults.append(detectionBoxFormat(frame.camera_name,ids,boxs))
        return detectionResults
    
    def getClassNames(self):
        return self.class_names#{id:"class name"}



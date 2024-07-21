import cv2
# import cv2.cuda as cuda
import cv2.aruco as aruco
import numpy as np # type: ignore
import time


from config.config_io import configIO
from data_class import Photoformat
from data_class import Detectionformat
from constants import aprilTag


class arucoDetector:
    def __init__(self,detectorConfig:dict) -> None:
        print("opencv version", cv2.__version__)
        self.aruco_dict = cv2.aruco.Dictionary_get(getattr(cv2.aruco,detectorConfig['aruco']))
        self.parameters = cv2.aruco.DetectorParameters_create()
        # self.markerDetector = cv2.aruco.detectMarkers(self.aruco_dict, self.parameters)
        self.rejectingIds=detectorConfig["rejectingIds"]
    def detect(self,frame):
        #detect tag corners
        corners = []
        gray = cv2.cvtColor(frame.frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejectedImgPoints =cv2.aruco.detectMarkers(gray,self.aruco_dict, parameters=self.parameters)
        
        #delete rejected ids
        if not ids is None:
            for i in range(len(ids)):
                if ids[i] in self.rejectingIds:
                    corners=np.delete(corners,i,axis=0)
                    ids=np.delete(ids,i,axis=0)
        
        return Detectionformat(frame.camera_name,ids,corners,frame.time_taken)


# class apriltagDetector:
#     def __init__(self) -> None:
#         self.aruco_dict = cv2.aruco.getPredefinedDictionary(aruco.DICT_APRILTAG_36H11)
#         self.parameters = cv2.aruco.DetectorParameters()
#         self.markerDetector = cv2.aruco.ArucoDetector(self.aruco_dict, self.parameters)

#     def detect(self,frames:list,):
#         result=[]
#         # Detect ArUco markers
#         for frame in frames:
#             corners, id, rejectedImgPoints = self.markerDetector.detectMarkers(frame.frame)
#             filteredIds:list = apriltagConfig["filteredIds"]
#         for i in filteredIds:
#             if id == i:
#                 return Detectionformat(frame.camera_name,id,corners)
#             else: 
#                 pass
#         return result



import cv2
import numpy as np  # type: ignore
from wpimath.geometry import * 

from data_class import RobotPoseFormat

import unit

class PoseEstimator:
    def __init__(self,cameraConfig: dict,tagLayout:list) -> None:
        self.camerasToRobot:dict={}
        for camera in cameraConfig:
            self.camerasToRobot[str(camera["name"])]=unit.poseDictToWPITransform3d(camera["pose"]).inverse()
        self.tagLayout:dict={}
        for tag in tagLayout:
            self.tagLayout[str(tag["ID"])]=unit.poseDictToWPIPose3d(tag["pose"])

    def getRobotPose(self,cameraId:int,tagId:int,cameraToTag):# apply transformation
        fieldToTag=self.tagLayout[str(tagId)]
        return fieldToTag.transformBy(cameraToTag.inverse()).transformBy(self.camerasToRobot[cameraId])
    
    def getRobotPoses(self,cameraToTagPoses:list)->list:
        robotPosesForOneCamera=[]
        cameraToRobot=self.camerasToRobot[cameraToTagPoses.camera_name]
        for i in range(len(cameraToTagPoses.poses)):
          fieldToTag=self.tagLayout[str(cameraToTagPoses.ids[i][0])]
          robotPose=fieldToTag.transformBy(unit.pose3dToTransform3d(cameraToTagPoses.poses[i]).inverse()).transformBy(cameraToRobot)
          robotPosesForOneCamera.append(RobotPoseFormat(robotPose,cameraToTagPoses.errors[i][0],cameraToTagPoses.time_taken))
        return robotPosesForOneCamera

if __name__ == "__main__":
    p=PoseEstimator({
      "pose":{
        "x":0,
        "y":0,
        "z":0,
        "roll":0,
        "pitch":0,
        "yaw":0
        
      }
    },[
    {
      "ID": 1,
      "pose": {
        "translation": {
          "x": 15.079471999999997,
          "y": 0.24587199999999998,
          "z": 1.355852
        },
        "rotation": {
          "quaternion": {
            "W": 0.5000000000000001,
            "X": 0.0,
            "Y": 0.0,
            "Z": 0.8660254037844386
          }
        }
      }
    }])
    robotp=p.getRobotPose(1,Transform3d(Translation3d(0,0,0),Rotation3d(0,0,0)))
    print(robotp)
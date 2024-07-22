import cv2
import numpy as np  # type: ignore
from wpimath.geometry import * # type: ignore
import math
import unit

class poseEstimator:
    def __init__(self,cameraConfig: list) -> None:
        self.robotToCameras:list=[]
        for camera in cameraConfig:
            self.robotToCameras.append(unit.poseDictToWPIPose3d(camera["pose"]))

    def normalizeAngle(self,cameraRotationToRobot:Rotation3d, objectAngleToCamera:Rotation3d):#convert object to camera angle to object to robot angle
        objectAngleToRobot=objectAngleToCamera.rotateBy(unit.inverseRotation(cameraRotationToRobot))
        return objectAngleToRobot
    def getObjectToCameraPose(self,cameraHeight:float,normalizedAngle:Rotation3d):# calculate object pose from camera using it's angle and camera to robot pose
        pitch=normalizedAngle.Y()
        
        x=-cameraHeight/math.tan(pitch)
        y=x*math.tan(normalizedAngle.Z())
        objectPose=Translation2d(x,y)
        return objectPose
    def getObjectToRobotPose(self,CameraToObject:Translation2d,robotToCamera:Pose2d):# transform camera to object pose to robot to object pose
        robotToObjectPose=robotToCamera.transformBy(unit.pose2dToTransform2d(Pose2d(CameraToObject,Rotation2d(0))))
        return robotToObjectPose
    
    def getPoses(self,anglesResult):
        poses=[]
        for i, camera in enumerate(anglesResult):
            for objectAngle in camera:
                objectAngleToCamera=Rotation3d(0,objectAngle[1],objectAngle[0])
                objectAngleToRobot=self.normalizeAngle(objectAngleToCamera,self.robotToCameras[i].rotation())
                objectToCameraPose=self.getObjectToCameraPose(self.robotToCameras[i].Z(),objectAngleToRobot)
                
                robotToObjectPose=self.getObjectToRobotPose(objectToCameraPose,self.robotToCameras[i].toPose2d())
                pose=objectAngle
                pose[0]=robotToObjectPose.X()
                pose[1]=robotToObjectPose.Y()
                poses.append(pose)
        return poses
            

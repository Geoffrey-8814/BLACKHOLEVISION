import cv2
import numpy as np  # type: ignore
from wpimath.geometry import * # type: ignore

import unit
from data_class import RobotPoseFormat

class multiTagPoseEstimator:
    def __init__(self,tagPoseEstimatorConfig: dict, cameraConfig: dict,tagLayout:list) -> None:
        self.tagSize = tagPoseEstimatorConfig["tagSize"]
        self.cameraMatrixs:dict={}
        self.distortionCoeffs:dict={}
        #convert calibration information to a dict so that it can be called using it's name
        for camera in cameraConfig:
            self.cameraMatrixs[str(camera["name"])]=np.array(camera['cameraMatrix'])
            self.distortionCoeffs[str(camera["name"])] = np.array(camera["distortionCoeffs"])
        #create a cameras pose dict
        self.camerasToRobot:dict={}
        for camera in cameraConfig:
            self.camerasToRobot[str(camera["name"])]=unit.poseDictToWPITransform3d(camera["pose"]).inverse()
        #create a dict of the four corners of all the tags
        self.cornerPoses:dict={}
        for tag in tagLayout:
            tagPose=unit.poseDictToWPIPose3d(tag["pose"])
            corner0=tagPose+Transform3d(Translation3d(0.0,self.tagSize/2.0,-self.tagSize/2.0),Rotation3d())
            corner1=tagPose+Transform3d(Translation3d(0.0,-self.tagSize/2.0,-self.tagSize/2.0),Rotation3d())
            corner2=tagPose+Transform3d(Translation3d(0.0,-self.tagSize/2.0,self.tagSize/2.0),Rotation3d())
            corner3=tagPose+Transform3d(Translation3d(0.0,self.tagSize/2.0,self.tagSize/2.0),Rotation3d())
            tagObjectPoints=[
                unit.wpilibTranslationtoOpenCv(corner0.translation()),
                unit.wpilibTranslationtoOpenCv(corner1.translation()),
                unit.wpilibTranslationtoOpenCv(corner2.translation()),
                unit.wpilibTranslationtoOpenCv(corner3.translation())
            ]
            self.cornerPoses[str(tag["ID"])]=tagObjectPoints
    def getRobotPoses(self,detection):
        self.robotPoses:dict={}
        if len(detection.corners)>0:
            objectPoints:list=[]
            observedPoints:list=[]
            #create the object points (observed corners' pose)
            for i in range(len(detection.corners)):
                observedPoints.extend(detection.corners[i][0])
                objectPoints.extend(self.cornerPoses[str(detection.ids[i][0])])
            # print("object points:",objectPoints)
            # print("observed points:",observedPoints)

            #get opencv pose(field to camera)
            try:
                _, rvecs, tvecs, errors = cv2.solvePnPGeneric(np.array(objectPoints), np.array(observedPoints),
                                                                    np.array(self.cameraMatrixs[str(detection.camera_name)]),
                                                                    np.array(self.distortionCoeffs[str(detection.camera_name)]),
                                                                    flags=cv2.SOLVEPNP_SQPNP)
            except:
                raise Exception("Failed to solvePnP")  

            #convert it to wpi pose      
            cameraToFieldPose=unit.openCvPoseToWpilib(tvecs[0],rvecs[0])
            #transform it to field to robot pose
            cameraToField=Transform3d(cameraToFieldPose.translation(),cameraToFieldPose.rotation())
            fieldToCamera=cameraToField.inverse()
            fieldToCameraPose=Pose3d(fieldToCamera.translation(),fieldToCamera.rotation())
            cameraToRobot=self.camerasToRobot[detection.camera_name]
            robotPose=RobotPoseFormat(fieldToCameraPose.transformBy(cameraToRobot),errors[0][0],detection.time_taken)
            return robotPose
        return None


if __name__ == "__main__":
    pass
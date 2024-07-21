import cv2
import numpy as np  # type: ignore
import unit
from data_class import Detectionformat
from data_class import CameraPosesFormat

class CameraPoseEstimator:
    def __init__(self, tagPoseEstimatorConfig: dict, cameraConfig: dict) -> None:
        self.tagSize = tagPoseEstimatorConfig["tagSize"]
        self.cameraMatrixs:dict={}
        self.distortionCoeffs:dict={}

        #convert calibration information to a dict so that it can be called using it's name
        for camera in cameraConfig:
            self.cameraMatrixs[str(camera["name"])]=np.array(camera['cameraMatrix'])
            self.distortionCoeffs[str(camera["name"])] = np.array(camera["distortionCoeffs"])
        
        #get object points
        self.objectPoints = np.array(((-self.tagSize / 2, self.tagSize / 2, 0),
                                      (self.tagSize / 2, self.tagSize / 2, 0),
                                      (self.tagSize / 2, -self.tagSize / 2, 0),
                                      (-self.tagSize / 2, -self.tagSize / 2, 0)))

    def getPose(self, detection):
        # print("corners:",detection.corners)
        cameraPoses=[]
        poseErrors=[]
        tagIds=[]
        
        if len(detection.corners)>0:
            for i in range(len(detection.corners)):
                # print("corners:",tagCorners.corners[0][0])
                # print("self.objectPoints:",self.objectPoints)
                # print("cameraMatrixs:",np.array(self.cameraMatrixs[str(tagCorners.camera_name)]))
                # print("distorationCoedds:",self.distortionCoeffs[str(tagCorners.camera_name)])
                # corners format [[[points]]] there are one more []


                #use the solve pnp method to calculate the pose of the tag relative to the camera
                try:
                    _, rvecs, tvecs, errors = cv2.solvePnPGeneric(self.objectPoints, np.array(detection.corners[i]),
                                                                np.array(self.cameraMatrixs[str(detection.camera_name)]),
                                                                np.array(self.distortionCoeffs[str(detection.camera_name)]))
                except:
                    raise Exception("Failed to solvePnP")
                
                #convert tvec and rvect to wpi pose3d
                wpiPose0=unit.openCvPoseToWpilib(tvecs[0],rvecs[0])

                #add results to lists
                cameraPoses.append(wpiPose0)
                poseErrors.append(errors[0])
                tagIds.append(detection.ids[i])
                i=i+1
                        
        return CameraPosesFormat(detection.camera_name,tagIds,cameraPoses,poseErrors,detection.time_taken)
                    


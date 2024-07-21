import math
from wpimath.geometry import * # type: ignore
import numpy as np  # type: ignore

def poseDictToWPIPose3d(poseDict:dict):
    try:
        return Pose3d(poseDict["x"],poseDict["y"],poseDict["z"],
                    Rotation3d(poseDict["roll"],poseDict["pitch"],poseDict["yaw"]))
    except:
        rotation=poseDict["rotation"]["quaternion"]
        return Pose3d(poseDict["translation"]["x"],poseDict["translation"]["y"],poseDict["translation"]["z"],
                    Rotation3d(Quaternion(rotation["W"],rotation["X"],rotation["Y"],rotation["Z"])))
    
def poseDictToWPITransform3d(poseDict:dict):
    return Transform3d(Translation3d(poseDict["x"],poseDict["y"],poseDict["z"]),
                  Rotation3d(poseDict["roll"],poseDict["pitch"],poseDict["yaw"]))
def pose3dToTransform3d(pose):
    return Transform3d(pose.translation(),pose.rotation())
def pose2dToTransform2d(pose):
    return Transform2d(pose.translation(),pose.rotation())


def wpilibTranslationtoOpenCv(translation:Translation3d):
    return [-translation.Y(),-translation.Z(),translation.X()]

def openCvPoseToWpilib(tvec,rvec)->Pose3d:
    return Pose3d(
        Translation3d(tvec[2][0],-tvec[0][0],-tvec[1][0]),
        Rotation3d(
            np.array([rvec[2][0],-rvec[0][0],-rvec[1][0]]),
            math.sqrt(math.pow(rvec[0][0],2)+math.pow(rvec[1][0],2)+math.pow(rvec[2][0],2))
        )
    )

def robotPoseToList(robotPose):
        if not robotPose is None:
            pose=robotPose.pose
            error=robotPose.error
            time_taken=robotPose.time_taken
            return [pose.X(),pose.Y(),pose.Z(),pose.rotation().X(),pose.rotation().Y(),pose.rotation().Z(),error,time_taken]
        return [0,0,0,0,0,0,-1,0]
def listToRobotPose(robotPose):
        try:
             return Pose3d(
                Translation3d(robotPose[0],robotPose[1],robotPose[2]),
                Rotation3d(robotPose[3],robotPose[4],robotPose[5])),robotPose[6]
        except:
             return None


def inverseRotation(rotation):
        quaternion=rotation.getQuaternion()
        quaternion=quaternion.inverse()
        inversedRotation=Rotation3d(quaternion)
        return inversedRotation
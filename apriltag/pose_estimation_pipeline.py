

import ctypes
from multiprocessing import Process, Queue

from shareData import SharedArray, SharedValue

import time

from apriltag.camera_pose_estimator import CameraPoseEstimator
from apriltag.apriltag_detector import arucoDetector
from apriltag.pose_estimator import PoseEstimator
from apriltag.multi_tag_pose_estimator import multiTagPoseEstimator
import unit

from data_class import Photoformat


class poseEstimationPipeline:
    
    def pipeline(self,run,cameraConfig,frameSharedArray,resultSharedArray,timeTakenSharedValue,detector,m_cameraPoseEstimator,robotPoseEstimator,multiTagPoseEstimator):
        while run.get()==1:
            timeTaken=timeTakenSharedValue.get()#get the time that the frame was taken
            frame=Photoformat(cameraConfig["ID"],cameraConfig["name"],timeTaken,frameSharedArray.get())#add meta data to the frame 
            detection=detector.detect(frame)# get the corners

            #calculate robot pose using each tag
            cameraPoses:list = m_cameraPoseEstimator.getPose(detection)#get tag to camera pose
            
            robotPoses:list=robotPoseEstimator.getRobotPoses(cameraPoses)#get field to robot pose
            
            #calculate robot pose using all tags in the frame
            multiTagRobotPose=multiTagPoseEstimator.getRobotPoses(detection)
            # print("robotPoses multiTag:",self.robotPoses)
            
            #convert wpi pose to list so that it can be saved to shared array
            listPoses=[unit.robotPoseToList(multiTagRobotPose)]
            for i in range(3):
                try:
                    listPoses.append(unit.robotPoseToList(robotPoses[i]))
                except:
                    listPoses.append([0,0,0,0,0,0,-1,0])
            #save to shared array
            resultSharedArray.put(listPoses)

    def __init__(self,config:dict,tagLayout:list) -> None:
        self.cameraNames=[]
        self.frameSharedArrays=[]
        self.resultSharedArrays=[]
        self.timeTakenSharedValue=[]
        self.processes=[]
        self.run=SharedValue(ctypes.c_double)
        self.run.set(1)

        self.poseResult:dict={}
        self.config:dict={}
        self.tagLayout:dict={}
        self.detector=arucoDetector(config["apriltagDetector"])
        self.m_cameraPoseEstimator=CameraPoseEstimator(config["tagPoseEstimator"],config["cameras"])
        self.robotPoseEstimator = PoseEstimator(config["cameras"], tagLayout)
        self.multiTagPoseEstimator=multiTagPoseEstimator(config["tagPoseEstimator"],config["cameras"],tagLayout)
        self.config=config
        self.tagLayout=tagLayout
        captureConfig=config["capture"]
        
        #create a pipeline for each camera
        for cameraConfig in config["cameras"]:
            frameSharedArray=SharedArray((captureConfig["resolution"]["height"], captureConfig["resolution"]["width"], 3),ctypes.c_uint8)
            resultSharedArray=SharedArray((4,8),ctypes.c_double)
            sharedValue=SharedValue(ctypes.c_double)
            p=Process(target=self.pipeline,args=(
                self.run,cameraConfig,frameSharedArray,resultSharedArray,sharedValue,self.detector,self.m_cameraPoseEstimator,self.robotPoseEstimator,self.multiTagPoseEstimator))
            p.start()
            self.processes.append(p)
            self.frameSharedArrays.append(frameSharedArray)
            self.resultSharedArrays.append(resultSharedArray)
            self.cameraNames.append(cameraConfig["name"])
            self.timeTakenSharedValue.append(sharedValue)
    def update(self, frames:Photoformat):#updata frames
        for frame in frames:
            i=self.cameraNames.index(frame.camera_name)
            self.frameSharedArrays[i].put(frame.frame)
            self.timeTakenSharedValue[i].set(frame.time_taken)
    def updateConfig(self,config):
        self.release()
        self.__init__(config,self.tagLayout)

    def release(self):
        self.run.set(0)
        for process in self.processes:
            process.join()
        self.cameraNames=[]
        self.frameSharedArrays=[]
        self.resultSharedArrays=[]
        self.timeTakenSharedValue=[]
        self.processes=[]

    def getPoses(self):#get pose from each pipeline
        results={}
        for i in range(len(self.cameraNames)):
            poses=self.resultSharedArrays[i].get().tolist()# get list
            multiTagPose=poses[0]
            #delete all the unvalid list
            if multiTagPose[7]==0:
                multiTagPose=[]
            poses.pop(0)
            robotPoses=[]
            for pose in poses:
                if pose[7] != 0.0:
                    robotPoses.append(pose)
            #convert to dict
            result={self.cameraNames[i]:{'multiTagRobotPose':multiTagPose,'robotPoses':robotPoses}}
            results.update(result)
        return results 
    

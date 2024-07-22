import ctypes
from ultralytics import YOLO

import cv2
import time
import threading
from multiprocessing import Process, Queue , set_start_method

from objectDetection.object_detector import objectDetector
from objectDetection.angle_estimator import angleEstimator
from objectDetection.pose_estimator import poseEstimator

from data_class import Photoformat

from shareData import SharedArray, SharedValue

class objectDetectionPipeline:

    
    resultSharedArray=SharedArray((10,7),ctypes.c_double)
    

    def pipeline(self,run,framesSharedArrays,timeTakenSharedValues,resultSharedArray,detector,angleEstimator,poseEstimator):
        while run.get()==1:
            frames=[]
            times=[]
            for i,frameSharedArray in enumerate(framesSharedArrays):
                frames.append(frameSharedArray.get())
                times.append(timeTakenSharedValues[i].get())
            boxes=detector.detect(frames,times)
            angles=angleEstimator.getObjectAngles(boxes)
            poses=poseEstimator.getPoses(angles)#[x,y,height,width,class,confidence,time]
            print(poses)
            while len(poses)<10:
                poses.append([0,0,0,0,0,-1,0])
            returePoses=poses[:10]
            resultSharedArray.put(returePoses)

    def __init__(self,config:dict) -> None:
        self.cameraNames=[]
        self.frameSharedArrays=[]
        self.timeTakenSharedValues=[]
        self.config=config
        self.detector=objectDetector(config["objectDetection"]["modelName"])
        self.angleEstimator=angleEstimator(config["cameras"])
        self.poseEstimator=poseEstimator(config["cameras"])
        self.run=SharedValue(ctypes.c_double)
        self.run.set(1)
        captureConfig=config["capture"]
        for cameraConfig in config["cameras"]:
            frameSharedArray=SharedArray((captureConfig["resolution"]["height"], captureConfig["resolution"]["width"], 3),ctypes.c_uint8)
            sharedValue=SharedValue(ctypes.c_double)
            self.frameSharedArrays.append(frameSharedArray)
            self.cameraNames.append(cameraConfig["name"])
            self.timeTakenSharedValues.append(sharedValue)
        self.process=Process(target=self.pipeline,args=(
            self.run,self.frameSharedArrays,self.timeTakenSharedValues,self.resultSharedArray,self.detector,self.angleEstimator,self.poseEstimator))
        self.process.start()
    def update(self, frames:Photoformat):
        for frame in frames:
            i=self.cameraNames.index(frame.camera_name)
            self.frameSharedArrays[i].put(frame.frame)
            self.timeTakenSharedValues[i].set(frame.time_taken)
    def updateConfig(self,config):
        self.release()
        self.__init__(config)
    def release(self):
        self.run.set(0)
        self.process.join()

    def getPoses(self):
        rawResults=self.resultSharedArray.get().tolist()
        results=[]
        for i in range(len(self.detector.getClassNames())):
            results.append([])
        for pose in rawResults:
            if pose[6] > 0:
                index=int(pose[4])
                pose.pop(4)
                results[index].append(pose)
        return results
    def getClasses(self):
        return self.detector.getClassNames()
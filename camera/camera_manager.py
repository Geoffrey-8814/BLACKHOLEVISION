import ctypes
from multiprocessing import Process, Queue

from shareData import SharedArray,SharedValue

from camera import opencv_capture
from camera import gstreamer_capture
from data_class import Photoformat
import cv2
import time

class CameraManager:
    
    def __init__(self, config) ->None:
        self.config=config
        cameraConfigs=config["cameras"]
        captureConfig=config["capture"]
        self.cameras = []
        self.result = []

        self.processes=[]
        self.frameSharedArray=[]
        self.timeTakenSharedValue=[]
        self.run=SharedValue(ctypes.c_double)
        self.run.set(1)
        self.size=(captureConfig["resolution"]["width"],captureConfig["resolution"]["height"])
        #create a pipeline for each camera
        for cameraConfig in cameraConfigs:
            camera=opencv_capture.OpencvCapture(cameraConfig["ID"],cameraConfig["name"], captureConfig)#create camera
            self.cameras.append(camera)#add camera to list
            sharedArray=SharedArray((captureConfig["resolution"]["height"], captureConfig["resolution"]["width"], 3),ctypes.c_uint8)
            sharedValue=SharedValue(ctypes.c_double)
            self.frameSharedArray.append(sharedArray)
            self.timeTakenSharedValue.append(sharedValue)
            p=Process(target=self.readFrame,args=(self.run,sharedArray,sharedValue,camera))
            p.start()
            self.processes.append(p)

    def readFrame(self,run,frameSharedArray,timeTakenSharedValue,camera):
        while run.get()==1:
            frame = camera.getFrame()

            frame=cv2.resize(frame,self.size)# resize the frame so that it's shape can be saved to shared array
            frameSharedArray.put(frame)
            timeTakenSharedValue.set(time.time())
    def getResult(self):
        self.result = []
        # print(len(self.frameSharedArray))
        #get all the frame from shared arrays
        for i in range(len(self.cameras)):
            #get the frame and convert it to Photoformat
            photo=Photoformat(self.cameras[i].getID(),self.cameras[i].getName(),self.timeTakenSharedValue[i].get(),self.frameSharedArray[i].get())
            self.result.append(photo)
        # print("get time",time.time()-s)
        return self.result
    def updateConfig(self,config):
        self.release()
        self.__init__(config)
    def release(self):
        self.run.set(0)
        for process in self.processes:
            process.join()
        for camera in self.cameras:
            camera.release()
        self.processes=[]
        self.frameSharedArray=[]
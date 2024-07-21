import cv2
import os
import numpy as np # type: ignore
import logging
import sys

from camera.camera_manager import CameraManager
import time
from config.config_io import configIO
from apriltag.pose_estimation_pipeline import poseEstimationPipeline
from calibration.detect_corners import detectCorners
from calibration.record_video import recordVideo
from data_class import Photoformat
from output.network_table import NTables

from objectDetection.object_detection_pipeline import objectDetectionPipeline

from output.Interface import app



app.initialize()
def updateConfig():
    config["capture"]["resolution"]["height"] = app.camera_settings["camera1"]["resolution"][0]
    config["capture"]["resolution"]["width"] = app.camera_settings["camera1"]["resolution"][1]
    config["capture"]["FPS"]= app.camera_settings["camera1"]["frame_rate"]
    config["capture"]["autoExposure"] = app.autoexposure
    config["capture"]["exposure"] = app.exposure
    config["output"]["networkTable"]["teamNumber"] = app.teamNumber
    config["cameras"][0]["pose"]["x"]= app.x
    config["cameras"][0]["pose"]["y"]= app.y
    config["cameras"][0]["pose"]["z"]= app.z
    config["cameras"][0]["pose"]["roll"]= app.roll
    config["cameras"][0]["pose"]["pitch"]= app.pitch
    config["cameras"][0]["pose"]["yaw"]= app.yaw
    
while True:
    m_networktable = NTables("1001")
    #get config
    m_config = configIO()
    config=m_networktable.getConfig()

    # config:dict = m_config.load_config("config/config.json")
    tagLayout:list=(m_config.load_config("config/aprilTagFieldLayout.json"))["tags"]
    #initialize
    m_cameraManager = CameraManager(config)
    m_apriltagPipline = poseEstimationPipeline(config,tagLayout)
    # m_videoRecorder= recordVideo("/home/jetson/Desktop/BlackHoleVision/BlackHoleVision1.0(6,2,2024)/calibration/calibration_videos")

    # m_calibrate = Calibration(config["Calibration"])

    m_calibration=detectCorners(config["Calibration"])

    m_networktable.createTable(config)
    m_objectDetectionPipeline = objectDetectionPipeline(config)

    calibrationCamera=None

    while True:
        #get capture result
        startTime=time.time()
        frames:list= m_cameraManager.getResult()
        
        key=cv2.waitKey(1)
        
        if True:
            #update apriltag pipline frame
            m_apriltagPipline.update(frames)
            #get apriltag pipline result
            robotPoses=m_apriltagPipline.getPoses()
        if True:
            
            #update object detection pipline frame
            m_objectDetectionPipeline.update(frames)
            
            #get object pipline result
            objectPoses=m_objectDetectionPipeline.getPoses()
        #output
        m_networktable.sendRobotPose(robotPoses)
        m_networktable.sendObjectPose(objectPoses,m_objectDetectionPipeline.getClasses())
        updateConfig()

        # camera calibration:
        # if True:
        #     if key& 0xFF ==ord('s'):
        #         calibrationCamera=None
        #     if key& 0xFF ==ord('c'):
        #         calibrationCamera="testCamera"
        #     calibrationResult=m_calibration.readCorners(frames,calibrationCamera)
        #     if not calibrationResult is None:
        #         for i in range(len(config["cameras"])):
        #             if config["cameras"][i]["name"] == calibrationResult.camera_name:
        #                 config["cameras"][i]["cameraMatrix"]=calibrationResult.cameraMatrix.tolist()
        #                 config["cameras"][i]["distortionCoeffs"]=calibrationResult.dist_coeffs.tolist()
        #         print(config)
        
        #display frame
        for frame in frames:
            cv2.imshow(f"{frame.camera_name}",frame.frame)
        # print("loop running")

        if key& 0xFF ==ord('q'):
            break

        # if m_networktable.configChanged():
        #     cv2.destroyAllWindows()
        #     config=m_networktable.getConfig()
        #     time.sleep(60)
        #     m_apriltagPipline.updateConfig(config)
        #     m_objectDetectionPipeline.updateConfig(config)
        #     m_cameraManager.updateConfig(config)
        print("time:",time.time()-startTime)
        # elapsedTime=time.time()-startTime
        # sleepTime=0.02-elapsedTime
        # if(sleepTime>0):
        #     time.sleep(sleepTime)
        
    m_cameraManager.release()
    m_apriltagPipline.release()
    m_objectDetectionPipeline.release()
    break
  
    

import json
from networktables import NetworkTables
import time
import numpy as np

from data_class import RobotPoseFormat

class NTables: 
    def __init__(self,teamNumber) -> None:
        self.roboRIO_hostname = f'roborio-{teamNumber}-frc.local'
        
        # Initialize NetworkTables
        self.initializeNetworkTable()

        self.SmartDashboard=NetworkTables.getTable("SmartDashboard")

        self.objectDetectionTables=[]

    def createTable(self,config):
        self.datatables = {}
        for camera in config["cameras"]: 
            self.datatables[camera["name"]]=NetworkTables.getTable(camera["name"])
    def initializeNetworkTable(self):
        NetworkTables.initialize(server=self.roboRIO_hostname)
    def getConfig(self):
        while not NetworkTables.isConnected():
            self.initializeNetworkTable
        configString=""
        while configString == "":
            configString=self.SmartDashboard.getString("config","")
            
        return json.loads(configString)
    def configChanged(self):
        string=self.SmartDashboard.getString("config","")
        return string == ""
    def sendRobotPose(self, result: dict):
        # print(result)
        if not NetworkTables.isConnected():
            self.initializeNetworkTable()

        for name in self.datatables:
            try:
                multiTagPose = result[name]['multiTagRobotPose']
                robotPoses:list=result[name]['robotPoses']
                multiTagPose[7]=time.time()-multiTagPose[7]
                for robotPose in robotPoses:
                    robotPose[7]=time.time()-robotPose[7]
            except:
                multiTagPose=[]
                robotPoses=[]
            
            robotPoses=self.sortPoses(robotPoses)
            tagAmount=0
            self.datatables[name].putNumberArray("multiTagRobotPose",multiTagPose)
            for i in range(3):
                try:
                    self.datatables[name].putNumberArray(f"pose{i}",robotPoses[i])
                    tagAmount+=1
                except:
                    self.datatables[name].putNumberArray(f"pose{i}",[])
            self.datatables[name].putNumber("tagAmount",tagAmount)
    def robotPoseToList(self,robotPose:RobotPoseFormat):
        pose=robotPose.pose
        error=robotPose.error
        return [pose.X(),pose.Y(),pose.Y(),pose.rotation().X(),pose.rotation().Y(),pose.rotation().Z(),error]
    def sortPoses(self,robotPoses:list):
        for n in range(len(robotPoses)-1):
            for i in range(len(robotPoses)-n-1):
                if robotPoses[i][6]>robotPoses[i+1][6]:
                    robotPoses[i],robotPoses[i+1]=robotPoses[i+1],robotPoses[i]
        return robotPoses

    def sendObjectPose(self, results: list,objectClasses:list):
        if len(self.objectDetectionTables)==0:
            for objectClass in objectClasses.values():
                self.objectDetectionTables.append(NetworkTables.getTable(objectClass))
        # print(result)
        for i,objectClass in enumerate(results):
            for pose in objectClass:
                pose[5]=time.time()-pose[5]
            npResults=np.array(objectClass)
            npResults=npResults.flatten()
            results=npResults.tolist()
            self.objectDetectionTables[i].putNumberArray("poses",results)

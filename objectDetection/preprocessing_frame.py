import cv2

class preprocessingFrame:
    def __init__(self,cameraConfigs) -> None:
        self.cameraRolls=[]
        for cameraConfig in cameraConfigs:
            self.cameraRolls.append(cameraConfig["pose"]["roll"])
        pass
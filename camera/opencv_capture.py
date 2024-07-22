import cv2

class OpencvCapture:

    def  __init__(self,id:int,name:str,captureConfig:dict) -> None:
        self.name=name
        self.id=id
        #create the camera
        self.videoCapture = cv2.VideoCapture()
        self.videoCapture.open(self.id)
        self.videoCapture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc(*'MJPG'))#this should be the first, without this the camera will run in 5fps for arducam
        self.videoCapture.set(cv2.CAP_PROP_SETTINGS,0)#reset to defualt
        self.videoCapture.set(cv2.CAP_PROP_FRAME_WIDTH, captureConfig["resolution"]["width"])# set frame width
        self.videoCapture.set(cv2.CAP_PROP_FRAME_HEIGHT, captureConfig["resolution"]["height"])# set frame height
        self.videoCapture.set(cv2.CAP_PROP_AUTO_EXPOSURE, captureConfig["autoExposure"])# Disable auto exposure
        self.videoCapture.set(cv2.CAP_PROP_EXPOSURE, captureConfig["exposure"])# Set exposure value
        self.videoCapture.set(cv2.CAP_PROP_GAIN, captureConfig["gain"])# Set sensor gain
        self.videoCapture.set(cv2.CAP_PROP_FPS, captureConfig["FPS"])# Set FPS
        # self.videoCapture.set(cv2.CAP_PROP_BRIGHTNESS, captureConfig["brightness"])# Set brightness
        # self.videoCapture.set(cv2.CAP_PROP_CONTRAST, captureConfig["contrast"])# Set contrast



        if not self.videoCapture.isOpened():
           print(f"Could not open camera {id}")
           raise Exception(f"Could not open camera {id}") 
        else:
            print("opened")
        self.frame=None
    
    def getFrame(self):
        ret,frame=self.videoCapture.read()
        if ret:
            return frame
        else:    
            raise Exception(f"Failed to capture frame with camera {self.id}") 
    def getID(self):
        return self.id
    def getName(self):
        return self.name
    def release(self):
        self.videoCapture.release()
    
if __name__=="__main__":
    pass
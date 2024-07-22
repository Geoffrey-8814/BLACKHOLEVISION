import cv2
import numpy as np

class angleEstimator:
    def __init__(self,cameraConfig) -> None:
        self.cameraMatrixs:list=[]
        self.distortionCoeffs:list=[]
        #convert calibration information to a dict so that it can be called using it's name
        for camera in cameraConfig:
            self.cameraMatrixs.append(np.array(camera['cameraMatrix']))
            self.distortionCoeffs.append(np.array(camera["distortionCoeffs"]))

    def getAngle(self,x,y,camera_matrix,dist_coeffs):# calculate angle from pixel on the frame
        # 2D image points (example values, use your detected coordinates)
        image_points = np.array([[x, y]], dtype=np.float32)

        # Step 1: Normalize the image coordinates
        normalized_points = cv2.undistortPoints(image_points, camera_matrix, dist_coeffs)

        # Step 2: Correct for distortion (since undistortPoints already corrects for distortion, this step is integrated)
        # The output of undistortPoints are the corrected normalized coordinates

        # Extract the corrected normalized coordinates
        normalized_corrected_x = normalized_points[0][0][0]
        normalized_corrected_y = normalized_points[0][0][1]

        # Step 3: Calculate the angles in radian
        angle_x = np.arctan(normalized_corrected_x)
        angle_y = np.arctan(normalized_corrected_y)

        return angle_x,angle_y

    def getObjectAngles(self,detectionResults):
        allFrameresult=[]
        for i, detectionResult in enumerate(detectionResults):
            oneFrameResult=[]
            for object in detectionResult:
                # get the angle from the bottom of the object to the camera
                angle_x, angle_y=self.getAngle(object[0],object[1],self.cameraMatrixs[i],self.distortionCoeffs[i])
                angle=object
                angle[0]=angle_x
                angle[1]=angle_y
                oneFrameResult.append(angle)
            allFrameresult.append(oneFrameResult)
        return allFrameresult
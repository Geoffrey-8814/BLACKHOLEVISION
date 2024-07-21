import cv2
import os
import json
import numpy as np
from typing import List

from data_class import calibrationResultFormat

class detectCorners:
    all_corners: List[np.ndarray] = []
    all_ids: List[np.ndarray] = []
    _imsize = None
    def __init__(self,calibrationConfig:dict):
        self.config=calibrationConfig
        
        charuco_dict_name = self.config['charuco_dict']
        self.charuco_dict = cv2.aruco.Dictionary_get(getattr(cv2.aruco, charuco_dict_name))
        board_config = self.config['charuco_board']
        self.charuco_board = cv2.aruco.CharucoBoard_create(board_config['squares_x'], board_config['squares_y'], 
                                                    board_config['square_length'], 
                                                    board_config['marker_length'], 
                                                    self.charuco_dict)
        self.current_name = None

    def readCorners(self, frames: list, camera_name: str):
        if  camera_name != self.current_name:
            if len(self.all_corners) > 0 and self._imsize != None:
                print("calculating calibration...")
                camera_matrix = np.zeros((3, 3))
                dist_coeffs = np.zeros((5, 1))
                ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.aruco.calibrateCameraCharuco(
                charucoCorners = self.all_corners,
                charucoIds = self.all_ids,
                board = self.charuco_board,
                imageSize = self._imsize,
                cameraMatrix = camera_matrix,
                distCoeffs = dist_coeffs)
                print("calibrated")
                print(camera_matrix)
                print(dist_coeffs)
                calibratedCameraName=self.current_name
                self.current_name=camera_name
                return calibrationResultFormat(calibratedCameraName,camera_matrix,dist_coeffs)
            self.current_name=camera_name
        frame=None
        if camera_name != None:
            for f in frames: 
                if camera_name == f.camera_name: 
                    frame = f.frame
                    break
        if not frame is None:
            # Convert frame to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            self._imsize = gray.shape

            # Detect Aruco markers in the image
            corners, ids, _ = cv2.aruco.detectMarkers(gray, self.charuco_dict)
            
            # If markers are detected
            if ids is not None:
                # Interpolate Charuco corners
                ret, charuco_corners, charuco_ids = cv2.aruco.interpolateCornersCharuco(corners, ids, gray, self.charuco_board)

                # If there are enough corners for calibration
                if ret >10:
                    print("saved")
                    self.all_corners.append(charuco_corners)
                    self.all_ids.append(charuco_ids)
        return None
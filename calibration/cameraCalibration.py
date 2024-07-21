import cv2
import numpy as np
import glob
import json
import os
from data_class import CalibrationCoeffs

class Calibration:
    def __init__(self,calibrationConfig:dict):
        self.config=calibrationConfig
        
        charuco_dict_name = self.config['charuco_dict']
        self.charuco_dict = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, charuco_dict_name))
        board_config = self.config['charuco_board']
        self.charuco_board = cv2.aruco.CharucoBoard((board_config['squares_x'], board_config['squares_y']), 
                                                    board_config['square_length'], 
                                                    board_config['marker_length'], 
                                                    self.charuco_dict)
        self.image_path = self.config['image_path']

    def calibrate(self, camera_names: list):
        # Arrays to store detected corners and corresponding ids from all frames
        all_corners = []
        all_ids = []
        gray = None
        results = []
        for camera_name in camera_names:

            # Read the video
            cap = cv2.VideoCapture("calibration/calibration_videos/" + camera_name + ".mp4")

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Convert frame to grayscale
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                 

                # Detect Aruco markers in the image
                corners, ids, _ = cv2.aruco.detectMarkers(gray, self.charuco_dict)

                # If markers are detected
                if ids is not None:
                    # Interpolate Charuco corners
                    ret, charuco_corners, charuco_ids = cv2.aruco.interpolateCornersCharuco(corners, ids, gray, self.charuco_board)

                    # If there are enough corners for calibration
                    if ret >10:
                        all_corners.append(charuco_corners)
                        all_ids.append(charuco_ids)

                # Optional: Display the detected markers and corners
                frame_markers = cv2.aruco.drawDetectedMarkers(frame.copy(), corners, ids)
                if ret >10:
                    frame_markers = cv2.aruco.drawDetectedCornersCharuco(frame_markers, charuco_corners, charuco_ids)
                cv2.imshow('frame', frame_markers)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()
            if gray is not None:
                # Perform camera calibration
                camera_matrix = np.zeros((3, 3))
                dist_coeffs = np.zeros((5, 1))
                ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.aruco.calibrateCameraCharuco(
                    charucoCorners = all_corners,
                    charucoIds = all_ids,
                    board = self.charuco_board,
                    imageSize = gray.shape,
                    cameraMatrix = camera_matrix,
                    distCoeffs = dist_coeffs)
                results.append(CalibrationCoeffs(camera_matrix, dist_coeffs))
            else: 
                print("No video/charuco found")

        return results
from dataclasses import dataclass
from typing import Union
import numpy as np
from wpimath.geometry import * # type: ignore

@dataclass
class Photoformat:
    camera_id: int
    camera_name: str
    time_taken: float
    frame: Union[np.ndarray, None]

@dataclass
class Detectionformat:
    camera_name:str
    ids: int
    corners: Union[np.ndarray, None]
    time_taken: float

@dataclass
class CameraPosesFormat:
    camera_name:int
    ids: int
    poses:list
    errors:list
    time_taken: float

@dataclass
class RobotPoseFormat:
    pose:Pose3d
    error:float
    time_taken: float

@dataclass
class CalibrationCoeffs:
    camera_name: str
    camera_matrix: np.ndarray
    dist_coeffs: np.ndarray

@dataclass
class detectionBoxFormat:
    camera_name:str
    ids: int
    boxs: Union[np.ndarray, None]

@dataclass
class calibrationResultFormat:
    camera_name:str
    cameraMatrix:list
    dist_coeffs:list
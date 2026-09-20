"""
Captures a single frame from the webcam and saves it to disk.
Used by the Intruder Snapshot Module.
"""
import os
from datetime import datetime
from typing import Optional

import cv2

import config


def capture_snapshot(camera_index: int = 0) -> Optional[str]:
    """
    Captures one frame and saves it to intruders/intruder_YYYYmmdd_HHMMSS.jpg
    Returns the saved file path, or None if the webcam couldn't be reached.
    """
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        return None

    ret, frame = cap.read()
    cap.release()
    if not ret:
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"intruder_{timestamp}.jpg"
    filepath = os.path.join(config.INTRUDER_FOLDER, filename)
    cv2.imwrite(filepath, frame)
    return filepath

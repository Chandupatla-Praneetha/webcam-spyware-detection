"""
Face Recognition Module.

NOTE ON TECH SUBSTITUTION:
The original spec listed "OpenCV + face_recognition" (the face_recognition
package is a wrapper around dlib). dlib has no prebuilt wheels for most
Windows/Python combos, so installing it means compiling C++ from source
with CMake + Visual Studio Build Tools -- exactly the kind of build pain
you hit earlier with greenlet, just much worse.

Instead this module uses OpenCV's own LBPH face recognizer (cv2.face,
part of opencv-contrib-python), which needs zero compilation and ships
as a normal pip wheel on Windows. It does the same job: register a face,
store its "encoding" (trained model), and verify a live face against it.
"""
import json
import os
from typing import Optional

import cv2
import numpy as np

import config

_LABELS_FILE = os.path.join(config.FACES_FOLDER, "labels.json")
_HAAR_CASCADE = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"


def _load_labels() -> dict:
    if os.path.exists(_LABELS_FILE):
        with open(_LABELS_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def _save_labels(labels: dict) -> None:
    with open(_LABELS_FILE, "w", encoding="utf-8") as fh:
        json.dump(labels, fh)


def _model_path(username: str) -> str:
    return os.path.join(config.FACES_FOLDER, f"{username}_model.yml")


def is_face_recognition_available() -> bool:
    """
    True only if BOTH conditions hold:
      - cv2.face exists (needs opencv-contrib-python, not plain opencv-python)
      - the Haar cascade XML is actually present on disk.
    NOTE: opencv-contrib-python 5.0.x stopped bundling haarcascade_*.xml files
    (verified: 4.10.0.84 ships them, 5.0.0.93 does not). requirements.txt
    pins <5.0.0 for this reason -- this check exists so that if someone
    upgrades opencv anyway, they get a clear message instead of OpenCV's
    cryptic "!empty()" assertion error deep inside detectMultiScale().
    """
    return hasattr(cv2, "face") and os.path.exists(_HAAR_CASCADE)


def register_admin_face(username: str, camera_index: int = 0,
                         samples: int = config.FACE_SAMPLES_TO_CAPTURE) -> tuple[bool, str]:
    """
    Opens the webcam, captures `samples` face crops, trains an LBPH model,
    and saves it. Call this once per admin during setup.
    """
    if not is_face_recognition_available():
        return False, "Face recognition unavailable: cv2.face missing or haarcascade file not found (check opencv-contrib-python version, must be <5.0.0)."

    cascade = cv2.CascadeClassifier(_HAAR_CASCADE)
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        return False, "Could not access the webcam."

    faces_collected = []
    attempts = 0
    max_attempts = samples * 20  # avoid an infinite loop if no face is ever seen

    while len(faces_collected) < samples and attempts < max_attempts:
        ret, frame = cap.read()
        attempts += 1
        if not ret:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detected = cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)
        for (x, y, w, h) in detected:
            face_roi = cv2.resize(gray[y:y + h, x:x + w], (200, 200))
            faces_collected.append(face_roi)
            break  # one face per frame is enough

    cap.release()

    if len(faces_collected) < max(5, samples // 2):
        return False, f"Only captured {len(faces_collected)} face samples -- try better lighting."

    labels = _load_labels()
    label_id = labels.get(username, len(labels) + 1)
    labels[username] = label_id
    _save_labels(labels)

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces_collected, np.array([label_id] * len(faces_collected)))
    recognizer.save(_model_path(username))

    return True, f"Registered {len(faces_collected)} face samples for '{username}'."


def verify_face(username: str, camera_index: int = 0) -> tuple[bool, str]:
    """
    Captures one live frame and checks it against the stored model for `username`.
    Returns (matched, message).
    """
    if not is_face_recognition_available():
        return False, "Face recognition unavailable: cv2.face missing or haarcascade file not found (check opencv-contrib-python version, must be <5.0.0)."

    model_path = _model_path(username)
    if not os.path.exists(model_path):
        return False, "No face registered for this user yet."

    labels = _load_labels()
    expected_label = labels.get(username)
    if expected_label is None:
        return False, "No face registered for this user yet."

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(model_path)

    cascade = cv2.CascadeClassifier(_HAAR_CASCADE)
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        return False, "Could not access the webcam."

    matched = False
    message = "No face detected."
    for _ in range(30):  # try for ~30 frames to find a face
        ret, frame = cap.read()
        if not ret:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detected = cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)
        if len(detected) == 0:
            continue
        (x, y, w, h) = detected[0]
        face_roi = cv2.resize(gray[y:y + h, x:x + w], (200, 200))
        label, confidence = recognizer.predict(face_roi)
        # LBPH: LOWER confidence value = better match.
        if label == expected_label and confidence <= config.FACE_CONFIDENCE_THRESHOLD:
            matched = True
            message = f"Face matched (confidence {confidence:.1f})."
        else:
            message = f"Face did not match (confidence {confidence:.1f})."
        break

    cap.release()
    return matched, message

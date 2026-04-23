"""
Facial expression service — uses DeepFace to detect emotion from a base64 image.
Install: pip install deepface opencv-python
"""
import base64
import numpy as np
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

DEEPFACE_AVAILABLE = False
try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    pass

DEEPFACE_TO_APP = {
    "happy"   : "joy",
    "sad"     : "sadness",
    "angry"   : "anger",
    "fear"    : "fear",
    "disgust" : "anger",
    "surprise": "surprise",
    "neutral" : "joy",
}


def analyse_frame(base64_image: str) -> dict:
    if not DEEPFACE_AVAILABLE:
        # Fallback — return a neutral result instead of error so app still works
        return {
            "emotion"   : "joy",
            "confidence": 0.5,
            "raw"       : {},
            "note"      : "DeepFace not installed — using fallback. Run: pip install deepface opencv-python"
        }

    try:
        import cv2
        img_data = base64_image.split(",")[-1]
        img_bytes = base64.b64decode(img_data)
        np_arr   = np.frombuffer(img_bytes, np.uint8)
        img      = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            return {"emotion": "joy", "confidence": 0.5, "raw": {}}

        result = DeepFace.analyze(
            img, actions=["emotion"],
            enforce_detection=False,
            silent=True
        )
        face   = result[0] if isinstance(result, list) else result
        raw_em = face["dominant_emotion"]
        scores = face["emotion"]

        mapped     = DEEPFACE_TO_APP.get(raw_em, "joy")
        confidence = round(scores.get(raw_em, 0) / 100, 4)

        return {
            "emotion"   : mapped,
            "confidence": confidence,
            "raw"       : {DEEPFACE_TO_APP.get(k, k): round(v / 100, 4) for k, v in scores.items()},
        }
    except Exception as e:
        return {"emotion": "joy", "confidence": 0.5, "raw": {}, "error": str(e)}
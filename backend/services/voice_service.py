"""
Voice tone service — analyses a base64 audio clip for emotional tone.
Install: pip install librosa soundfile
"""
import base64
import tempfile
import os
import numpy as np

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

LIBROSA_AVAILABLE = False
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    pass


def _extract_features(audio_path: str) -> np.ndarray:
    y, sr = librosa.load(audio_path, sr=22050, mono=True, duration=10)
    mfcc   = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    mel    = librosa.feature.melspectrogram(y=y, sr=sr)
    zcr    = librosa.feature.zero_crossing_rate(y)
    rms    = librosa.feature.rms(y=y)
    return np.hstack([
        np.mean(mfcc, axis=1), np.std(mfcc, axis=1),
        np.mean(chroma, axis=1),
        np.mean(mel, axis=1)[:20],
        np.mean(zcr), np.mean(rms),
    ]).reshape(1, -1)


def analyse_audio(base64_audio: str) -> dict:
    if not LIBROSA_AVAILABLE:
        return {
            "emotion"   : "joy",
            "confidence": 0.5,
            "note"      : "librosa not installed — using fallback. Run: pip install librosa soundfile"
        }

    try:
        audio_bytes = base64.b64decode(base64_audio.split(",")[-1])
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        features = _extract_features(tmp_path)
        os.unlink(tmp_path)

        energy = float(features[0, -1])
        zcr    = float(features[0, -2])

        if energy > 0.05 and zcr > 0.1:
            emotion, confidence = "anger",   0.65
        elif energy > 0.03:
            emotion, confidence = "joy",     0.60
        elif zcr < 0.05:
            emotion, confidence = "sadness", 0.60
        else:
            emotion, confidence = "fear",    0.55

        return {"emotion": emotion, "confidence": confidence}
    except Exception as e:
        return {"emotion": "joy", "confidence": 0.5, "error": str(e)}
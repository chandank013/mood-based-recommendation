"""
Passive service — collects passive signals (time of day, weather,
heart rate from wearable) and blends them into a soft mood hint
without requiring explicit user input.
"""
from datetime import datetime
from services.weather_service import get_weather, weather_to_mood_hint

# ── Emotion weights for blending signals ─────────────────────────────────────
EMOTION_SCORES = {
    "sadness" : 0,
    "fear"    : 1,
    "anger"   : 2,
    "surprise": 3,
    "love"    : 4,
    "joy"     : 5,
}
SCORE_TO_EMOTION = {v: k for k, v in EMOTION_SCORES.items()}


def get_time_signal() -> dict:
    """
    Derive a soft mood hint from the current time of day.
    Morning → joy, Afternoon → joy, Evening → love, Night → sadness
    """
    hour = datetime.now().hour

    if 5 <= hour < 9:
        return {"time_of_day": "morning",   "hint": "joy",     "energy": "medium"}
    if 9 <= hour < 12:
        return {"time_of_day": "morning",   "hint": "joy",     "energy": "high"}
    if 12 <= hour < 17:
        return {"time_of_day": "afternoon", "hint": "joy",     "energy": "high"}
    if 17 <= hour < 20:
        return {"time_of_day": "evening",   "hint": "love",    "energy": "medium"}
    if 20 <= hour < 23:
        return {"time_of_day": "evening",   "hint": "sadness", "energy": "low"}
    return     {"time_of_day": "night",     "hint": "sadness", "energy": "low"}


def get_heart_rate_signal(bpm: int) -> dict:
    """
    Map heart rate (BPM) from a wearable to an emotion hint.
    Resting: <60, Normal: 60-100, Elevated: 100-140, High: >140
    """
    if bpm < 60:
        return {"bpm": bpm, "hint": "sadness", "state": "resting/low"}
    if bpm < 80:
        return {"bpm": bpm, "hint": "love",    "state": "calm"}
    if bpm < 100:
        return {"bpm": bpm, "hint": "joy",     "state": "normal"}
    if bpm < 130:
        return {"bpm": bpm, "hint": "surprise","state": "elevated"}
    return     {"bpm": bpm, "hint": "anger",   "state": "high/stressed"}


def blend_signals(
    city: str = "Chennai",
    bpm: int = None,
    weights: dict = None,
) -> dict:
    """
    Blend all available passive signals into a single mood hint.

    Parameters:
        city    : city name for weather lookup
        bpm     : heart rate from wearable (optional)
        weights : custom signal weights e.g. {"time": 0.3, "weather": 0.4, "heart_rate": 0.3}

    Returns:
        {
          "blended_emotion" : str,
          "signals"         : { time, weather, heart_rate },
          "energy_level"    : str,
        }
    """
    if weights is None:
        weights = {
            "time"      : 0.4,
            "weather"   : 0.4,
            "heart_rate": 0.2,
        }

    signals     = {}
    score_sum   = 0.0
    weight_used = 0.0

    # ── Time signal ───────────────────────────────────────────────────────────
    time_sig = get_time_signal()
    signals["time"] = time_sig
    score_sum   += EMOTION_SCORES.get(time_sig["hint"], 3) * weights["time"]
    weight_used += weights["time"]

    # ── Weather signal ────────────────────────────────────────────────────────
    weather = get_weather(city)
    if weather:
        w_emotion = weather_to_mood_hint(weather.get("condition", "Clear"))
        signals["weather"] = {**weather, "hint": w_emotion}
        score_sum   += EMOTION_SCORES.get(w_emotion, 3) * weights["weather"]
        weight_used += weights["weather"]

    # ── Heart rate signal (optional) ──────────────────────────────────────────
    if bpm is not None:
        hr_sig = get_heart_rate_signal(bpm)
        signals["heart_rate"] = hr_sig
        score_sum   += EMOTION_SCORES.get(hr_sig["hint"], 3) * weights["heart_rate"]
        weight_used += weights["heart_rate"]

    # ── Blend ─────────────────────────────────────────────────────────────────
    if weight_used == 0:
        blended_score = 3
    else:
        blended_score = round(score_sum / weight_used)

    # Clamp to valid range
    blended_score   = max(0, min(5, blended_score))
    blended_emotion = SCORE_TO_EMOTION.get(blended_score, "joy")
    energy_level    = time_sig.get("energy", "medium")

    return {
        "blended_emotion": blended_emotion,
        "energy_level"   : energy_level,
        "signals"        : signals,
    }
"""
Mood routes — all mood detection endpoints.
Now attaches user_id from JWT to every mood log for journey tracking.
"""
import uuid
from flask import Blueprint, request, jsonify
from db.connection import execute_write
from services.model_service   import predict_mood
from services.groq_service    import classify_mood_groq
from services.facial_service  import analyse_frame
from services.voice_service   import analyse_audio
from services.weather_service import get_weather, weather_to_mood_hint
from utils.mood_mapper        import time_of_day
from routes.auth              import optional_auth

mood_bp = Blueprint("mood", __name__, url_prefix="/api/mood")

# ──────────────────────────────────────────────────────────────────────────────
# Emoji mapping
# ──────────────────────────────────────────────────────────────────────────────
EMOJI_MAP = {
    "😀":"joy","😊":"joy","🥰":"love","😍":"love",
    "😢":"sadness","😭":"sadness","😠":"anger","😡":"anger",
    "😨":"fear","😱":"fear","😲":"surprise","🤩":"surprise",
    "😔":"sadness","😤":"anger","🥺":"sadness","😌":"joy",
}


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
def _log_mood(session_id, user_id, raw_input, input_type, emotion,
              confidence=None, intensity=5, mode="amplify",
              context_time=None, context_who=None,
              weather=None, location=None) -> int:
    return execute_write(
        """INSERT INTO mood_logs
           (session_id, user_id, raw_input, input_type, emotion, confidence,
            intensity, context_time, context_who, mode, weather, location)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (session_id, user_id, raw_input, input_type, emotion, confidence,
         intensity, context_time, context_who, mode, weather, location),
    )


def _get_user_id() -> int | None:
    user = getattr(request, "user", None)
    return user["user_id"] if user else None


# ──────────────────────────────────────────────────────────────────────────────
# TEXT
# ──────────────────────────────────────────────────────────────────────────────
@mood_bp.route("/text", methods=["POST"])
@optional_auth
def detect_from_text():
    data        = request.get_json(force=True)
    text        = data.get("text", "").strip()
    session_id  = data.get("session_id") or str(uuid.uuid4())
    mode        = data.get("mode", "amplify")
    intensity   = int(data.get("intensity", 5))
    context_who = data.get("context_who")
    user_id     = _get_user_id()

    if not text:
        return jsonify({"error": "text field is required"}), 400

    result = predict_mood(text)

    # 🔥 fallback to LLM if low confidence
    if result["confidence"] is None or result["confidence"] < 0.55:
        groq_result = classify_mood_groq(text)
        if groq_result.get("emotion"):
            result["emotion"]     = groq_result["emotion"]
            result["groq_reason"] = groq_result.get("reason")

    context_time = time_of_day()

    mood_log_id = _log_mood(
        session_id, user_id, text, "text",
        result["emotion"], result["confidence"],
        intensity, mode, context_time, context_who,
    )

    return jsonify({
        "session_id"  : session_id,
        "mood_log_id" : mood_log_id,
        "emotion"     : result["emotion"],
        "confidence"  : result["confidence"],
        "all_scores"  : result.get("all_scores", {}),
        "groq_reason" : result.get("groq_reason"),
        "context_time": context_time,
        "mode"        : mode,
        "user_id"     : user_id,
    })


# ──────────────────────────────────────────────────────────────────────────────
# EMOJI
# ──────────────────────────────────────────────────────────────────────────────
@mood_bp.route("/emoji", methods=["POST"])
@optional_auth
def detect_from_emoji():
    data        = request.get_json(force=True)
    emoji       = data.get("emoji", "")
    slider_val  = int(data.get("slider", 5))
    session_id  = data.get("session_id") or str(uuid.uuid4())
    mode        = data.get("mode", "amplify")
    user_id     = _get_user_id()

    emotion = EMOJI_MAP.get(emoji)
    if not emotion:
        if slider_val >= 8:   emotion = "joy"
        elif slider_val >= 6: emotion = "love"
        elif slider_val >= 4: emotion = "surprise"
        elif slider_val >= 2: emotion = "sadness"
        else:                 emotion = "anger"

    mood_log_id = _log_mood(
        session_id, user_id, emoji or str(slider_val), "emoji",
        emotion, 1.0, slider_val, mode, time_of_day(),
    )

    return jsonify({
        "session_id" : session_id,
        "mood_log_id": mood_log_id,
        "emotion"    : emotion,
        "confidence" : 1.0,
        "mode"       : mode,
        "user_id"    : user_id,
    })


# ──────────────────────────────────────────────────────────────────────────────
# FACE  (🔥 FIXED — NO MORE 422)
# ──────────────────────────────────────────────────────────────────────────────
@mood_bp.route("/face", methods=["POST"])
@optional_auth
def detect_from_face():
    try:
        data = request.get_json()
        print("[FACE INPUT]:", data)

        if not data:
            return jsonify({"error": "No JSON body received"}), 422

        # ✅ accept both keys
        image_b64 = data.get("image") or data.get("base64_image")

        if not image_b64:
            return jsonify({"error": "image field is required"}), 422

        session_id = data.get("session_id") or str(uuid.uuid4())
        mode       = data.get("mode", "amplify")
        user_id    = _get_user_id()

        result = analyse_frame(image_b64)
        print("[FACE RESULT]:", result)

        # ❌ only fail for real errors
        if result.get("error"):
            return jsonify(result), 422

        # ✅ fallback
        emotion    = result.get("emotion") or "neutral"
        confidence = result.get("confidence") or 0.5

        mood_log_id = _log_mood(
            session_id, user_id, "webcam_frame", "face",
            emotion, confidence,
            mode=mode, context_time=time_of_day()
        )

        return jsonify({
            "session_id": session_id,
            "mood_log_id": mood_log_id,
            "emotion": emotion,
            "confidence": confidence,
            "raw": result.get("raw", {}),
            "warning": result.get("warning"),
            "mode": mode,
            "user_id": user_id,
        }), 200

    except Exception as e:
        print("[FACE ERROR]", str(e))
        return jsonify({"error": str(e)}), 500


# ──────────────────────────────────────────────────────────────────────────────
# VOICE  (🔥 FIXED — NO MORE 422)
# ──────────────────────────────────────────────────────────────────────────────
@mood_bp.route("/voice", methods=["POST"])
@optional_auth
def detect_from_voice():
    try:
        data = request.get_json()
        print("[VOICE INPUT]:", data)

        if not data:
            return jsonify({"error": "No JSON body received"}), 422

        audio_b64 = data.get("audio")

        if not audio_b64:
            return jsonify({"error": "audio field is required"}), 422

        session_id = data.get("session_id") or str(uuid.uuid4())
        mode       = data.get("mode", "amplify")
        user_id    = _get_user_id()

        result = analyse_audio(audio_b64)
        print("[VOICE RESULT]:", result)

        # ❌ only fail for real errors
        if result.get("error"):
            return jsonify(result), 422

        # ✅ fallback
        emotion    = result.get("emotion") or "neutral"
        confidence = result.get("confidence") or 0.5

        mood_log_id = _log_mood(
            session_id, user_id, "audio_clip", "voice",
            emotion, confidence,
            mode=mode, context_time=time_of_day()
        )

        return jsonify({
            "session_id": session_id,
            "mood_log_id": mood_log_id,
            "emotion": emotion,
            "confidence": confidence,
            "mode": mode,
            "user_id": user_id,
        }), 200

    except Exception as e:
        print("[VOICE ERROR]", str(e))
        return jsonify({"error": str(e)}), 500


# ──────────────────────────────────────────────────────────────────────────────
# PASSIVE
# ──────────────────────────────────────────────────────────────────────────────
@mood_bp.route("/passive", methods=["GET"])
def passive_signals():
    city    = request.args.get("city", "Chennai")
    weather = get_weather(city)
    tod     = time_of_day()

    return jsonify({
        "time_of_day": tod,
        "weather"    : weather,
        "mood_hint"  : weather_to_mood_hint(weather.get("condition", "Clear")),
    })
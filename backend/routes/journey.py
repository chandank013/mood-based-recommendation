"""
Journey routes — mood history, filtered by user_id when authenticated.
Falls back to session_id for unauthenticated users.
"""
from flask import Blueprint, request, jsonify
from db.connection import execute
from routes.auth   import optional_auth

journey_bp = Blueprint("journey", __name__, url_prefix="/api/journey")


@journey_bp.route("/history", methods=["GET"])
@optional_auth
def mood_history():
    days       = int(request.args.get("days", 7))
    user       = getattr(request, "user", None)
    session_id = request.args.get("session_id", "")

    # Prefer user_id over session_id for journey tracking
    if user:
        rows = execute(
            """SELECT id, emotion, confidence, intensity, input_type,
                      mode, context_time, context_who, weather, raw_input, created_at
               FROM mood_logs
               WHERE user_id = %s
                 AND created_at >= NOW() - INTERVAL %s DAY
               ORDER BY created_at DESC
               LIMIT 200""",
            (user["user_id"], days),
        )
    elif session_id:
        rows = execute(
            """SELECT id, emotion, confidence, intensity, input_type,
                      mode, context_time, context_who, weather, raw_input, created_at
               FROM mood_logs
               WHERE session_id = %s
                 AND created_at >= NOW() - INTERVAL %s DAY
               ORDER BY created_at DESC
               LIMIT 100""",
            (session_id, days),
        )
    else:
        return jsonify({"error": "session_id or auth token required"}), 400

    history = []
    for row in rows:
        recs = execute(
            "SELECT category, title, thumbnail, source, external_id as url FROM recommendations WHERE mood_log_id=%s LIMIT 8",
            (row["id"],),
        )
        history.append({**row, "recommendations": recs, "created_at": str(row["created_at"])})

    return jsonify({
        "history"    : history,
        "days"       : days,
        "tracked_by" : "user" if user else "session",
    })


@journey_bp.route("/summary", methods=["GET"])
@optional_auth
def mood_summary():
    user       = getattr(request, "user", None)
    session_id = request.args.get("session_id", "")

    if user:
        rows = execute(
            """SELECT emotion,
                      COUNT(*)        as count,
                      AVG(confidence) as avg_confidence,
                      AVG(intensity)  as avg_intensity
               FROM mood_logs WHERE user_id=%s
               GROUP BY emotion ORDER BY count DESC""",
            (user["user_id"],),
        )
    elif session_id:
        rows = execute(
            """SELECT emotion,
                      COUNT(*)        as count,
                      AVG(confidence) as avg_confidence,
                      AVG(intensity)  as avg_intensity
               FROM mood_logs WHERE session_id=%s
               GROUP BY emotion ORDER BY count DESC""",
            (session_id,),
        )
    else:
        return jsonify({"error": "session_id or auth token required"}), 400

    total   = sum(r["count"] for r in rows)
    summary = [
        {
            **r,
            "percentage"     : round(r["count"] / total * 100, 1) if total else 0,
            "avg_confidence" : round(float(r["avg_confidence"] or 0), 3),
            "avg_intensity"  : round(float(r["avg_intensity"]  or 0), 1),
        }
        for r in rows
    ]

    return jsonify({
        "total_entries": total,
        "summary"      : summary,
        "dominant_mood": summary[0]["emotion"] if summary else None,
        "tracked_by"   : "user" if user else "session",
    })
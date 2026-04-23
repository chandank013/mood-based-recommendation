"""
Social mood routes — anonymised community mood aggregation.

GET  /api/social/trending          — top emotions in the last hour
POST /api/social/contribute        — add current mood to community pool
GET  /api/social/pulse             — emotion counts over last 24 hours
"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from db.connection import execute, execute_write

social_bp = Blueprint("social", __name__, url_prefix="/api/social")


def _current_hour_slot() -> str:
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:00:00")


@social_bp.route("/trending", methods=["GET"])
def trending():
    rows = execute(
        """SELECT emotion, SUM(count) as total
           FROM social_moods
           WHERE hour_slot >= NOW() - INTERVAL 1 HOUR
           GROUP BY emotion
           ORDER BY total DESC
           LIMIT 6""",
    )
    grand_total = sum(r["total"] for r in rows) or 1
    return jsonify({
        "trending": [
            {
                "emotion"   : r["emotion"],
                "count"     : r["total"],
                "percentage": round(r["total"] / grand_total * 100, 1),
            }
            for r in rows
        ],
        "period": "last_hour",
    })


@social_bp.route("/contribute", methods=["POST"])
def contribute():
    data    = request.get_json(force=True)
    emotion = data.get("emotion", "").strip().lower()
    valid   = {"sadness", "joy", "anger", "fear", "love", "surprise"}
    if emotion not in valid:
        return jsonify({"error": f"emotion must be one of {sorted(valid)}"}), 400

    slot = _current_hour_slot()
    execute_write(
        """INSERT INTO social_moods (emotion, count, hour_slot)
           VALUES (%s, 1, %s)
           ON DUPLICATE KEY UPDATE count = count + 1""",
        (emotion, slot),
    )
    return jsonify({"status": "ok", "emotion": emotion})


@social_bp.route("/pulse", methods=["GET"])
def pulse():
    rows = execute(
        """SELECT emotion, hour_slot, SUM(count) as total
           FROM social_moods
           WHERE hour_slot >= NOW() - INTERVAL 24 HOUR
           GROUP BY emotion, hour_slot
           ORDER BY hour_slot ASC""",
    )
    pulse_data = {}
    for r in rows:
        slot = str(r["hour_slot"])
        if slot not in pulse_data:
            pulse_data[slot] = {}
        pulse_data[slot][r["emotion"]] = r["total"]

    return jsonify({"pulse": pulse_data, "period": "last_24_hours"})
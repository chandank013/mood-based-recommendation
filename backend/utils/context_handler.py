"""
context_handler.py — combines passive signals (time of day, weather,
companion context) into a context profile that adjusts recommendations.
"""
from datetime import datetime
from services.weather_service import get_weather, weather_to_mood_hint


# ── Time-of-day buckets ───────────────────────────────────────────────────────
def get_time_of_day() -> str:
    hour = datetime.now().hour
    if 5  <= hour < 12: return "morning"
    if 12 <= hour < 17: return "afternoon"
    if 17 <= hour < 21: return "evening"
    return "night"


# ── Time → content tone hints ─────────────────────────────────────────────────
TIME_HINTS = {
    "morning"  : {"energy": "medium", "note": "Start the day right"},
    "afternoon": {"energy": "high",   "note": "Keep the momentum going"},
    "evening"  : {"energy": "low",    "note": "Wind down and relax"},
    "night"    : {"energy": "low",    "note": "Rest and recover"},
}

# ── Companion context adjustments ─────────────────────────────────────────────
COMPANION_HINTS = {
    "alone"  : {"tone": "personal",   "note": "Just for you"},
    "family" : {"tone": "wholesome",  "note": "Great for the whole family"},
    "friends": {"tone": "social",     "note": "Perfect to enjoy together"},
    "partner": {"tone": "romantic",   "note": "A moment for two"},
}

# ── Weather → energy modifier ─────────────────────────────────────────────────
WEATHER_ENERGY = {
    "Clear"       : "high",
    "Clouds"      : "medium",
    "Rain"        : "low",
    "Drizzle"     : "low",
    "Thunderstorm": "low",
    "Snow"        : "medium",
    "Mist"        : "low",
    "Fog"         : "low",
}


def build_context(
    city: str = "Chennai",
    context_who: str = None,
) -> dict:
    """
    Build a full context profile by combining:
      - time of day
      - live weather
      - companion context (alone / family / friends / partner)

    Returns a context dict that routes can attach to mood logs
    and pass to recommendation logic.
    """
    # ── Time ──────────────────────────────────────────────────────────────────
    tod       = get_time_of_day()
    time_hint = TIME_HINTS.get(tod, TIME_HINTS["afternoon"])

    # ── Weather ───────────────────────────────────────────────────────────────
    weather      = get_weather(city)
    condition    = weather.get("condition", "Clear")
    mood_hint    = weather_to_mood_hint(condition)
    energy_level = WEATHER_ENERGY.get(condition, "medium")

    # Override energy with time-of-day if it is stricter
    if time_hint["energy"] == "low":
        energy_level = "low"

    # ── Companion ─────────────────────────────────────────────────────────────
    companion = COMPANION_HINTS.get(context_who, None)

    # ── Activity filter based on energy ───────────────────────────────────────
    activity_filter = {
        "high"  : ["hiit", "boxing", "running", "dancing", "group sport"],
        "medium": ["yoga", "walk", "stretching", "cycling"],
        "low"   : ["meditation", "breathing", "light stretching", "journaling"],
    }.get(energy_level, [])

    return {
        "time_of_day"    : tod,
        "time_note"      : time_hint["note"],
        "weather"        : weather,
        "weather_hint"   : mood_hint,
        "energy_level"   : energy_level,
        "companion"      : context_who,
        "companion_tone" : companion["tone"] if companion else "personal",
        "companion_note" : companion["note"] if companion else "",
        "activity_filter": activity_filter,
    }


def adjust_recommendations(recs: dict, context: dict) -> dict:
    """
    Filter and annotate recommendations based on context.
    - Filters activities by energy level
    - Adds a context note to the response
    """
    allowed_activities = context.get("activity_filter", [])

    if allowed_activities and recs.get("activities"):
        filtered = [
            a for a in recs["activities"]
            if any(kw in a.lower() for kw in allowed_activities)
        ]
        # Fallback: keep original list if nothing matched
        recs["activities"] = filtered if filtered else recs["activities"]

    recs["context"] = {
        "time_of_day"    : context["time_of_day"],
        "time_note"      : context["time_note"],
        "energy_level"   : context["energy_level"],
        "weather"        : context.get("weather", {}),
        "companion_note" : context["companion_note"],
        "companion_tone" : context["companion_tone"],
    }

    return recs
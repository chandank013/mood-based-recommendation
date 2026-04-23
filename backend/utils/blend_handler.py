"""
Blend handler — supports mixed emotions like 'happy but nostalgic'.
Merges strategies from two emotions weighted by intensity.
"""

BLEND_KEYWORDS = {
    "nostalgic" : "sadness",
    "melancholy": "sadness",
    "excited"   : "joy",
    "grateful"  : "love",
    "anxious"   : "fear",
    "frustrated": "anger",
    "tender"    : "love",
    "energetic" : "joy",
    "peaceful"  : "fear",
    "passionate": "love",
}

VALID_EMOTIONS = {"sadness", "joy", "anger", "fear", "love", "surprise"}


def parse_blend(emotion_input: str) -> list[dict]:
    """
    Parse a comma or 'and' separated emotion string.
    Returns a list of {emotion, weight} dicts.

    Examples:
      "happy"                  → [{"emotion": "joy", "weight": 1.0}]
      "joy, nostalgic"         → [{"emotion": "joy", "weight": 0.6},
                                   {"emotion": "sadness", "weight": 0.4}]
    """
    parts = [p.strip().lower() for p in emotion_input.replace(" and ", ",").split(",")]
    resolved = []
    for part in parts:
        emotion = BLEND_KEYWORDS.get(part, part)
        if emotion in VALID_EMOTIONS:
            resolved.append(emotion)

    if not resolved:
        return [{"emotion": "joy", "weight": 1.0}]

    weight = round(1.0 / len(resolved), 2)
    return [{"emotion": e, "weight": weight} for e in resolved]


def dominant_emotion(blend: list[dict]) -> str:
    """Return the highest-weight emotion from a blend list."""
    return max(blend, key=lambda x: x["weight"])["emotion"]
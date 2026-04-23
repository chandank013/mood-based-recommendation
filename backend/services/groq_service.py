"""
Groq service — uses LLaMA 3 via Groq API for:
  1. Classifying mood from free text (fallback / second opinion)
  2. Generating a personalised recommendation explanation
"""
import json
from groq import Groq
from config import Config

_client = Groq(api_key=Config.GROQ_API_KEY) if Config.GROQ_API_KEY else None

VALID_EMOTIONS = ["sadness", "joy", "anger", "fear", "love", "surprise"]


def classify_mood_groq(text: str) -> dict:
    """
    Ask Groq LLaMA 3 to classify the emotion in the text.
    Returns {"emotion": str, "reason": str}
    """
    if not _client:
        return {"emotion": None, "reason": "Groq API key not configured"}

    prompt = f"""You are a mood classification assistant.
Classify the emotion expressed in the following text into exactly ONE of these labels:
sadness, joy, anger, fear, love, surprise

Text: "{text}"

Respond ONLY with valid JSON in this exact format:
{{"emotion": "<label>", "reason": "<one sentence explanation>"}}"""

    try:
        response = _client.chat.completions.create(
            model=Config.GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=120,
        )
        raw  = response.choices[0].message.content.strip()
        data = json.loads(raw)
        if data.get("emotion") not in VALID_EMOTIONS:
            data["emotion"] = "joy"
        return data
    except Exception as e:
        return {"emotion": None, "reason": str(e)}


def generate_recommendation_note(emotion: str, mode: str, items: dict) -> str:
    """
    Generate a short personalised note explaining why these recommendations
    suit the user's current mood.
    Returns a plain string.
    """
    if not _client:
        return f"Here are some recommendations tailored to your {emotion} mood."

    item_summary = ", ".join([
        f"{cat}: {info.get('title', '') if isinstance(info, dict) else info}"
        for cat, info in items.items() if info
    ])

    prompt = f"""You are a warm, empathetic mood-based recommendation assistant.
The user is feeling {emotion}. Mode is '{mode}' (amplify = match the mood, contrast = shift the mood).
Recommended items: {item_summary}

Write a single friendly paragraph (2-3 sentences) explaining why these picks
suit their current mood. Be warm, concise, and avoid generic phrases."""

    try:
        response = _client.chat.completions.create(
            model=Config.GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Here are some {emotion}-matched recommendations for you."
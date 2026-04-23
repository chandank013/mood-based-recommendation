"""
Weather service — fetches current weather for passive mood signal.
"""
import requests
from config import Config

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather(city: str = "Chennai") -> dict:
    """Return current weather summary for a city."""
    if not Config.OPENWEATHER_API_KEY:
        return {}
    try:
        r = requests.get(
            BASE_URL,
            params={
                "q"     : city,
                "appid" : Config.OPENWEATHER_API_KEY,
                "units" : "metric",
            },
            timeout=8,
        )
        if r.status_code != 200:
            return {}

        data = r.json()
        return {
            "city"       : data.get("name"),
            "condition"  : data["weather"][0]["main"],
            "description": data["weather"][0]["description"],
            "temp_c"     : data["main"]["temp"],
            "humidity"   : data["main"]["humidity"],
        }
    except Exception:
        return {}


def weather_to_mood_hint(condition: str) -> str:
    """Map weather condition to a soft mood hint."""
    mapping = {
        "Clear"        : "joy",
        "Clouds"       : "sadness",
        "Rain"         : "sadness",
        "Drizzle"      : "sadness",
        "Thunderstorm" : "fear",
        "Snow"         : "surprise",
        "Mist"         : "fear",
        "Fog"          : "fear",
    }
    return mapping.get(condition, "joy")
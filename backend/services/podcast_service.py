"""
Podcast service — fetches podcasts from Listen Notes API matching the mood.
Sign up for a free API key at: https://www.listennotes.com/api/
"""
import requests
from config import Config

BASE_URL = "https://listen-api.listennotes.com/api/v2"

# Mood → podcast search terms
MOOD_PODCAST_MAP = {
    "sadness" : "healing emotional wellness mindfulness",
    "joy"     : "happiness motivation positivity fun",
    "anger"   : "stress relief calm anger management",
    "fear"    : "anxiety relief courage confidence",
    "love"    : "relationships love self care romance",
    "surprise": "adventure discovery curiosity new things",
}


def get_podcasts(emotion: str, limit: int = 4) -> list[dict]:
    """
    Search Listen Notes for podcasts matching the mood emotion.
    Returns a list of podcast episode dicts.
    """
    api_key = getattr(Config, "LISTEN_NOTES_API_KEY", "")
    if not api_key:
        return _fallback_podcasts(emotion, limit)

    query = MOOD_PODCAST_MAP.get(emotion, "wellbeing")

    try:
        r = requests.get(
            f"{BASE_URL}/search",
            headers={"X-ListenAPI-Key": api_key},
            params={
                "q"           : query,
                "type"        : "episode",
                "len_min"     : 5,
                "len_max"     : 60,
                "language"    : "English",
                "safe_mode"   : 1,
                "page_size"   : limit,
            },
            timeout=10,
        )
        if r.status_code != 200:
            return _fallback_podcasts(emotion, limit)

        results = r.json().get("results", [])
        return [
            {
                "title"      : ep.get("title_original"),
                "podcast"    : ep.get("podcast", {}).get("title_original"),
                "description": (ep.get("description_original") or "")[:200],
                "duration"   : ep.get("audio_length_sec"),
                "thumbnail"  : ep.get("image"),
                "url"        : ep.get("listennotes_url"),
                "source"     : "listennotes",
            }
            for ep in results
        ]
    except Exception:
        return _fallback_podcasts(emotion, limit)


def _fallback_podcasts(emotion: str, limit: int) -> list[dict]:
    """
    Static fallback podcasts when Listen Notes API key is not configured.
    These are real, well-known podcasts mapped to each emotion.
    """
    FALLBACKS = {
        "sadness": [
            {"title": "Grief Out Loud",          "podcast": "The Dougy Center",        "url": "https://www.dougy.org/grief-resources/podcast", "duration": 1800},
            {"title": "Terrible, Thanks for Asking","podcast": "Nora McInerny",         "url": "https://www.ttfa.org",                          "duration": 2400},
            {"title": "The Healing Place Podcast","podcast": "Teri Patterson",          "url": "https://podcasts.apple.com/us/podcast/the-healing-place-podcast", "duration": 2700},
            {"title": "Unlocking Us",             "podcast": "Brené Brown",            "url": "https://brenebrown.com/podcast/",               "duration": 3000},
        ],
        "joy": [
            {"title": "The Happiness Lab",        "podcast": "Dr. Laurie Santos",      "url": "https://www.happinesslab.fm",                   "duration": 2400},
            {"title": "Good Life Project",        "podcast": "Jonathan Fields",        "url": "https://www.goodlifeproject.com/podcast/",      "duration": 3600},
            {"title": "Conan O'Brien Needs A Friend","podcast": "Conan O'Brien",       "url": "https://www.earwolf.com/show/conan-obrien-needs-a-friend/", "duration": 3600},
            {"title": "SmartLess",                "podcast": "Jason Bateman",          "url": "https://www.smartless.com",                     "duration": 3600},
        ],
        "anger": [
            {"title": "Ten Percent Happier",      "podcast": "Dan Harris",             "url": "https://www.tenpercent.com/podcast",            "duration": 3000},
            {"title": "The Mindful Minute",       "podcast": "Meryl Arnett",           "url": "https://podcasts.apple.com/us/podcast/the-mindful-minute", "duration": 600},
            {"title": "Calm it Down",             "podcast": "Calm it Down",           "url": "https://podcasts.apple.com/us/podcast/calm-it-down", "duration": 1800},
            {"title": "Dare to Lead",             "podcast": "Brené Brown",            "url": "https://brenebrown.com/podcast/",               "duration": 2700},
        ],
        "fear": [
            {"title": "The Anxiety Coaches Podcast","podcast": "Gina Ryan",            "url": "https://theanxietycoachespodcast.com",          "duration": 1800},
            {"title": "Overcome Anxiety",         "podcast": "Overcome Anxiety",       "url": "https://podcasts.apple.com/us/podcast/overcome-anxiety", "duration": 1500},
            {"title": "Feel Better Live More",    "podcast": "Dr. Rangan Chatterjee",  "url": "https://drchatterjee.com/podcast/",             "duration": 3600},
            {"title": "The Calm Collective",      "podcast": "Cassandra Eldridge",     "url": "https://podcasts.apple.com/us/podcast/the-calm-collective", "duration": 2400},
        ],
        "love": [
            {"title": "Where Should We Begin?",   "podcast": "Esther Perel",           "url": "https://www.estherperel.com/podcast",           "duration": 3000},
            {"title": "Love Life with Matthew Hussey","podcast": "Matthew Hussey",     "url": "https://matthewhussey.com/podcast",             "duration": 2400},
            {"title": "DTR: Define the Relationship","podcast": "Bumble",              "url": "https://podcasts.apple.com/us/podcast/dtr",     "duration": 1800},
            {"title": "The School of Greatness",  "podcast": "Lewis Howes",            "url": "https://lewishowes.com/podcast/",               "duration": 3600},
        ],
        "surprise": [
            {"title": "Stuff You Should Know",    "podcast": "iHeartRadio",            "url": "https://www.iheart.com/podcast/105-stuff-you-should-know", "duration": 3600},
            {"title": "Radiolab",                 "podcast": "WNYC Studios",           "url": "https://radiolab.org",                          "duration": 3600},
            {"title": "Hidden Brain",             "podcast": "NPR",                    "url": "https://hiddenbrain.org",                       "duration": 2700},
            {"title": "No Such Thing as a Fish",  "podcast": "QI Elves",               "url": "https://www.nosuchthingasafish.com",            "duration": 2400},
        ],
    }

    items = FALLBACKS.get(emotion, FALLBACKS["joy"])[:limit]
    return [{**item, "thumbnail": None, "source": "fallback"} for item in items]
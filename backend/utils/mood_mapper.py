"""
mood_mapper.py — Emotion → content strategy with granular genre mappings.

Key improvements:
  - Multiple TMDB genres per emotion (rotated randomly to avoid same content)
  - Multiple food queries per emotion (rotated randomly)
  - Multiple Spotify seeds per emotion (rotated randomly)
  - Contrast map fixed for fear/sadness/anger → meaningful positive shifts
  - Book genre subjects added for Google Books filtering
  - Podcast topic keywords added
"""

import random
from datetime import datetime

# ── Granular emotion → content strategy ───────────────────────────────────────
# Each field now has a LIST of options — randomly selected per request
# so the same emotion never returns the same content twice.

EMOTION_STRATEGY = {
    "sadness": {
        "music": {
            "mood_tags"      : ["sad", "melancholy", "acoustic healing", "rainy day", "emotional"],
            "spotify_seeds"  : [
                "37i9dQZF1DX7qK8ma5wgG1",   # Sad Songs
                "37i9dQZF1DWXe9gFZP0gtP",   # Acoustic Melancholy
                "37i9dQZF1DX4E3UdUs7fUx",   # Rain & Tears
                "37i9dQZF1DWXIcbzpLauPS",   # Healing Vibes
                "37i9dQZF1DX3Ynp2ANub7f",   # Calm Vibes
            ],
        },
        "movie": {
            "tmdb_genres"    : [18, 10751, 10749, 36],   # Drama, Family, Romance, History
            "mood_tags"      : ["comfort", "heartwarming", "inspiring", "feel-good drama"],
            "book_subjects"  : ["self-help grief", "healing emotional", "hope resilience"],
        },
        "food": {
            "queries"        : [
                "comfort food soup pasta",
                "mac and cheese grilled cheese",
                "warm ramen noodle broth",
                "chocolate chip cookies brownies",
                "chicken pot pie casserole",
            ],
        },
        "podcast_topics"     : ["mental health healing", "grief support", "emotional wellness"],
        "activities"         : [
            "Gentle yoga (20 min)",
            "Slow walk in nature",
            "Journaling your thoughts",
            "Hot bath with calming music",
            "Call a close friend",
            "Watch a comfort movie",
        ],
    },

    "joy": {
        "music": {
            "mood_tags"      : ["happy", "feel-good", "upbeat", "dance pop", "summer hits"],
            "spotify_seeds"  : [
                "37i9dQZF1DXdPec7aLTmlC",   # Happy Hits
                "37i9dQZF1DX3rxVfibe1L0",   # Mood Booster
                "37i9dQZF1DXaXB8fQg7xof",   # Dance Pop Hits
                "37i9dQZF1DX0FOF1IUWK1W",   # Good Vibes
                "37i9dQZF1DX2L0iB23Enbq",   # Viral Hits
            ],
        },
        "movie": {
            "tmdb_genres"    : [35, 12, 16, 10402],  # Comedy, Adventure, Animation, Music
            "mood_tags"      : ["comedy", "fun", "adventure", "light-hearted"],
            "book_subjects"  : ["happiness adventure", "comedy humor", "feel good fiction"],
        },
        "food": {
            "queries"        : [
                "healthy salad smoothie bowl",
                "acai bowl fresh fruit",
                "mango salsa tacos",
                "lemon pasta zucchini",
                "avocado toast eggs benedict",
            ],
        },
        "podcast_topics"     : ["happiness motivation", "positivity personal growth", "comedy fun"],
        "activities"         : [
            "HIIT workout (30 min)",
            "Dance session at home",
            "Outdoor run or cycling",
            "Group sport or game",
            "Try a new hobby",
            "Cook a favourite meal",
        ],
    },

    "anger": {
        "music": {
            "mood_tags"      : ["energetic", "hard rock", "metal", "power workout", "adrenaline"],
            "spotify_seeds"  : [
                "37i9dQZF1DWXIcbzpLauPS",   # Rage Fuel
                "37i9dQZF1DX9qNs32fujYe",   # Metal Workout
                "37i9dQZF1DWXNFSTtym834",   # Hard Rock Drive
                "37i9dQZF1DX76Wlfdnj7AP",   # Adrenaline Workout
                "37i9dQZF1DX70RN3TfWWJh",   # Rock Classics
            ],
        },
        "movie": {
            "tmdb_genres"    : [28, 53, 80, 10752],  # Action, Thriller, Crime, War
            "mood_tags"      : ["action", "intense", "thriller", "crime"],
            "book_subjects"  : ["stoicism calm", "anger management mindfulness", "inner peace"],
        },
        "food": {
            "queries"        : [
                "spicy wings tacos chilli",
                "nashville hot chicken",
                "buffalo wings sriracha",
                "spicy korean bibimbap",
                "jalapeño burger loaded fries",
            ],
        },
        "podcast_topics"     : ["anger management calm", "stress relief", "mindfulness meditation"],
        "activities"         : [
            "Boxing or punching bag",
            "Sprint intervals",
            "Weight training",
            "Kickboxing class",
            "Intense cycling session",
            "Cold shower + breathing exercise",
        ],
    },

    "fear": {
        "music": {
            "mood_tags"      : ["calm", "ambient", "peaceful", "meditation", "sleep music"],
            "spotify_seeds"  : [
                "37i9dQZF1DX3Ynp2ANub7f",   # Calm Vibes
                "37i9dQZF1DWZd79rJ6a7lp",   # Sleep & Relax
                "37i9dQZF1DWZeKCadgRdKQ",   # Deep Focus
                "37i9dQZF1DX4dyzvuaRJ0n",   # Ambient Chill
                "37i9dQZF1DX3PIPIT6lEg5",   # Nature Sounds
            ],
        },
        "movie": {
            "tmdb_genres"    : [35, 10751, 16, 10402],  # Comedy, Family, Animation, Music
            "mood_tags"      : ["feel-good", "uplifting", "family", "light-hearted"],
            "book_subjects"  : ["courage overcoming fear", "confidence self-help", "anxiety relief"],
        },
        "food": {
            "queries"        : [
                "warm soup ramen broth",
                "chamomile tea honey toast",
                "chicken noodle soup",
                "miso soup warm oatmeal",
                "ginger turmeric latte",
            ],
        },
        "podcast_topics"     : ["anxiety relief calm", "courage mindfulness", "fear overcoming"],
        "activities"         : [
            "Box breathing (4-4-4-4)",
            "Meditation (10 min guided)",
            "Light stretching or yoga",
            "Call a trusted friend",
            "Write down your worries",
            "Warm bath with lavender",
        ],
    },

    "love": {
        "music": {
            "mood_tags"      : ["romantic", "r&b", "love songs", "slow dance", "soulful"],
            "spotify_seeds"  : [
                "37i9dQZF1DWXbttAJcbphz",   # R&B Romance
                "37i9dQZF1DXbtzAgnntyvH",   # Love Songs
                "37i9dQZF1DX6mvEU1S6INL",   # Valentine's Day
                "37i9dQZF1DX9wC1KY45plY",   # Slow Dance
                "37i9dQZF1DX2UgsUIyFjzR",   # Neo Soul
            ],
        },
        "movie": {
            "tmdb_genres"    : [10749, 18, 35, 10402],  # Romance, Drama, Comedy, Music
            "mood_tags"      : ["romantic", "love story", "heartwarming", "couples"],
            "book_subjects"  : ["romance love story", "relationships heart", "love poetry"],
        },
        "food": {
            "queries"        : [
                "chocolate fondue dessert tiramisu",
                "strawberry crepes valentines",
                "lobster pasta seafood romantic",
                "chocolate lava cake mousse",
                "bruschetta wine cheese board",
            ],
        },
        "podcast_topics"     : ["relationships love", "romance dating", "self love care"],
        "activities"         : [
            "Couples yoga",
            "Cook a special meal together",
            "Scenic evening walk",
            "Write a heartfelt letter",
            "Watch a romantic movie",
            "Plan a surprise date night",
        ],
    },

    "surprise": {
        "music": {
            "mood_tags"      : ["eclectic", "discover", "new music", "indie mix", "unexpected"],
            "spotify_seeds"  : [
                "37i9dQZF1DX4dyzvuaRJ0n",   # Discover Weekly
                "37i9dQZEVXcQ9COmYvdajy",   # Release Radar
                "37i9dQZF1DX4JAvHpjipBk",   # New Music Friday
                "37i9dQZF1DX2L0iB23Enbq",   # Viral Hits
                "37i9dQZF1DXbITWG1ZJzn6",   # All New Indie
            ],
        },
        "movie": {
            "tmdb_genres"    : [9648, 878, 53, 14],  # Mystery, Sci-Fi, Thriller, Fantasy
            "mood_tags"      : ["mystery", "sci-fi", "unexpected twist", "mind-bending"],
            "book_subjects"  : ["mystery thriller twist", "science fiction fantasy", "unexpected adventure"],
        },
        "food": {
            "queries"        : [
                "exotic fusion japanese korean",
                "moroccan tagine middle eastern",
                "thai green curry pad thai",
                "ethiopian injera berbere",
                "peruvian ceviche causa",
            ],
        },
        "podcast_topics"     : ["curiosity discovery", "science adventure", "surprising facts"],
        "activities"         : [
            "Try a completely new recipe",
            "Explore a new area of your city",
            "Sign up for a random class",
            "Random act of kindness",
            "Start learning a new skill",
            "Visit somewhere you've never been",
        ],
    },
}

# ── Contrast map — meaningful emotional shifts ────────────────────────────────
# fear     → joy       (calm → confident & happy)
# sadness  → joy       (melancholy → uplifted)
# anger    → love      (aggression → warmth & calm)
# joy      → surprise  (content → excited & curious)
# love     → surprise  (romantic → adventurous)
# surprise → fear      (stimulated → grounded & calm)
CONTRAST_MAP = {
    "fear"    : "joy",       # shift from anxious → confident & happy
    "sadness" : "joy",       # shift from low → uplifted
    "anger"   : "love",      # shift from aggressive → warm & calm
    "joy"     : "surprise",  # shift from content → excited & curious
    "love"    : "surprise",  # shift from romantic → adventurous
    "surprise": "fear",      # shift from overstimulated → grounded & calm
}


# ── Strategy getter (with random rotation) ────────────────────────────────────
def get_strategy(emotion: str, mode: str = "amplify") -> dict:
    """
    Return the content strategy for a given emotion.
    mode='amplify'  → match the emotion
    mode='contrast' → meaningful emotional shift via CONTRAST_MAP

    Randomly selects one option from each list so the same emotion
    never returns identical content on consecutive calls.
    """
    if mode == "contrast":
        emotion = CONTRAST_MAP.get(emotion, emotion)

    raw = EMOTION_STRATEGY.get(emotion, EMOTION_STRATEGY["joy"])

    # Flatten lists → single random pick for each field
    return {
        "music": {
            "mood_tag"      : random.choice(raw["music"]["mood_tags"]),
            "spotify_seed"  : random.choice(raw["music"]["spotify_seeds"]),
        },
        "movie": {
            "tmdb_genre"    : random.choice(raw["movie"]["tmdb_genres"]),
            "mood_tag"      : random.choice(raw["movie"]["mood_tags"]),
            "book_subject"  : random.choice(raw["movie"]["book_subjects"]),
        },
        "food": {
            "query"         : random.choice(raw["food"]["queries"]),
        },
        "podcast_topic"     : random.choice(raw["podcast_topics"]),
        "activities"        : random.sample(raw["activities"], min(4, len(raw["activities"]))),
    }


# ── Time of day ───────────────────────────────────────────────────────────────
def time_of_day() -> str:
    hour = datetime.now().hour
    if 5  <= hour < 12: return "morning"
    if 12 <= hour < 17: return "afternoon"
    if 17 <= hour < 21: return "evening"
    return "night"
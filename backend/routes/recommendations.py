"""
Recommendations route — works fully without any external API keys.
"""
import json
from flask import Blueprint, request, jsonify
from db.connection    import execute, execute_write
from services.spotify_service import get_playlists
from services.tmdb_service    import get_movies, get_tv_shows
from services.food_service    import get_recipes
from services.groq_service    import generate_recommendation_note
from utils.mood_mapper        import get_strategy

# Service imports — book_service uses Google Books API (no key needed)
from services.book_service import get_books

try:
    from services.podcast_service import get_podcasts
except ImportError:
    def get_podcasts(emotion, limit=4): return []

rec_bp = Blueprint("recommendations", __name__, url_prefix="/api/recommendations")

ACTIVITIES = {
    "sadness" : ["Gentle yoga (20 min)", "Slow walk in nature", "Journaling your thoughts", "Hot bath with calming music"],
    "joy"     : ["HIIT workout", "Dance session", "Outdoor run", "Group sport or game"],
    "anger"   : ["Boxing / punching bag", "Sprint intervals", "Weight training", "Kickboxing class"],
    "fear"    : ["Box breathing (4-4-4-4)", "Meditation (10 min)", "Light stretching", "Call a trusted friend"],
    "love"    : ["Couples yoga", "Cook a meal together", "Scenic evening walk", "Creative art project"],
    "surprise": ["Try a new recipe", "Explore a new area", "Sign up for a class", "Random act of kindness"],
}

MUSIC_FALLBACK = {
    "sadness":  [
        {"title":"Sad Songs Playlist",   "url":"https://open.spotify.com/playlist/37i9dQZF1DX7qK8ma5wgG1", "thumbnail":None, "source":"fallback"},
        {"title":"Acoustic Melancholy",  "url":"https://open.spotify.com/playlist/37i9dQZF1DWXe9gFZP0gtP", "thumbnail":None, "source":"fallback"},
        {"title":"Rain & Melancholy",    "url":"https://open.spotify.com/playlist/37i9dQZF1DX4E3UdUs7fUx", "thumbnail":None, "source":"fallback"},
        {"title":"Healing Sounds",       "url":"https://open.spotify.com/playlist/37i9dQZF1DWXIcbzpLauPS", "thumbnail":None, "source":"fallback"},
    ],
    "joy":      [
        {"title":"Happy Hits",           "url":"https://open.spotify.com/playlist/37i9dQZF1DXdPec7aLTmlC", "thumbnail":None, "source":"fallback"},
        {"title":"Mood Booster",         "url":"https://open.spotify.com/playlist/37i9dQZF1DX3rxVfibe1L0", "thumbnail":None, "source":"fallback"},
        {"title":"Dance Pop Hits",       "url":"https://open.spotify.com/playlist/37i9dQZF1DXaXB8fQg7xof", "thumbnail":None, "source":"fallback"},
        {"title":"Good Vibes",           "url":"https://open.spotify.com/playlist/37i9dQZF1DX0FOF1IUWK1W", "thumbnail":None, "source":"fallback"},
    ],
    "anger":    [
        {"title":"Rage Fuel",            "url":"https://open.spotify.com/playlist/37i9dQZF1DWXIcbzpLauPS", "thumbnail":None, "source":"fallback"},
        {"title":"Metal Workout",        "url":"https://open.spotify.com/playlist/37i9dQZF1DX9qNs32fujYe", "thumbnail":None, "source":"fallback"},
        {"title":"Hard Rock Drive",      "url":"https://open.spotify.com/playlist/37i9dQZF1DWXNFSTtym834", "thumbnail":None, "source":"fallback"},
        {"title":"Adrenaline Workout",   "url":"https://open.spotify.com/playlist/37i9dQZF1DX76Wlfdnj7AP", "thumbnail":None, "source":"fallback"},
    ],
    "fear":     [
        {"title":"Calm Anxiety",         "url":"https://open.spotify.com/playlist/37i9dQZF1DX3Ynp2ANub7f", "thumbnail":None, "source":"fallback"},
        {"title":"Sleep & Relax",        "url":"https://open.spotify.com/playlist/37i9dQZF1DWZd79rJ6a7lp", "thumbnail":None, "source":"fallback"},
        {"title":"Ambient Chill",        "url":"https://open.spotify.com/playlist/37i9dQZF1DX3Ynp2ANub7f", "thumbnail":None, "source":"fallback"},
        {"title":"Deep Focus",           "url":"https://open.spotify.com/playlist/37i9dQZF1DWZeKCadgRdKQ", "thumbnail":None, "source":"fallback"},
    ],
    "love":     [
        {"title":"Love Songs",           "url":"https://open.spotify.com/playlist/37i9dQZF1DXbtzAgnntyvH", "thumbnail":None, "source":"fallback"},
        {"title":"R&B Romance",          "url":"https://open.spotify.com/playlist/37i9dQZF1DWXbttAJcbphz", "thumbnail":None, "source":"fallback"},
        {"title":"Valentine's Day",      "url":"https://open.spotify.com/playlist/37i9dQZF1DX6mvEU1S6INL", "thumbnail":None, "source":"fallback"},
        {"title":"Slow Dance",           "url":"https://open.spotify.com/playlist/37i9dQZF1DX9wC1KY45plY", "thumbnail":None, "source":"fallback"},
    ],
    "surprise": [
        {"title":"Eclectic Mix",         "url":"https://open.spotify.com/playlist/37i9dQZF1DX4dyzvuaRJ0n", "thumbnail":None, "source":"fallback"},
        {"title":"Discover Weekly",      "url":"https://open.spotify.com/playlist/37i9dQZEVXcQ9COmYvdajy", "thumbnail":None, "source":"fallback"},
        {"title":"New Music Friday",     "url":"https://open.spotify.com/playlist/37i9dQZF1DX4JAvHpjipBk", "thumbnail":None, "source":"fallback"},
        {"title":"Viral Hits",           "url":"https://open.spotify.com/playlist/37i9dQZF1DX2L0iB23Enbq", "thumbnail":None, "source":"fallback"},
    ],
}

BOOK_FALLBACK = {
    "sadness":  [
        {"title":"The Midnight Library",        "authors":"Matt Haig",         "url":"https://www.goodreads.com/book/show/52578297", "thumbnail":None, "source":"fallback"},
        {"title":"Option B",                    "authors":"Sheryl Sandberg",   "url":"https://www.goodreads.com/book/show/32938155", "thumbnail":None, "source":"fallback"},
        {"title":"When Breath Becomes Air",     "authors":"Paul Kalanithi",    "url":"https://www.goodreads.com/book/show/25899336", "thumbnail":None, "source":"fallback"},
        {"title":"Man's Search for Meaning",    "authors":"Viktor E. Frankl",  "url":"https://www.goodreads.com/book/show/4069",     "thumbnail":None, "source":"fallback"},
    ],
    "joy":      [
        {"title":"The Hitchhiker's Guide",      "authors":"Douglas Adams",     "url":"https://www.goodreads.com/book/show/11",       "thumbnail":None, "source":"fallback"},
        {"title":"Born a Crime",                "authors":"Trevor Noah",       "url":"https://www.goodreads.com/book/show/29780253", "thumbnail":None, "source":"fallback"},
        {"title":"Yes Please",                  "authors":"Amy Poehler",       "url":"https://www.goodreads.com/book/show/20910157", "thumbnail":None, "source":"fallback"},
        {"title":"The Happiness Lab",           "authors":"Dr. Laurie Santos", "url":"https://www.goodreads.com/book/show/50884616", "thumbnail":None, "source":"fallback"},
    ],
    "anger":    [
        {"title":"The Subtle Art of Not Giving a F*ck","authors":"Mark Manson","url":"https://www.goodreads.com/book/show/28257707","thumbnail":None,"source":"fallback"},
        {"title":"Meditations",                 "authors":"Marcus Aurelius",   "url":"https://www.goodreads.com/book/show/30659",    "thumbnail":None, "source":"fallback"},
        {"title":"Dare to Lead",                "authors":"Brené Brown",       "url":"https://www.goodreads.com/book/show/40109367", "thumbnail":None, "source":"fallback"},
        {"title":"Don't Sweat the Small Stuff", "authors":"Richard Carlson",   "url":"https://www.goodreads.com/book/show/170548",   "thumbnail":None, "source":"fallback"},
    ],
    "fear":     [
        {"title":"Feel the Fear and Do It Anyway","authors":"Susan Jeffers",   "url":"https://www.goodreads.com/book/show/220991",   "thumbnail":None, "source":"fallback"},
        {"title":"Daring Greatly",              "authors":"Brené Brown",       "url":"https://www.goodreads.com/book/show/13588356", "thumbnail":None, "source":"fallback"},
        {"title":"Big Magic",                   "authors":"Elizabeth Gilbert", "url":"https://www.goodreads.com/book/show/24453082", "thumbnail":None, "source":"fallback"},
        {"title":"The Gift of Fear",            "authors":"Gavin de Becker",   "url":"https://www.goodreads.com/book/show/56465",    "thumbnail":None, "source":"fallback"},
    ],
    "love":     [
        {"title":"The Notebook",                "authors":"Nicholas Sparks",   "url":"https://www.goodreads.com/book/show/15931",    "thumbnail":None, "source":"fallback"},
        {"title":"Pride and Prejudice",         "authors":"Jane Austen",       "url":"https://www.goodreads.com/book/show/1885",     "thumbnail":None, "source":"fallback"},
        {"title":"The Five Love Languages",     "authors":"Gary Chapman",      "url":"https://www.goodreads.com/book/show/23878",    "thumbnail":None, "source":"fallback"},
        {"title":"Attachment",                  "authors":"Amir Levine",       "url":"https://www.goodreads.com/book/show/9547888",  "thumbnail":None, "source":"fallback"},
    ],
    "surprise": [
        {"title":"Gone Girl",                   "authors":"Gillian Flynn",     "url":"https://www.goodreads.com/book/show/19288043", "thumbnail":None, "source":"fallback"},
        {"title":"And Then There Were None",    "authors":"Agatha Christie",   "url":"https://www.goodreads.com/book/show/16299",    "thumbnail":None, "source":"fallback"},
        {"title":"The Da Vinci Code",           "authors":"Dan Brown",         "url":"https://www.goodreads.com/book/show/968",      "thumbnail":None, "source":"fallback"},
        {"title":"Knives Out Screenplay",       "authors":"Rian Johnson",      "url":"https://www.goodreads.com/book/show/48570454", "thumbnail":None, "source":"fallback"},
    ],
}

PODCAST_FALLBACK = {
    "sadness":  [
        {"title":"Grief Out Loud",              "podcast":"The Dougy Center",   "url":"https://www.dougy.org/grief-resources/podcast",                        "source":"fallback"},
        {"title":"Terrible, Thanks for Asking", "podcast":"Nora McInerny",      "url":"https://www.ttfa.org",                                                 "source":"fallback"},
        {"title":"Unlocking Us",                "podcast":"Brené Brown",        "url":"https://brenebrown.com/podcast/",                                       "source":"fallback"},
        {"title":"Feel Better Live More",       "podcast":"Dr. Rangan Chatterjee","url":"https://drchatterjee.com/podcast/",                                   "source":"fallback"},
    ],
    "joy":      [
        {"title":"The Happiness Lab",           "podcast":"Dr. Laurie Santos",  "url":"https://www.happinesslab.fm",                                           "source":"fallback"},
        {"title":"SmartLess",                   "podcast":"Jason Bateman",      "url":"https://www.smartless.com",                                             "source":"fallback"},
        {"title":"Good Life Project",           "podcast":"Jonathan Fields",    "url":"https://www.goodlifeproject.com/podcast/",                              "source":"fallback"},
        {"title":"Conan O'Brien Needs A Friend","podcast":"Conan O'Brien",      "url":"https://www.earwolf.com/show/conan-obrien-needs-a-friend/",             "source":"fallback"},
    ],
    "anger":    [
        {"title":"Ten Percent Happier",         "podcast":"Dan Harris",         "url":"https://www.tenpercent.com/podcast",                                    "source":"fallback"},
        {"title":"The Mindful Minute",          "podcast":"Meryl Arnett",       "url":"https://podcasts.apple.com/us/podcast/the-mindful-minute/id1275144444", "source":"fallback"},
        {"title":"Dare to Lead",                "podcast":"Brené Brown",        "url":"https://brenebrown.com/podcast/",                                       "source":"fallback"},
        {"title":"Calm it Down",                "podcast":"Calm it Down",       "url":"https://podcasts.apple.com/us/podcast/calm-it-down/id1435090382",       "source":"fallback"},
    ],
    "fear":     [
        {"title":"The Anxiety Coaches Podcast", "podcast":"Gina Ryan",          "url":"https://theanxietycoachespodcast.com",                                  "source":"fallback"},
        {"title":"Feel Better Live More",       "podcast":"Dr. Rangan Chatterjee","url":"https://drchatterjee.com/podcast/",                                   "source":"fallback"},
        {"title":"The Calm Collective",         "podcast":"Cassandra Eldridge", "url":"https://podcasts.apple.com/us/podcast/the-calm-collective/id1435090382","source":"fallback"},
        {"title":"Overcome Anxiety",            "podcast":"Overcome Anxiety",   "url":"https://podcasts.apple.com/us/podcast/overcome-anxiety/id1441394769",   "source":"fallback"},
    ],
    "love":     [
        {"title":"Where Should We Begin?",      "podcast":"Esther Perel",       "url":"https://www.estherperel.com/podcast",                                   "source":"fallback"},
        {"title":"Love Life with Matthew Hussey","podcast":"Matthew Hussey",    "url":"https://matthewhussey.com/podcast",                                     "source":"fallback"},
        {"title":"The School of Greatness",     "podcast":"Lewis Howes",        "url":"https://lewishowes.com/podcast/",                                       "source":"fallback"},
        {"title":"DTR: Define the Relationship","podcast":"Bumble",             "url":"https://podcasts.apple.com/us/podcast/dtr/id1445095008",                "source":"fallback"},
    ],
    "surprise": [
        {"title":"Stuff You Should Know",       "podcast":"iHeartRadio",        "url":"https://www.iheart.com/podcast/105-stuff-you-should-know-26940277/",    "source":"fallback"},
        {"title":"Radiolab",                    "podcast":"WNYC Studios",       "url":"https://radiolab.org",                                                  "source":"fallback"},
        {"title":"Hidden Brain",                "podcast":"NPR",                "url":"https://hiddenbrain.org",                                               "source":"fallback"},
        {"title":"No Such Thing as a Fish",     "podcast":"QI Elves",           "url":"https://www.nosuchthingasafish.com",                                    "source":"fallback"},
    ],
}



FOOD_FALLBACK = {
    "sadness":  [
        {"title":"Creamy Tomato Soup",       "authors":None, "url":"https://www.allrecipes.com/recipe/39775/", "thumbnail":None, "ready_in":30, "source":"fallback"},
        {"title":"Mac and Cheese",           "authors":None, "url":"https://www.allrecipes.com/recipe/11679/", "thumbnail":None, "ready_in":25, "source":"fallback"},
        {"title":"Warm Ramen Bowl",          "authors":None, "url":"https://www.allrecipes.com/recipe/228823/","thumbnail":None, "ready_in":35, "source":"fallback"},
        {"title":"Chocolate Chip Cookies",   "authors":None, "url":"https://www.allrecipes.com/recipe/10813/", "thumbnail":None, "ready_in":25, "source":"fallback"},
    ],
    "joy":      [
        {"title":"Acai Smoothie Bowl",       "authors":None, "url":"https://www.allrecipes.com/recipe/257498/","thumbnail":None, "ready_in":10, "source":"fallback"},
        {"title":"Greek Salad",              "authors":None, "url":"https://www.allrecipes.com/recipe/14234/", "thumbnail":None, "ready_in":15, "source":"fallback"},
        {"title":"Mango Salsa",              "authors":None, "url":"https://www.allrecipes.com/recipe/74186/", "thumbnail":None, "ready_in":15, "source":"fallback"},
        {"title":"Lemon Pasta",              "authors":None, "url":"https://www.allrecipes.com/recipe/228823/","thumbnail":None, "ready_in":20, "source":"fallback"},
    ],
    "anger":    [
        {"title":"Nashville Hot Chicken",    "authors":None, "url":"https://www.allrecipes.com/recipe/265452/","thumbnail":None, "ready_in":40, "source":"fallback"},
        {"title":"Spicy Beef Tacos",         "authors":None, "url":"https://www.allrecipes.com/recipe/217535/","thumbnail":None, "ready_in":30, "source":"fallback"},
        {"title":"Buffalo Wings",            "authors":None, "url":"https://www.allrecipes.com/recipe/9028/",  "thumbnail":None, "ready_in":35, "source":"fallback"},
        {"title":"Chilli Con Carne",         "authors":None, "url":"https://www.allrecipes.com/recipe/25108/", "thumbnail":None, "ready_in":50, "source":"fallback"},
    ],
    "fear":     [
        {"title":"Chicken Noodle Soup",      "authors":None, "url":"https://www.allrecipes.com/recipe/26317/", "thumbnail":None, "ready_in":40, "source":"fallback"},
        {"title":"Warm Oatmeal",             "authors":None, "url":"https://www.allrecipes.com/recipe/241756/","thumbnail":None, "ready_in":10, "source":"fallback"},
        {"title":"Chamomile Tea & Honey",    "authors":None, "url":"https://www.allrecipes.com/recipe/228823/","thumbnail":None, "ready_in":5,  "source":"fallback"},
        {"title":"Miso Soup",               "authors":None, "url":"https://www.allrecipes.com/recipe/13107/", "thumbnail":None, "ready_in":15, "source":"fallback"},
    ],
    "love":     [
        {"title":"Chocolate Fondue",         "authors":None, "url":"https://www.allrecipes.com/recipe/12167/", "thumbnail":None, "ready_in":20, "source":"fallback"},
        {"title":"Strawberry Crepes",        "authors":None, "url":"https://www.allrecipes.com/recipe/19037/", "thumbnail":None, "ready_in":30, "source":"fallback"},
        {"title":"Tiramisu",                 "authors":None, "url":"https://www.allrecipes.com/recipe/21412/", "thumbnail":None, "ready_in":30, "source":"fallback"},
        {"title":"Lobster Pasta",            "authors":None, "url":"https://www.allrecipes.com/recipe/228823/","thumbnail":None, "ready_in":40, "source":"fallback"},
    ],
    "surprise": [
        {"title":"Korean BBQ Bowl",          "authors":None, "url":"https://www.allrecipes.com/recipe/228823/","thumbnail":None, "ready_in":35, "source":"fallback"},
        {"title":"Japanese Ramen",           "authors":None, "url":"https://www.allrecipes.com/recipe/228823/","thumbnail":None, "ready_in":60, "source":"fallback"},
        {"title":"Moroccan Tagine",          "authors":None, "url":"https://www.allrecipes.com/recipe/69724/", "thumbnail":None, "ready_in":90, "source":"fallback"},
        {"title":"Thai Green Curry",         "authors":None, "url":"https://www.allrecipes.com/recipe/246728/","thumbnail":None, "ready_in":45, "source":"fallback"},
    ],
}

def _save_rec(mood_log_id, category, item, source):
    try:
        execute_write(
            """INSERT INTO recommendations
               (mood_log_id, category, title, external_id, thumbnail, source, metadata)
               VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (mood_log_id, category, item.get("title"),
             item.get("url"), item.get("thumbnail"),
             source, json.dumps(item)),
        )
    except Exception:
        pass


@rec_bp.route("", methods=["POST"])
def get_recommendations():
    data        = request.get_json(force=True)
    mood_log_id = data.get("mood_log_id")
    emotion     = data.get("emotion", "joy")
    mode        = data.get("mode", "amplify")

    if not mood_log_id:
        return jsonify({"error": "mood_log_id is required"}), 400

    # get_strategy now returns a randomly rotated single pick per call
    # so same emotion gives different content every time
    strategy = get_strategy(emotion, mode)

    # The contrast-mapped emotion (for fallback lookups)
    from utils.mood_mapper import CONTRAST_MAP
    strategy_emotion = CONTRAST_MAP.get(emotion, emotion) if mode == "contrast" else emotion

    music_s  = strategy["music"]
    movie_s  = strategy["movie"]
    food_s   = strategy["food"]

    # Music
    playlists = get_playlists(strategy_emotion, music_s["mood_tag"], limit=4)
    if not playlists:
        playlists = MUSIC_FALLBACK.get(strategy_emotion, MUSIC_FALLBACK["joy"])

    # Movies & TV — use randomly rotated genre
    movies   = get_movies(movie_s["tmdb_genre"], limit=4)
    tv_shows = get_tv_shows(movie_s["tmdb_genre"], limit=4)

    # Books — pass book_subject for better results
    books = get_books(strategy_emotion, limit=4)
    if not books:
        books = BOOK_FALLBACK.get(strategy_emotion, BOOK_FALLBACK["joy"])

    # Food — randomly rotated query
    recipes = get_recipes(food_s["query"], limit=4)
    if not recipes:
        recipes = FOOD_FALLBACK.get(strategy_emotion, FOOD_FALLBACK["joy"])

    # Podcasts
    podcasts = get_podcasts(strategy_emotion, limit=4)
    if not podcasts:
        podcasts = PODCAST_FALLBACK.get(strategy_emotion, PODCAST_FALLBACK["joy"])

    # Activities — randomly rotated from extended list
    activities = strategy.get("activities", ACTIVITIES.get(emotion, ACTIVITIES["joy"]))

    # Persist
    for p in playlists:  _save_rec(mood_log_id, "music",    p, p.get("source","fallback"))
    for m in movies:     _save_rec(mood_log_id, "movie",    m, "tmdb")
    for b in books:      _save_rec(mood_log_id, "book",     b, b.get("source","fallback"))
    for r in recipes:    _save_rec(mood_log_id, "food",     r, r.get("source","fallback"))
    for p in podcasts:   _save_rec(mood_log_id, "podcast",  p, p.get("source","fallback"))

    note = generate_recommendation_note(emotion, mode, {
        "music"   : playlists[0] if playlists else {},
        "movie"   : movies[0]    if movies    else {},
        "food"    : recipes[0]   if recipes   else {},
        "activity": activities[0],
    })

    return jsonify({
        "emotion"   : emotion,
        "mode"      : mode,
        "note"      : note,
        "music"     : playlists,
        "movies"    : movies,
        "tv_shows"  : tv_shows,
        "books"     : books,
        "food"      : recipes,
        "podcasts"  : podcasts,
        "activities": activities,
    })


@rec_bp.route("/activities", methods=["GET"])
def get_activities():
    emotion = request.args.get("emotion", "joy")
    return jsonify({"emotion": emotion, "activities": ACTIVITIES.get(emotion, ACTIVITIES["joy"])})
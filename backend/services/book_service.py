"""
Book service — fetches books from Google Books API.
No API key required for basic usage (1000 req/day free).
Optional: add GOOGLE_BOOKS_API_KEY to .env for higher limits.
"""
import requests
from config import Config

BASE_URL = "https://www.googleapis.com/books/v1/volumes"

MOOD_QUERY_MAP = {
    "sadness" : "healing grief hope emotional recovery",
    "joy"     : "happiness comedy adventure feel good",
    "anger"   : "stoicism mindfulness inner peace calm",
    "fear"    : "courage confidence overcoming fear",
    "love"    : "romance love relationships heart",
    "surprise": "mystery thriller suspense twist",
}


def _fix_thumbnail(url: str) -> str:
    """
    Google Books returns http:// thumbnails which browsers block on https sites.
    Also upgrades to a higher resolution image.
    """
    if not url:
        return None
    # Force https
    url = url.replace("http://", "https://")
    # Upgrade to zoom=1 for better quality
    if "zoom=1" not in url:
        url = url + "&zoom=1" if "?" in url else url + "?zoom=1"
    return url


def get_books(emotion: str, limit: int = 4, subject: str = None) -> list[dict]:
    """
    Fetch books from Google Books API matching the emotion.
    Optionally pass a subject override from the strategy map.
    Returns list of book dicts with real thumbnails.
    """
    import random
    queries = [
        MOOD_QUERY_MAP.get(emotion, "wellbeing mindfulness"),
        subject or MOOD_QUERY_MAP.get(emotion, "wellbeing"),
    ]
    query = random.choice(queries)

    params = {
        "q"           : query,
        "maxResults"  : min(limit * 2, 10),  # fetch extra, filter bad ones
        "orderBy"     : "relevance",
        "printType"   : "books",
        "langRestrict": "en",
        "fields"      : "items(id,volumeInfo(title,authors,description,imageLinks,averageRating,pageCount,publishedDate,infoLink,categories))",
    }

    api_key = getattr(Config, "GOOGLE_BOOKS_API_KEY", "")
    if api_key:
        params["key"] = api_key

    try:
        r = requests.get(BASE_URL, params=params, timeout=10)
        if r.status_code != 200:
            return _fallback_books(emotion, limit)

        items = r.json().get("items", [])
        books = []

        for item in items:
            info = item.get("volumeInfo", {})

            # Skip items without title or authors
            if not info.get("title") or not info.get("authors"):
                continue

            # Get best thumbnail available
            image_links = info.get("imageLinks", {})
            thumbnail = (
                image_links.get("medium") or
                image_links.get("large")  or
                image_links.get("thumbnail") or
                image_links.get("smallThumbnail")
            )
            thumbnail = _fix_thumbnail(thumbnail)

            books.append({
                "title"      : info.get("title"),
                "authors"    : ", ".join(info.get("authors", ["Unknown"])[:2]),
                "description": (info.get("description") or "")[:180],
                "rating"     : info.get("averageRating"),
                "pages"      : info.get("pageCount"),
                "thumbnail"  : thumbnail,
                "url"        : info.get("infoLink"),
                "year"       : (info.get("publishedDate") or "")[:4],
                "categories" : (info.get("categories") or [""])[0],
                "source"     : "google_books",
            })

            if len(books) >= limit:
                break

        return books if books else _fallback_books(emotion, limit)

    except Exception as e:
        print(f"[BookService] Error: {e}")
        return _fallback_books(emotion, limit)


def _fallback_books(emotion: str, limit: int) -> list[dict]:
    """Static fallback when Google Books API is unavailable."""
    FALLBACKS = {
        "sadness": [
            {"title":"The Midnight Library",         "authors":"Matt Haig",        "url":"https://books.google.com/books?id=52578297", "year":"2020"},
            {"title":"Option B",                     "authors":"Sheryl Sandberg",  "url":"https://books.google.com/books?id=32938155", "year":"2017"},
            {"title":"When Breath Becomes Air",      "authors":"Paul Kalanithi",   "url":"https://books.google.com/books?id=25899336", "year":"2016"},
            {"title":"Man's Search for Meaning",     "authors":"Viktor E. Frankl", "url":"https://books.google.com/books?id=4069",     "year":"1946"},
        ],
        "joy": [
            {"title":"The Hitchhiker's Guide to the Galaxy","authors":"Douglas Adams", "url":"https://books.google.com/books?id=11",   "year":"1979"},
            {"title":"Born a Crime",                 "authors":"Trevor Noah",      "url":"https://books.google.com/books?id=29780253","year":"2016"},
            {"title":"Yes Please",                   "authors":"Amy Poehler",      "url":"https://books.google.com/books?id=20910157","year":"2014"},
            {"title":"The Happiness Advantage",      "authors":"Shawn Achor",      "url":"https://books.google.com/books?id=20910158","year":"2010"},
        ],
        "anger": [
            {"title":"The Subtle Art of Not Giving a F*ck","authors":"Mark Manson","url":"https://books.google.com/books?id=28257707","year":"2016"},
            {"title":"Meditations",                  "authors":"Marcus Aurelius",  "url":"https://books.google.com/books?id=30659",    "year":"180"},
            {"title":"Daring Greatly",               "authors":"Brené Brown",      "url":"https://books.google.com/books?id=13588356", "year":"2012"},
            {"title":"Don't Sweat the Small Stuff",  "authors":"Richard Carlson",  "url":"https://books.google.com/books?id=170548",   "year":"1997"},
        ],
        "fear": [
            {"title":"Feel the Fear and Do It Anyway","authors":"Susan Jeffers",   "url":"https://books.google.com/books?id=220991",   "year":"1987"},
            {"title":"Daring Greatly",               "authors":"Brené Brown",      "url":"https://books.google.com/books?id=13588356", "year":"2012"},
            {"title":"Big Magic",                    "authors":"Elizabeth Gilbert","url":"https://books.google.com/books?id=24453082", "year":"2015"},
            {"title":"The Gift of Fear",             "authors":"Gavin de Becker",  "url":"https://books.google.com/books?id=56465",    "year":"1997"},
        ],
        "love": [
            {"title":"Pride and Prejudice",          "authors":"Jane Austen",      "url":"https://books.google.com/books?id=1885",     "year":"1813"},
            {"title":"The Notebook",                 "authors":"Nicholas Sparks",  "url":"https://books.google.com/books?id=15931",    "year":"1996"},
            {"title":"The Five Love Languages",      "authors":"Gary Chapman",     "url":"https://books.google.com/books?id=23878",    "year":"1992"},
            {"title":"Attachment",                   "authors":"Amir Levine",      "url":"https://books.google.com/books?id=9547888",  "year":"2010"},
        ],
        "surprise": [
            {"title":"Gone Girl",                    "authors":"Gillian Flynn",    "url":"https://books.google.com/books?id=19288043", "year":"2012"},
            {"title":"And Then There Were None",     "authors":"Agatha Christie",  "url":"https://books.google.com/books?id=16299",    "year":"1939"},
            {"title":"The Girl with the Dragon Tattoo","authors":"Stieg Larsson", "url":"https://books.google.com/books?id=2429135",  "year":"2005"},
            {"title":"The Da Vinci Code",            "authors":"Dan Brown",        "url":"https://books.google.com/books?id=968",      "year":"2003"},
        ],
    }
    items = FALLBACKS.get(emotion, FALLBACKS["joy"])[:limit]
    return [{**item, "thumbnail": None, "rating": None,
             "description": "", "pages": None,
             "categories": "", "source": "fallback"} for item in items]
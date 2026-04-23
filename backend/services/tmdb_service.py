"""
TMDB service — fetches movies and TV shows matching the mood genre.
"""
import requests
from config import Config

BASE_URL = "https://api.themoviedb.org/3"
IMG_BASE = "https://image.tmdb.org/t/p/w500"


def _get(endpoint: str, params: dict) -> dict:
    if not Config.TMDB_API_KEY:
        return {}
    params["api_key"] = Config.TMDB_API_KEY
    try:
        r = requests.get(f"{BASE_URL}{endpoint}", params=params, timeout=10)
        return r.json() if r.status_code == 200 else {}
    except Exception:
        return {}


def get_movies(tmdb_genre: int, limit: int = 4) -> list[dict]:
    """Fetch popular movies for a given TMDB genre id."""
    data = _get("/discover/movie", {
        "with_genres"        : tmdb_genre,
        "sort_by"            : "popularity.desc",
        "vote_average.gte"   : 6.5,
        "page"               : 1,
    })
    items = data.get("results", [])[:limit]
    return [
        {
            "title"    : m.get("title"),
            "overview" : m.get("overview", "")[:200],
            "rating"   : m.get("vote_average"),
            "year"     : (m.get("release_date") or "")[:4],
            "thumbnail": f"{IMG_BASE}{m['poster_path']}" if m.get("poster_path") else None,
            "url"      : f"https://www.themoviedb.org/movie/{m.get('id')}",
            "source"   : "tmdb",
        }
        for m in items
    ]


def get_tv_shows(tmdb_genre: int, limit: int = 4) -> list[dict]:
    """Fetch popular TV shows for a given TMDB genre id."""
    data = _get("/discover/tv", {
        "with_genres"  : tmdb_genre,
        "sort_by"      : "popularity.desc",
        "page"         : 1,
    })
    items = data.get("results", [])[:limit]
    return [
        {
            "title"    : s.get("name"),
            "overview" : s.get("overview", "")[:200],
            "rating"   : s.get("vote_average"),
            "year"     : (s.get("first_air_date") or "")[:4],
            "thumbnail": f"{IMG_BASE}{s['poster_path']}" if s.get("poster_path") else None,
            "url"      : f"https://www.themoviedb.org/tv/{s.get('id')}",
            "source"   : "tmdb",
        }
        for s in items
    ]
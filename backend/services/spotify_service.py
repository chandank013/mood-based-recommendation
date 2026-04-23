"""
Spotify service — fetches playlists matching the mood strategy.
Uses Client Credentials flow (no user login required).
"""
import requests
import base64
from config import Config

_token_cache = {"token": None, "expires_at": 0}


def _get_token() -> str | None:
    import time
    if not Config.SPOTIFY_CLIENT_ID or not Config.SPOTIFY_CLIENT_SECRET:
        return None

    if _token_cache["token"] and time.time() < _token_cache["expires_at"] - 60:
        return _token_cache["token"]

    creds   = f"{Config.SPOTIFY_CLIENT_ID}:{Config.SPOTIFY_CLIENT_SECRET}"
    encoded = base64.b64encode(creds.encode()).decode()

    r = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {encoded}"},
        data={"grant_type": "client_credentials"},
        timeout=10,
    )
    if r.status_code != 200:
        return None

    data = r.json()
    _token_cache["token"]      = data["access_token"]
    _token_cache["expires_at"] = time.time() + data["expires_in"]
    return _token_cache["token"]


def get_playlists(emotion: str, mood_tag: str, limit: int = 4) -> list[dict]:
    """
    Search Spotify for playlists matching the emotion mood tag.
    Returns a list of playlist dicts.
    """
    token = _get_token()
    if not token:
        return []

    query = f"{mood_tag} {emotion} playlist"
    r = requests.get(
        "https://api.spotify.com/v1/search",
        headers={"Authorization": f"Bearer {token}"},
        params={"q": query, "type": "playlist", "limit": limit},
        timeout=10,
    )
    if r.status_code != 200:
        return []

    items = r.json().get("playlists", {}).get("items", [])
    results = []
    for item in items:
        if not item:
            continue
        results.append({
            "title"      : item.get("name"),
            "description": item.get("description", ""),
            "url"        : item.get("external_urls", {}).get("spotify"),
            "thumbnail"  : (item.get("images") or [{}])[0].get("url"),
            "tracks"     : item.get("tracks", {}).get("total", 0),
            "source"     : "spotify",
        })
    return results
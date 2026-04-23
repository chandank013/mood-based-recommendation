import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ── Database ─────────────────────────────
    DB_HOST     = os.getenv("DB_HOST", "localhost")
    DB_PORT     = int(os.getenv("DB_PORT", 3306))
    DB_USER     = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME     = os.getenv("DB_NAME", "mood_recommender")

    # ── Groq ─────────────────────────────────
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL   = os.getenv("GROQ_MODEL", "llama3-8b-8192")

    # ── External APIs ────────────────────────
    SPOTIFY_CLIENT_ID     = os.getenv("SPOTIFY_CLIENT_ID", "")
    SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
    TMDB_API_KEY          = os.getenv("TMDB_API_KEY", "")
    SPOONACULAR_API_KEY   = os.getenv("SPOONACULAR_API_KEY", "")
    GOOGLE_BOOKS_API_KEY   = os.getenv("GOOGLE_BOOKS_API_KEY", "")
    OPENWEATHER_API_KEY   = os.getenv("OPENWEATHER_API_KEY", "")

    # ── Flask ────────────────────────────────
    SECRET_KEY  = os.getenv("SECRET_KEY", "dev-secret-key")
    DEBUG       = os.getenv("FLASK_DEBUG", "True") == "True"

    # ── ML Model paths ───────────────────────
    ML_MODELS_DIR  = os.path.join(os.path.dirname(__file__), "..", "ml", "models")
    SBERT_MODEL    = "all-mpnet-base-v2"
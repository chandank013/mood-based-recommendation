"""
FAISS service — semantic mood matching using vector similarity search.

Instead of exact emotion labels, this finds the closest matching
content items based on semantic distance between the user's mood
embedding and pre-indexed content embeddings.

Install: pip install faiss-cpu sentence-transformers
"""
import os
import json
import numpy as np
import joblib

FAISS_AVAILABLE = False
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    pass

from sentence_transformers import SentenceTransformer
from config import Config

# ── Paths ─────────────────────────────────────────────────────────────────────
FAISS_DIR   = os.path.join(Config.ML_MODELS_DIR, "faiss")
INDEX_PATH  = os.path.join(FAISS_DIR, "content_index.faiss")
META_PATH   = os.path.join(FAISS_DIR, "content_meta.json")

os.makedirs(FAISS_DIR, exist_ok=True)

# ── Sample content corpus to index ────────────────────────────────────────────
# In production, replace with your full content_items from MySQL
CONTENT_CORPUS = [
    # Music
    {"id": "m1", "category": "music", "title": "Rainy Day Acoustic",      "description": "Soft acoustic songs for melancholy moods",          "emotion": "sadness"},
    {"id": "m2", "category": "music", "title": "Feel Good Hits",          "description": "Upbeat pop tracks to boost your energy",            "emotion": "joy"},
    {"id": "m3", "category": "music", "title": "Rage Fuel",               "description": "Hard hitting rock and metal anthems",               "emotion": "anger"},
    {"id": "m4", "category": "music", "title": "Chill Ambient",           "description": "Calming ambient sounds for anxiety relief",         "emotion": "fear"},
    {"id": "m5", "category": "music", "title": "Romantic Evening",        "description": "Smooth R&B for romantic moments",                   "emotion": "love"},
    {"id": "m6", "category": "music", "title": "Eclectic Mix",            "description": "Unpredictable genre-hopping playlist",              "emotion": "surprise"},
    # Movies
    {"id": "v1", "category": "movie", "title": "The Pursuit of Happyness","description": "Inspiring true story of resilience and hope",        "emotion": "sadness"},
    {"id": "v2", "category": "movie", "title": "The Grand Budapest Hotel","description": "Quirky comedy full of charm and laughs",             "emotion": "joy"},
    {"id": "v3", "category": "movie", "title": "John Wick",               "description": "High intensity action thriller",                    "emotion": "anger"},
    {"id": "v4", "category": "movie", "title": "Inside Out",              "description": "Heartwarming story about managing emotions",         "emotion": "fear"},
    {"id": "v5", "category": "movie", "title": "Before Sunrise",          "description": "A beautiful romantic journey through Vienna",        "emotion": "love"},
    {"id": "v6", "category": "movie", "title": "Knives Out",              "description": "A twisty mystery with shocking surprises",           "emotion": "surprise"},
    # Books
    {"id": "b1", "category": "book",  "title": "The Midnight Library",    "description": "A story about regret, hope and second chances",      "emotion": "sadness"},
    {"id": "b2", "category": "book",  "title": "The Hitchhiker's Guide",  "description": "Hilarious sci-fi comedy adventure",                  "emotion": "joy"},
    {"id": "b3", "category": "book",  "title": "Meditations",             "description": "Stoic wisdom for controlling anger and emotions",    "emotion": "anger"},
    {"id": "b4", "category": "book",  "title": "Feel the Fear and Do It Anyway","description": "Overcoming fear and building courage",         "emotion": "fear"},
    {"id": "b5", "category": "book",  "title": "Pride and Prejudice",     "description": "Classic romance of love and misunderstanding",       "emotion": "love"},
    {"id": "b6", "category": "book",  "title": "Gone Girl",               "description": "A psychological thriller full of twists",            "emotion": "surprise"},
    # Food
    {"id": "f1", "category": "food",  "title": "Mac and Cheese",          "description": "Ultimate comfort food for sad days",                "emotion": "sadness"},
    {"id": "f2", "category": "food",  "title": "Açaí Bowl",               "description": "Fresh and energising healthy bowl",                 "emotion": "joy"},
    {"id": "f3", "category": "food",  "title": "Nashville Hot Chicken",   "description": "Fiery spicy chicken for when you need intensity",   "emotion": "anger"},
    {"id": "f4", "category": "food",  "title": "Warm Ramen",              "description": "Comforting noodle soup for anxious evenings",       "emotion": "fear"},
    {"id": "f5", "category": "food",  "title": "Chocolate Fondue",        "description": "Indulgent dessert perfect for romantic evenings",    "emotion": "love"},
    {"id": "f6", "category": "food",  "title": "Korean BBQ",              "description": "Exciting and unexpected flavour experience",         "emotion": "surprise"},
]


class FAISSService:
    def __init__(self):
        self.sbert  = None
        self.index  = None
        self.meta   = []
        self._ready = False

    def _load_sbert(self):
        if self.sbert is None:
            self.sbert = SentenceTransformer(Config.SBERT_MODEL)

    def build_index(self, corpus: list[dict] = None) -> bool:
        """
        Build a FAISS index from the content corpus.
        Encodes the title + description of each item and saves the index.
        Returns True on success.
        """
        if not FAISS_AVAILABLE:
            print("[FAISS] faiss-cpu not installed. Run: pip install faiss-cpu")
            return False

        corpus = corpus or CONTENT_CORPUS
        self._load_sbert()

        texts = [f"{item['title']}. {item['description']}" for item in corpus]
        embeddings = self.sbert.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        ).astype("float32")

        dim   = embeddings.shape[1]  # 768 for all-mpnet-base-v2
        index = faiss.IndexFlatIP(dim)  # Inner product = cosine on normalised vecs
        index.add(embeddings)

        faiss.write_index(index, INDEX_PATH)
        with open(META_PATH, "w") as f:
            json.dump(corpus, f)

        self.index  = index
        self.meta   = corpus
        self._ready = True
        print(f"[FAISS] Index built with {len(corpus)} items → {INDEX_PATH}")
        return True

    def load_index(self) -> bool:
        """Load a pre-built FAISS index from disk."""
        if not FAISS_AVAILABLE:
            return False
        if not os.path.exists(INDEX_PATH):
            return self.build_index()
        try:
            self.index = faiss.read_index(INDEX_PATH)
            with open(META_PATH) as f:
                self.meta = json.load(f)
            self._ready = True
            return True
        except Exception as e:
            print(f"[FAISS] Load failed: {e}")
            return False

    def search(
        self,
        mood_text: str,
        category: str = None,
        top_k: int = 4,
    ) -> list[dict]:
        """
        Semantic search: find content items closest to the mood text.

        Parameters:
            mood_text : raw user mood text
            category  : optional filter — 'music' | 'movie' | 'book' | 'food'
            top_k     : number of results to return

        Returns list of matched content item dicts with a similarity score.
        """
        if not self._ready:
            self.load_index()

        if not self._ready or not FAISS_AVAILABLE:
            return []

        self._load_sbert()
        query_emb = self.sbert.encode(
            [mood_text],
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        ).astype("float32")

        # Search more, then filter by category
        search_k = top_k * 6 if category else top_k
        scores, indices = self.index.search(query_emb, min(search_k, len(self.meta)))

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.meta):
                continue
            item = self.meta[idx]
            if category and item.get("category") != category:
                continue
            results.append({**item, "similarity": round(float(score), 4)})
            if len(results) >= top_k:
                break

        return results

    def search_all_categories(self, mood_text: str, top_k_each: int = 3) -> dict:
        """
        Search across all content categories at once.
        Returns { music: [...], movie: [...], book: [...], food: [...] }
        """
        return {
            "music": self.search(mood_text, category="music", top_k=top_k_each),
            "movie": self.search(mood_text, category="movie", top_k=top_k_each),
            "book" : self.search(mood_text, category="book",  top_k=top_k_each),
            "food" : self.search(mood_text, category="food",  top_k=top_k_each),
        }


# ── Singleton instance ────────────────────────────────────────────────────────
faiss_service = FAISSService()
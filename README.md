# 🎭 Moodly — Mood-Based Recommendation System

An intelligent and empathetic web application for *personalised content discovery* — featuring AI-powered multi-modal mood detection, BERT + PyTorch deep learning emotion classification, Word2Vec embeddings, and real-time content recommendations across six categories — *through an intuitive browser-based interface with seamless real-time interaction*.

🎯 *GitHub Repository:*
👉 [https://github.com/chandank013/moodly](https://github.com/chandank013/mood-based-recommendation)

*Live Demo:*
👉 [Run locally at http://localhost:3000](http://localhost:3000)

---

<p align="center">
  <img src="docs/page-01.png" width="45%" />
  <img src="docs/page-02.png" width="45%" />
</p>

---

Built using **React 18 + Vite**, **Flask 3**, **BERT (bert-base-uncased) + PyTorch**, **Word2Vec (Gensim)**, **Groq LLaMA 3**, **MySQL 8.0**, and **six external content APIs**, this project transforms the way people discover music, movies, books, food, podcasts, and activities — by understanding *how they feel right now*. 🎵🎬📖🍽️🎙️⚡

---

## 🧑‍💻 Team Members

| Name | Roll No. | Contribution |
|------|----------|-----------|
| **Anchal Jaiswal** | 24bds003 | ML Pipeline, Word2Vec Embeddings,External APIs |
| **Chandan Kumar** | 24bds013 | Backend API, Flask Routes, MySQL Schema, JWT Auth, Groq LLaMA 3 integration |
| **Nitish Naveen** | 24bds050 | React Frontend, UI/UX Design, Vite Integration |
| **Prem Kishan** | 24bds057 | Model Training, Recommendation Engine |

**Project Guide:** Asst. Prof. Shirshendu Layek
**Department:** Data Science and Artificial Intelligence, Indian Institute of Information Technology Dharwad.

---

## 🧰 Tech Stack

| Technology | Purpose |
|------------|---------|
| **React 18 + Vite** | Fast frontend SPA with hot module replacement |
| **Tailwind CSS** | Slate & Terracotta utility-first design system |
| **Flask 3.0** | Python REST API backend with blueprint routing |
| **Python 3.11** | Primary language for all backend and ML logic |
| **BERT (bert-base-uncased)** | 768-dim contextual token representations from HuggingFace |
| **PyTorch 2.x** | Deep learning — BertMLP, BertBiLSTM, BertCNN, BertTransformer |
| **Word2Vec (Gensim)** | 100-dim mean-pool embeddings (lightweight baseline) |
| **TensorFlow / Keras** | Word2Vec DL baseline (MLP, BiLSTM, CNN1D, Transformer) |
| **Groq API (LLaMA 3)** | Low-confidence mood verification + recommendation narration |
| **MySQL 8.0** | Persistent storage — users, mood logs, recommendations |
| **PyJWT + bcrypt** | JWT authentication and password hashing |
| **Spotify Web API** | Playlist recommendations by mood tag and genre seed |
| **TMDB API** | Movies and TV shows by TMDB genre ID |
| **Google Books API** | Book recommendations (free tier — no key needed) |
| **Spoonacular API** | Recipes by cuisine and food query |
| **Listen Notes API** | Podcast episode recommendations |
| **DeepFace + OpenCV** | Facial expression → dominant emotion from webcam |
| **librosa + soundfile** | MFCC / energy / ZCR audio feature extraction |
| **Web Bluetooth API** | Heart rate monitor BPM → emotion heuristic |
| **Socket.IO** | Real-time community mood live feed |
| **Recharts** | Mood journey area chart and emotion timeline |
| **scikit-learn** | LabelEncoder, classification report, confusion matrix |
| **pandas + NumPy** | Dataset loading, preprocessing, embedding arrays |

---

## 🚀 Features

### For Users 👥
- ✍️ **Text Input** — Describe your mood freely; BERT + Deep Learning classifies it in < 100ms
- 😊 **Emoji / Slider** — Select an emotion emoji or use valence-arousal sliders
- 📷 **Webcam** — Real-time facial expression analysis via DeepFace
- 🎙️ **Voice** — Short audio clip analysed with librosa MFCC features
- 💓 **Wearable** — Bluetooth heart rate monitor BPM → emotion mapping
- 🎨 **Mood Blend** — Select up to 3 emotions with per-emotion intensity sliders
- ✦ **Match Mood** — Recommendations that amplify your current emotional state
- ↭ **Shift Mood** — Contrast mode shifts you toward a different feeling
- 🎵 **Music** — Spotify playlists with 5 randomly rotated seeds per emotion
- 🎬 **Movies & TV** — TMDB-powered with 4–5 genre options per emotion
- 📖 **Books** — Google Books with mood-matched subject queries
- 🍽️ **Food & Recipes** — Spoonacular with 5 food query variants per emotion
- 🎙️ **Podcasts** — Listen Notes + curated static fallback per emotion
- ⚡ **Activities** — 6-item activity pool with random 4-item selection each call
- ◈ **Mood Journey** — Personal mood history synced across devices
- ❋ **Community** — Anonymised trending emotions + 24-hour stacked histogram

### For Authenticated Users 🔐
- 🔐 **Register / Login** — JWT tokens (7-day expiry) with bcrypt password hashing
- 📊 **Persistent Journey** — All mood logs tied to `user_id` — works across sessions and devices
- 👤 **Profile Dropdown** — Username avatar, My Journey, Sign Out — Sign In button hidden after login
- 📈 **Emotion Summary** — Percentage breakdown, dominant mood card, average confidence
- 🗓️ **Days Filter** — View 7, 14, or 30-day windows on journey page

---

## 🎯 Key Functionalities

### 🧠 ML Pipeline — BERT + Deep Learning (PyTorch)

The emotion classifier is built in three stages:

**Stage 1 — BERT Tokenisation (preprocess.py)**
- HuggingFace `BertTokenizer` (bert-base-uncased), `max_length=128`
- `padding="max_length"`, `truncation=True`, `return_tensors="pt"`
- Saves `{split}_tokens.pt` with `input_ids`, `attention_mask`, `token_type_ids`, `labels`
- Tokenizer saved to `models/tokenizer/` for inference

**Stage 2 — Four Competing DL Architectures (train.py)**

| Model | BERT Input | Head Architecture | Typical Val F1 |
|-------|-----------|-------------------|----------------|
| BertMLP | `[CLS]` pooler (768-d) | Dense 768→512→256→6 + LayerNorm + GELU | ~0.91 |
| BertBiLSTM | All tokens (128×768) | 2-layer BiLSTM (hidden=256) + attention pooling | ~0.93 |
| BertCNN | All tokens (128×768) | 4× Conv1D (k=2,3,4,5) + GlobalMaxPool + concat | ~0.92 |
| **BertTransformer** | All tokens (128×768) | **2× Pre-LN Transformer (8 heads, ff=1024) + masked mean pool** | **~0.94** |

**Training configuration:**
- Optimiser: AdamW, `lr=2e-5`, `weight_decay=0.01`
- Schedule: Linear warmup (10% steps) → cosine decay
- Loss: Label-smoothing cross-entropy (ε=0.1)
- Gradient clipping: `||∇||₂ ≤ 1.0`
- Early stopping: patience=3 on validation F1
- Batch size: 16, max 10 epochs

**Stage 3 — Model Selection + Evaluation (evaluate.py)**
- All 4 models trained; best by val F1 saved as `mood_bert_model.pt`
- Full classification report + confusion matrix on val + test splits
- Comparison table printed across all architectures

### 🔄 Groq Verification Layer

When BERT confidence < 0.55, Groq LLaMA 3 is called for secondary classification. Groq also generates a personalised recommendation note explaining why the suggested content matches the user's emotional state.

### 🗺️ Genre Mapping Engine

Each emotion maps to **lists** of options — randomly selected per call so content never repeats:

| Emotion | TMDB Genres | Spotify Seeds | Food Queries | Activities |
|---------|-------------|---------------|--------------|------------|
| Sadness | Drama, Family, Romance, History | 5 options | 5 options | 6 options |
| Joy | Comedy, Adventure, Animation, Music | 5 options | 5 options | 6 options |
| Anger | Action, Thriller, Crime, War | 5 options | 5 options | 6 options |
| Fear | Comedy, Family, Animation, Music | 5 options | 5 options | 6 options |
| Love | Romance, Drama, Comedy, Music | 5 options | 5 options | 6 options |
| Surprise | Mystery, Sci-Fi, Thriller, Fantasy | 5 options | 5 options | 6 options |

**Contrast map (psychologically grounded):**
- `fear → joy` · `sadness → joy` · `anger → love` · `joy → surprise` · `love → surprise` · `surprise → fear`

---

## 🎯 System Workflow

### User Journey (Text Mood)
1. Open `http://localhost:3000` → Auth modal appears → Register or Sign In
2. Register → Redirected to **login tab** (not auto-logged in) with pre-filled email + success message
3. Login → JWT stored → Home page opens → Sign In button replaced with username dropdown
4. Type mood text → BERT tokeniser encodes → BertTransformer predicts emotion + confidence
5. If confidence < 0.55 → Groq LLaMA 3 verifies (Call 1)
6. `get_strategy(emotion, mode)` → random genre params selected from lists
7. Parallel API calls → Spotify, TMDB, Google Books, Spoonacular, Listen Notes
8. Groq narration generated (Call 2)
9. Mood log + recommendations persisted to MySQL under `user_id`
10. Results page renders — Music, Movies, Books, Food, Podcasts, Activities

### User Journey (Webcam Mood)
1. Click Camera tab → Start Camera → Capture Frame
2. JPEG snapshot base64-encoded in browser
3. `POST /api/mood/face` → DeepFace analyses → dominant emotion extracted
4. Same pipeline from step 6 above

### User Journey (Shift Mood)
1. On Results page, click `↭ Shift Mood`
2. `mode="contrast"` → `CONTRAST_MAP[emotion]` applied before genre lookup
3. `useRecommendations` detects new `mode` in cache key → clears + re-fetches
4. Different TMDB genre, Spotify seed, food query, book subject returned

---

## 🧩 Project Structure

```text
moodly/
│
├── ml/                              # Machine learning pipeline
│   ├── datasets/
│   │   ├── train.txt                # text;emotion pairs (semicolon-separated)
│   │   ├── val.txt
│   │   └── test.txt
│   ├── preprocess.py                # BERT tokenisation + dataset preparation
│   ├── train.py                     # BertMLP / BertBiLSTM / BertCNN / BertTransformer
│   ├── evaluate.py                  # Classification report + confusion matrix
│   └── models/                      # Saved artefacts (git-ignored, ~1.5 GB)
│       ├── mood_bert_model.pt        # Best PyTorch model weights
│       ├── tokenizer/                # BertTokenizer saved files
│       ├── label_encoder.pkl         # sklearn LabelEncoder
│       ├── model_meta.json           # Best model name, metrics, config
│       ├── config.json               # BERT config (n_classes, max_len, etc.)
│       ├── train/val/test_tokens.pt  # Pre-tokenised PyTorch tensors
│       └── evaluation_report.json   # Per-split accuracy and F1
│
├── backend/                         # Flask REST API
│   ├── app.py                       # Entry point — blueprint registration
│   ├── config.py                    # Env vars + ML model path config
│   ├── .env                         # API keys and DB credentials
│   ├── db/
│   │   ├── connection.py            # PyMySQL helper functions
│   │   └── schema.sql               # Full MySQL schema with auth tables
│   ├── routes/
│   │   ├── auth.py                  # POST /api/auth/register|login|logout|me
│   │   ├── mood.py                  # POST /api/mood/text|emoji|face|voice|passive
│   │   ├── recommendations.py       # POST /api/recommendations
│   │   ├── journey.py               # GET  /api/journey/history|summary
│   │   └── social.py                # GET  /api/social/trending|pulse|contribute
│   ├── services/
│   │   ├── model_service.py         # BERT tokeniser + DL inference
│   │   ├── groq_service.py          # Groq LLaMA 3 verify + narrate
│   │   ├── spotify_service.py       # Spotify Web API
│   │   ├── tmdb_service.py          # TMDB movies + TV shows
│   │   ├── book_service.py          # Google Books API
│   │   ├── food_service.py          # Spoonacular recipes
│   │   ├── podcast_service.py       # Listen Notes + static fallback
│   │   ├── weather_service.py       # OpenWeatherMap passive signal
│   │   ├── facial_service.py        # DeepFace webcam emotion analysis
│   │   ├── voice_service.py         # librosa MFCC audio analysis
│   │   ├── passive_service.py       # Time + weather + BPM blending
│   │   └── faiss_service.py         # FAISS semantic mood-to-content search
│   └── utils/
│       ├── mood_mapper.py           # Emotion strategy map + contrast map + rotation
│       ├── blend_handler.py         # Multi-emotion blend parsing
│       └── context_handler.py       # Time/weather/companion context
│
├── frontend/                        # React + Vite SPA
│   ├── index.html
│   ├── vite.config.js               # Proxy /api → Flask :5000
│   ├── tailwind.config.js           # Slate & Terracotta design tokens
│   ├── package.json
│   └── src/
│       ├── App.jsx                  # Router + AuthProvider + Navbar + ProtectedRoute
│       ├── main.jsx                 # React entry point
│       ├── index.css                # CSS variables + glass + animations
│       ├── services/api.js          # Axios instance with JWT header injection
│       ├── hooks/
│       │   ├── useAuth.jsx          # AuthContext — register/login/logout + state timing fix
│       │   ├── useMoodDetection.js  # All 7 modality detection hooks
│       │   ├── useRecommendations.js # Cache-key based re-fetch on mode change
│       │   └── useSocket.js         # Socket.IO community feed
│       ├── components/
│       │   ├── Auth/AuthModal.jsx   # Login/Register modal — redirects to login after register
│       │   ├── Controls/            # Navbar, ContrastToggle, ContextPanel
│       │   ├── MoodInput/           # TextInput, EmojiPicker, SliderInput,
│       │   │                          WebcamCapture, VoiceCapture, WearableInput, MoodBlend
│       │   ├── Recommendations/     # MusicSection, MovieSection, BookSection,
│       │   │                          FoodSection, ActivitySection (+ inline PodcastSection)
│       │   ├── MoodJourney/         # JourneyChart (Recharts), MoodHistory
│       │   └── SocialMood/          # TrendingMoods, MoodPulse
│       └── pages/
│           ├── Home.jsx             # 7-tab mood input + context panel
│           ├── Results.jsx          # Recommendations + mode toggle
│           └── Journey.jsx          # Mood history + community tab
│
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

---

## ⚙ Installation & Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- MySQL 8.0+
- Groq API key — free at [console.groq.com](https://console.groq.com)

### 1. Clone the repository

```bash
git clone https://github.com/chandank013/mood-based-recommendation.git
cd moodly
```

### 2. Install Python dependencies

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Install ML dependencies

```bash
# Core ML (required)
pip install torch transformers gensim scikit-learn pandas numpy joblib

# Webcam emotion detection (optional)
pip install deepface opencv-python

# Voice emotion detection (optional)
pip install librosa soundfile

# TensorFlow (only for Word2Vec DL baseline — not needed for BERT pipeline)
pip install tensorflow keras
```

### 4. Set up MySQL database

```bash
mysql -u root -p < backend/db/schema.sql
```

### 5. Configure environment variables

Create `backend/.env`:

```env
# ── Database ────────────────────────────────────────────
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=mood_recommender

# ── Groq LLM (required) ─────────────────────────────────
GROQ_API_KEY=gsk_your_key_here
GROQ_MODEL=llama3-8b-8192

# ── Content APIs (all optional — fallback content works without them) ──
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
TMDB_API_KEY=your_tmdb_api_key
SPOONACULAR_API_KEY=your_spoonacular_api_key
GOOGLE_BOOKS_API_KEY=your_google_books_api_key
LISTEN_NOTES_API_KEY=your_listen_notes_api_key

# ── Flask ────────────────────────────────────────────────
SECRET_KEY=your_jwt_secret_key_here
FLASK_DEBUG=True

# ── ML Model Directory ───────────────────────────────────
ML_MODELS_DIR=../ml/models
```

### 6. Train the ML model

```bash
cd ml

# Step 1 — BERT tokenisation (downloads ~250 MB bert-base-uncased on first run)
python preprocess.py

# Step 2 — Train all 4 architectures, auto-select best by val F1
python train.py

# Step 3 — Evaluate on test set, generate classification report
python evaluate.py
```

Expected output after `train.py`:
```
  ─────────────────────────────────────────────────────────────────
  Model             Val Acc     Val F1         Params
  ─────────────────────────────────────────────────────────────────
  BertMLP           0.9052      0.9100      109,491,462
  BertBiLSTM        0.9212      0.9280      218,635,782
  BertCNN           0.9158      0.9220      109,804,294
  BertTransformer   0.9360      0.9410      121,561,862

  ✓ Best → BertTransformer  (Val F1=0.9410)
```

### 7. Copy model service to backend

```bash
cp ml/model_service.py backend/services/model_service.py
```

### 8. Run the backend

```bash
cd backend
python app.py
# Running on http://localhost:5000
```

### 9. Run the frontend

```bash
cd frontend
npm install
npm run dev
# Running on http://localhost:3000
```

### 10. Open in browser

```
http://localhost:3000
```

---

## 🌐 API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/auth/register` | None | Create account — does NOT auto-login |
| `POST` | `/api/auth/login` | None | Authenticate; receive 7-day JWT |
| `POST` | `/api/auth/logout` | JWT | Client-side token invalidation |
| `GET`  | `/api/auth/me` | JWT | Current user profile + total mood count |
| `POST` | `/api/mood/text` | Optional | Text → BERT → emotion + confidence |
| `POST` | `/api/mood/emoji` | Optional | Emoji/slider → emotion |
| `POST` | `/api/mood/face` | Optional | Webcam base64 → DeepFace → emotion |
| `POST` | `/api/mood/voice` | Optional | Audio base64 → librosa → emotion |
| `GET`  | `/api/mood/passive` | None | Time-of-day + weather mood hint |
| `POST` | `/api/recommendations` | Optional | mood_log_id + emotion + mode → 6 categories |
| `GET`  | `/api/journey/history` | Optional | Mood log entries (user or session) |
| `GET`  | `/api/journey/summary` | Optional | Emotion % breakdown + dominant mood |
| `GET`  | `/api/social/trending` | None | Top emotions in the last hour |
| `GET`  | `/api/social/pulse` | None | 24-hour hourly emotion counts |
| `POST` | `/api/social/contribute` | None | Add emotion to community aggregation |
| `GET`  | `/api/health` | None | Backend health + API key status |

---

## 🗄 Database Schema

```sql
-- Auth
users            -- id, username, email, password_hash, created_at, last_login
sessions         -- id, session_id, user_id (FK → users), created_at, last_seen

-- Core
mood_logs        -- id, user_id (FK), session_id, raw_input, input_type,
                 --   emotion, confidence, intensity, context_time,
                 --   context_who, mode, weather, location, created_at
recommendations  -- id, mood_log_id (FK), user_id (FK), category (ENUM),
                 --   title, external_id, thumbnail, source, metadata (JSON)

-- Social
social_moods     -- id, emotion, count, hour_slot (UNIQUE per emotion+hour)
context_signals  -- id, user_id (FK), session_id, signal_type, signal_value
```

All foreign keys use `ON DELETE SET NULL` — deleting a user anonymises their history rather than destroying it.

---

## 🎨 UI Design System

### Colour Palette — Slate & Terracotta

| CSS Variable | Hex | Usage |
|---|---|---|
| `--slate` | `#0F172A` | Page background + deepest surface |
| `--navy` | `#1E293B` | Card backgrounds |
| `--denim` | `#334155` | Borders, dividers, inactive states |
| `--terracotta` | `#E07A5F` | Primary accent — buttons, badges, highlights |
| `--peach` | `#F2A28A` | Secondary accent — hover states |
| `--ivory` | `#FDF6F0` | Primary text, headings |
| `--muted` | `#94A3B8` | Secondary text, placeholders, metadata |

### Component Classes (index.css)
- `.glass` — frosted glass card with blur backdrop
- `.btn-primary` — terracotta gradient button with hover lift
- `.btn-ghost` — outline button, terracotta on hover
- `.mood-input` — dark input with terracotta focus ring
- `.rec-card` — recommendation card with hover lift + border glow
- `.tab-active` — active tab state with terracotta gradient
- `.shimmer` — animated loading placeholder
- `.emotion-badge` — terracotta pill showing detected emotion
- `.animate-fade-up` — 0.55s ease-both entry animation
- `.animate-float` — 3s floating loop (used on emotion emoji)

---

## 📈 Results & Performance

| Metric | Value | Notes |
|--------|-------|-------|
| Best architecture | BertTransformer | Pre-LN, 8-head self-attention |
| Test weighted F1 | **0.941** | 6-class emotion classification |
| Test accuracy | **93.6%** | Held-out test set |
| BERT inference latency | < 100 ms | CPU local |
| Groq verification | ~400 ms | Triggered only if confidence < 0.55 |
| End-to-end recommendation | < 2.0 s | Including API calls |
| Word2Vec vocab size | ~8,000 tokens | Trained on full corpus |
| Input modalities | 7 | Text, emoji, slider, webcam, voice, wearable, blend |
| Recommendation categories | 6 | Music, movies, books, food, podcasts, activities |
| Emotions classified | 6 | Sadness, joy, anger, fear, love, surprise |
| Genre options per emotion | 4–5 per category | Random rotation every call |
| Food query variants | 5 per emotion | Random rotation every call |
| Fallback content | All 6 categories | Works without any API keys |

---

## 🔮 Future Enhancements

- 🤖 **Fine-tuned DistilBERT** — domain-adapted for emotion text at half the BERT parameters
- 🔗 **Multimodal fusion** — unified model fusing text + audio + facial embeddings
- 🔍 **FAISS semantic search** — cosine similarity over mood embeddings for content retrieval
- 📱 **React Native app** — iOS and Android port
- 🔔 **Push notifications** — daily mood check-in via web push API
- 🌐 **Multilingual input** — Tamil, Hindi, Hinglish (mBERT / IndicBERT)
- 📊 **Advanced analytics** — emotion radar chart, weekly well-being score, calendar heatmap
- 🤝 **Social sharing** — share mood playlists and reading lists with friends
- 💓 **Continuous wearable** — Apple Watch / Wear OS passive mood monitoring
- 🦙 **Local LLM** — replace Groq with Ollama for zero-internet deployment

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch — `git checkout -b feature/YourFeature`
3. Commit your changes — `git commit -m 'Add YourFeature'`
4. Push — `git push origin feature/YourFeature`
5. Open a Pull Request

---

## 📞 Contact & Support

- **GitHub Issues**: [Report a bug](https://github.com/your-chandank013/mood-based-recommendation/issues)
- **Email**: ck263022@gmail.com
---

## 🙏 Acknowledgments

- **Indian Institute of Information Technology Dharwad** for academic support
- **Asst. Prof. ShirShendu Layek** for project guidance and continuous feedback
- **Groq** for blazing-fast LLaMA 3 inference via the free API
- **HuggingFace** for BERT checkpoints and the Transformers library
- **Spotify, TMDB, Google Books, Spoonacular, Listen Notes** for content APIs
- **Gensim** for the Word2Vec implementation
- **PyTorch** and the open-source deep learning community

---

## 💡 Authors

** Anchal Jaiswal · Chandan Kumar · Nitish Naveen · Prem Kishan**
Department of Data Science and Artificial Intelligence
Indian Institute of Information Technology Dharwad.

Built with ❤️ using React, Flask, BERT, PyTorch, Word2Vec, Groq LLaMA 3, and MySQL.

---

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?style=for-the-badge&logo=github)](https://github.com/chandank013/mood-based-recommendation)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.x-EE4C2C?style=for-the-badge&logo=pytorch)](https://pytorch.org)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react)](https://reactjs.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-blue?style=for-the-badge&logo=mysql)](https://mysql.com)
[![BERT](https://img.shields.io/badge/BERT-bert--base--uncased-orange?style=for-the-badge)](https://huggingface.co/bert-base-uncased)

---

*⭐ If you find this project helpful, please give it a star on GitHub!*
"""
preprocess.py — BERT tokenization + dataset preparation for Mood Recommender.

Pipeline:
  1. Load semicolon-separated text;emotion dataset
  2. Clean text
  3. Tokenize with HuggingFace BERT tokenizer (bert-base-uncased)
  4. Save: label_encoder.pkl, tokenized tensors, cleaned CSVs
"""

import os
import re
import joblib
import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(BASE_DIR, "datasets")
MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

TRAIN_PATH = os.path.join(DATA_DIR, "train.txt")
TEST_PATH  = os.path.join(DATA_DIR, "test.txt")
VAL_PATH   = os.path.join(DATA_DIR, "val.txt")

# ── Config ────────────────────────────────────────────────────────────────────
BERT_MODEL  = "bert-base-uncased"   # Pre-trained BERT checkpoint
MAX_LEN     = 128                   # Max token length (covers 99%+ of emotion sentences)
N_CLASSES   = 6
EMOTIONS    = ["sadness", "joy", "anger", "fear", "love", "surprise"]

EMOTION_CONTENT_MAP = {
    "sadness" : {"music":"soft_acoustic",  "movie":"comfort_drama",   "food":"comfort_food",   "activity":"yoga"},
    "joy"     : {"music":"upbeat_pop",     "movie":"comedy",          "food":"fresh_light",    "activity":"hiit"},
    "anger"   : {"music":"hard_rock",      "movie":"action_thriller", "food":"spicy_food",     "activity":"boxing"},
    "fear"    : {"music":"ambient_calm",   "movie":"feel_good",       "food":"warm_soup",      "activity":"meditation"},
    "love"    : {"music":"romantic_rnb",   "movie":"romance",         "food":"desserts",       "activity":"couples_yoga"},
    "surprise": {"music":"eclectic",       "movie":"scifi_mystery",   "food":"exotic_cuisine", "activity":"new_adventure"},
}


# ── Text cleaning ─────────────────────────────────────────────────────────────
def clean_text(text: str) -> str:
    """Light cleaning — BERT handles tokenisation internally."""
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


# ── File loader ───────────────────────────────────────────────────────────────
def load_file(path: str) -> pd.DataFrame:
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or ";" not in line:
                continue
            parts = line.rsplit(";", 1)
            rows.append({"text": parts[0].strip(), "emotion": parts[1].strip()})
    return pd.DataFrame(rows)


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(subset=["text", "emotion"]).copy()
    df["text"]    = df["text"].apply(clean_text)
    df["emotion"] = df["emotion"].str.lower().str.strip()
    df = df[df["text"].str.len() > 2]
    for col in ["music", "movie", "food", "activity"]:
        df[col] = df["emotion"].map(
            lambda e: EMOTION_CONTENT_MAP.get(e, {}).get(col, "general")
        )
    return df


# ── BERT tokenization ─────────────────────────────────────────────────────────
def tokenize_dataset(texts: list[str], tokenizer) -> dict:
    """
    Tokenize a list of texts with BERT tokenizer.
    Returns dict with input_ids, attention_mask, token_type_ids.
    """
    encoding = tokenizer(
        texts,
        max_length      = MAX_LEN,
        padding         = "max_length",
        truncation      = True,
        return_tensors  = "pt",   # PyTorch tensors
    )
    return {
        "input_ids"      : encoding["input_ids"],
        "attention_mask" : encoding["attention_mask"],
        "token_type_ids" : encoding["token_type_ids"],
    }


# ── Main ──────────────────────────────────────────────────────────────────────
def run():
    print("=" * 45)
    print("  MOOD RECOMMENDER — PREPROCESSING (BERT + PyTorch)")
    print("=" * 45)

    from transformers import BertTokenizer
    import torch

    # Load and clean data
    train_df = preprocess(load_file(TRAIN_PATH))
    test_df  = preprocess(load_file(TEST_PATH))
    val_df   = preprocess(load_file(VAL_PATH))

    print(f"\n[train]  {len(train_df):>5} rows")
    print(f"[test ]  {len(test_df):>5} rows")
    print(f"[val  ]  {len(val_df):>5} rows")

    print("\nEmotion distribution (train):")
    print(train_df["emotion"].value_counts().to_string())

    # Label encoder
    le = LabelEncoder()
    le.fit(train_df["emotion"])
    print(f"\nClasses : {list(le.classes_)}")

    # Save cleaned CSVs
    train_df.to_csv(os.path.join(MODELS_DIR, "train_clean.csv"), index=False)
    test_df.to_csv (os.path.join(MODELS_DIR, "test_clean.csv"),  index=False)
    val_df.to_csv  (os.path.join(MODELS_DIR, "val_clean.csv"),   index=False)
    joblib.dump(le, os.path.join(MODELS_DIR, "label_encoder.pkl"))

    # Load BERT tokenizer (downloads ~250MB on first run)
    print(f"\n[BERT] Loading tokenizer: {BERT_MODEL} ...")
    tokenizer = BertTokenizer.from_pretrained(BERT_MODEL)
    tokenizer.save_pretrained(os.path.join(MODELS_DIR, "tokenizer"))

    # Tokenize all splits
    print("[BERT] Tokenizing datasets ...")
    for split, df in [("train", train_df), ("val", val_df), ("test", test_df)]:
        texts  = df["text"].tolist()
        labels = torch.tensor(le.transform(df["emotion"]), dtype=torch.long)
        tokens = tokenize_dataset(texts, tokenizer)

        torch.save({
            "input_ids"      : tokens["input_ids"],
            "attention_mask" : tokens["attention_mask"],
            "token_type_ids" : tokens["token_type_ids"],
            "labels"         : labels,
        }, os.path.join(MODELS_DIR, f"{split}_tokens.pt"))

        print(f"  [{split}] input_ids shape: {tokens['input_ids'].shape}")

    # Save config
    config = {
        "bert_model" : BERT_MODEL,
        "max_len"    : MAX_LEN,
        "n_classes"  : N_CLASSES,
        "classes"    : list(le.classes_),
    }
    with open(os.path.join(MODELS_DIR, "config.json"), "w") as f:
        json.dump(config, f, indent=2)

    print("\n[OK] Saved → models/label_encoder.pkl")
    print("[OK] Saved → models/tokenizer/")
    print("[OK] Saved → models/train_tokens.pt, val_tokens.pt, test_tokens.pt")
    print("[OK] Saved → models/config.json")
    print("=" * 45)
    return train_df, val_df, test_df, le, tokenizer


if __name__ == "__main__":
    run()
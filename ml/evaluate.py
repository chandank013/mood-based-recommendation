"""
evaluate.py — Full evaluation of the trained BERT-based mood classifier.

Generates:
  - Per-class precision, recall, F1 for val + test splits
  - Confusion matrix
  - Misclassified examples analysis
  - evaluation_report.json
"""

import os
import json
import warnings
warnings.filterwarnings("ignore")

import joblib
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import (
    classification_report, confusion_matrix,
    accuracy_score, f1_score
)
from transformers import BertTokenizer, BertModel
import torch.nn as nn
import torch.nn.functional as F

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ── Rebuild model class (import from train.py) ────────────────────────────────
# We redefine here for standalone execution
BERT_HIDDEN = 768
DROPOUT     = 0.3
MAX_LEN     = 128


class MultiHeadSelfAttention(nn.Module):
    def __init__(self, d_model, n_heads=8, dropout=0.1):
        super().__init__()
        self.d_k = d_model // n_heads
        self.n_heads = n_heads
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
        self.drop = nn.Dropout(dropout)

    def forward(self, x, mask=None):
        B, L, D = x.shape
        Q = self.W_q(x).view(B, L, self.n_heads, self.d_k).transpose(1, 2)
        K = self.W_k(x).view(B, L, self.n_heads, self.d_k).transpose(1, 2)
        V = self.W_v(x).view(B, L, self.n_heads, self.d_k).transpose(1, 2)
        scores = (Q @ K.transpose(-2, -1)) / (self.d_k ** 0.5)
        if mask is not None:
            scores = scores.masked_fill(mask.unsqueeze(1).unsqueeze(2) == 0, -1e9)
        attn = self.drop(torch.softmax(scores, dim=-1))
        out  = (attn @ V).transpose(1, 2).contiguous().view(B, L, D)
        return self.W_o(out)


class TransformerEncoderBlock(nn.Module):
    def __init__(self, d_model, n_heads, ff_dim, dropout=0.1):
        super().__init__()
        self.self_attn = MultiHeadSelfAttention(d_model, n_heads, dropout)
        self.ff   = nn.Sequential(nn.Linear(d_model, ff_dim), nn.GELU(),
                                   nn.Dropout(dropout), nn.Linear(ff_dim, d_model))
        self.ln1  = nn.LayerNorm(d_model)
        self.ln2  = nn.LayerNorm(d_model)
        self.drop = nn.Dropout(dropout)

    def forward(self, x, mask=None):
        x = x + self.drop(self.self_attn(self.ln1(x), mask))
        x = x + self.drop(self.ff(self.ln2(x)))
        return x


MODEL_CLASSES = {}

def _register_models(n_classes):
    from transformers import BertModel

    class BertMLP(nn.Module):
        def __init__(self):
            super().__init__()
            self.bert = BertModel.from_pretrained("bert-base-uncased")
            self.classifier = nn.Sequential(
                nn.Linear(BERT_HIDDEN, 512), nn.LayerNorm(512), nn.GELU(), nn.Dropout(DROPOUT),
                nn.Linear(512, 256), nn.LayerNorm(256), nn.GELU(), nn.Dropout(DROPOUT),
                nn.Linear(256, n_classes))
        def forward(self, input_ids, attention_mask, token_type_ids):
            out = self.bert(input_ids=input_ids, attention_mask=attention_mask,
                            token_type_ids=token_type_ids)
            return self.classifier(out.pooler_output)

    class BertBiLSTM(nn.Module):
        def __init__(self):
            super().__init__()
            self.bert = BertModel.from_pretrained("bert-base-uncased")
            self.bilstm = nn.LSTM(BERT_HIDDEN, 256, num_layers=2,
                                   batch_first=True, bidirectional=True, dropout=0.2)
            self.attn_weight = nn.Linear(512, 1)
            self.drop = nn.Dropout(DROPOUT)
            self.classifier = nn.Linear(512, n_classes)
        def forward(self, input_ids, attention_mask, token_type_ids):
            out = self.bert(input_ids=input_ids, attention_mask=attention_mask,
                            token_type_ids=token_type_ids)
            lstm_out, _ = self.bilstm(out.last_hidden_state)
            attn = self.attn_weight(lstm_out).masked_fill(
                attention_mask.unsqueeze(-1) == 0, -1e9)
            attn = torch.softmax(attn, dim=1)
            context = (attn * lstm_out).sum(dim=1)
            return self.classifier(self.drop(context))

    class BertCNN(nn.Module):
        def __init__(self):
            super().__init__()
            self.bert = BertModel.from_pretrained("bert-base-uncased")
            self.convs = nn.ModuleList([
                nn.Conv1d(BERT_HIDDEN, 128, k, padding=k//2) for k in [2,3,4,5]])
            self.drop = nn.Dropout(DROPOUT)
            self.classifier = nn.Sequential(nn.Linear(512, 256), nn.GELU(),
                                             nn.Dropout(DROPOUT), nn.Linear(256, n_classes))
        def forward(self, input_ids, attention_mask, token_type_ids):
            out = self.bert(input_ids=input_ids, attention_mask=attention_mask,
                            token_type_ids=token_type_ids)
            x = out.last_hidden_state.permute(0, 2, 1)
            pooled = [F.adaptive_max_pool1d(F.gelu(c(x)), 1).squeeze(-1) for c in self.convs]
            return self.classifier(self.drop(torch.cat(pooled, dim=1)))

    class BertTransformer(nn.Module):
        def __init__(self):
            super().__init__()
            self.bert = BertModel.from_pretrained("bert-base-uncased")
            self.encoder = nn.ModuleList([
                TransformerEncoderBlock(BERT_HIDDEN, 8, 1024, 0.1) for _ in range(2)])
            self.ln_final = nn.LayerNorm(BERT_HIDDEN)
            self.drop = nn.Dropout(DROPOUT)
            self.classifier = nn.Sequential(nn.Linear(BERT_HIDDEN, 256), nn.GELU(),
                                             nn.Dropout(DROPOUT), nn.Linear(256, n_classes))
        def forward(self, input_ids, attention_mask, token_type_ids):
            out = self.bert(input_ids=input_ids, attention_mask=attention_mask,
                            token_type_ids=token_type_ids)
            x = out.last_hidden_state
            for layer in self.encoder:
                x = layer(x, attention_mask)
            x = self.ln_final(x)
            mask_exp = attention_mask.unsqueeze(-1).float()
            x = (x * mask_exp).sum(1) / mask_exp.sum(1).clamp(min=1e-9)
            return self.classifier(self.drop(x))

    return {"BertMLP": BertMLP, "BertBiLSTM": BertBiLSTM,
            "BertCNN": BertCNN, "BertTransformer": BertTransformer}


class EmotionDataset(torch.utils.data.Dataset):
    def __init__(self, path):
        data = torch.load(path, weights_only=True)
        self.input_ids      = data["input_ids"]
        self.attention_mask = data["attention_mask"]
        self.token_type_ids = data["token_type_ids"]
        self.labels         = data["labels"]
    def __len__(self): return len(self.labels)
    def __getitem__(self, i):
        return {"input_ids": self.input_ids[i], "attention_mask": self.attention_mask[i],
                "token_type_ids": self.token_type_ids[i], "labels": self.labels[i]}


@torch.no_grad()
def eval_model(model, loader):
    model.eval()
    all_preds, all_labels = [], []
    for batch in loader:
        logits = model(batch["input_ids"].to(DEVICE),
                       batch["attention_mask"].to(DEVICE),
                       batch["token_type_ids"].to(DEVICE))
        all_preds.extend(logits.argmax(1).cpu().numpy())
        all_labels.extend(batch["labels"].numpy())
    return np.array(all_labels), np.array(all_preds)


def print_confusion(cm, classes):
    header = f"{'':>12}" + "".join(f"{c:>12}" for c in classes)
    print(header)
    for i, row in enumerate(cm):
        print(f"{classes[i]:>12}" + "".join(f"{v:>12}" for v in row))


def run():
    print("=" * 65)
    print("  MOOD RECOMMENDER — EVALUATION (BERT + PyTorch)")
    print("=" * 65)

    with open(os.path.join(MODELS_DIR, "model_meta.json")) as f:
        meta = json.load(f)

    le       = joblib.load(os.path.join(MODELS_DIR, "label_encoder.pkl"))
    classes  = meta["classes"]
    n_cls    = meta["n_classes"]
    best_name = meta["best_model"]

    print(f"\n  Best model : {best_name}")
    print(f"  BERT base  : {meta['bert_model']}")
    print(f"  Classes    : {classes}")

    model_map = _register_models(n_cls)
    model     = model_map[best_name]().to(DEVICE)
    model.load_state_dict(
        torch.load(os.path.join(MODELS_DIR, "mood_bert_model.pt"),
                   map_location=DEVICE, weights_only=True)
    )

    summary = {}
    for split in ["val", "test"]:
        path   = os.path.join(MODELS_DIR, f"{split}_tokens.pt")
        loader = DataLoader(EmotionDataset(path), batch_size=32, shuffle=False)
        y, yp  = eval_model(model, loader)
        acc    = accuracy_score(y, yp)
        f1     = f1_score(y, yp, average="weighted")
        summary[split] = {"accuracy": round(acc, 4), "f1_weighted": round(f1, 4)}

        print(f"\n{'─'*45}")
        print(f"  [{split.upper()}]  Accuracy={acc:.4f}   F1={f1:.4f}")
        print(f"{'─'*45}")
        print(classification_report(y, yp, target_names=classes))

        print("Confusion Matrix:")
        print_confusion(confusion_matrix(y, yp), classes)

    # Comparison across all models
    print(f"\n{'═'*45}")
    print("  Model Comparison (Validation F1)")
    print(f"{'─'*45}")
    for name, r in meta.get("all_results", {}).items():
        marker = " ← selected" if name == best_name else ""
        print(f"  {name:<20}  F1={r['val_f1']:.4f}  Epoch={r['best_epoch']}{marker}")
    print(f"{'═'*45}")

    summary["model"] = best_name
    with open(os.path.join(MODELS_DIR, "evaluation_report.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print("\n[OK] Saved → models/evaluation_report.json")
    print("=" * 45)
    return summary


if __name__ == "__main__":
    run()
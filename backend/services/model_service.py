"""
model_service.py — BERT-based mood inference for Flask backend.

Loads: tokenizer, best model architecture + weights, label encoder.
Exposes: predict_mood(text) → dict
"""

import os
import json
import warnings
warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import joblib
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import BertTokenizer, BertModel

from config import Config

DEVICE      = torch.device("cuda" if torch.cuda.is_available() else "cpu")
BERT_HIDDEN = 768
DROPOUT     = 0.3
MAX_LEN     = 128


# ── Model definitions (same as train.py) ─────────────────────────────────────
class MultiHeadSelfAttention(nn.Module):
    def __init__(self, d_model, n_heads=8, dropout=0.1):
        super().__init__()
        self.d_k = d_model // n_heads; self.n_heads = n_heads
        self.W_q = nn.Linear(d_model, d_model); self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model); self.W_o = nn.Linear(d_model, d_model)
        self.drop = nn.Dropout(dropout)
    def forward(self, x, mask=None):
        B, L, D = x.shape
        Q = self.W_q(x).view(B,L,self.n_heads,self.d_k).transpose(1,2)
        K = self.W_k(x).view(B,L,self.n_heads,self.d_k).transpose(1,2)
        V = self.W_v(x).view(B,L,self.n_heads,self.d_k).transpose(1,2)
        sc = (Q @ K.transpose(-2,-1)) / (self.d_k**0.5)
        if mask is not None: sc = sc.masked_fill(mask.unsqueeze(1).unsqueeze(2)==0,-1e9)
        return self.W_o((self.drop(torch.softmax(sc,dim=-1))@V).transpose(1,2).contiguous().view(B,L,D))


class TransformerEncoderBlock(nn.Module):
    def __init__(self, d_model, n_heads, ff_dim, dropout=0.1):
        super().__init__()
        self.self_attn = MultiHeadSelfAttention(d_model, n_heads, dropout)
        self.ff  = nn.Sequential(nn.Linear(d_model,ff_dim),nn.GELU(),nn.Dropout(dropout),nn.Linear(ff_dim,d_model))
        self.ln1 = nn.LayerNorm(d_model); self.ln2 = nn.LayerNorm(d_model)
        self.drop = nn.Dropout(dropout)
    def forward(self, x, mask=None):
        x = x + self.drop(self.self_attn(self.ln1(x), mask))
        x = x + self.drop(self.ff(self.ln2(x)))
        return x


def _build_model(name: str, n_classes: int) -> nn.Module:
    if name == "BertMLP":
        model = nn.Sequential()
        bert  = BertModel.from_pretrained("bert-base-uncased")

        class _M(nn.Module):
            def __init__(self):
                super().__init__()
                self.bert = bert
                self.clf  = nn.Sequential(
                    nn.Linear(BERT_HIDDEN,512),nn.LayerNorm(512),nn.GELU(),nn.Dropout(DROPOUT),
                    nn.Linear(512,256),nn.LayerNorm(256),nn.GELU(),nn.Dropout(DROPOUT),
                    nn.Linear(256,n_classes))
            def forward(self,i,a,t):
                return self.clf(self.bert(i,a,t).pooler_output)
        return _M()

    if name == "BertBiLSTM":
        class _M(nn.Module):
            def __init__(self):
                super().__init__()
                self.bert   = BertModel.from_pretrained("bert-base-uncased")
                self.bilstm = nn.LSTM(BERT_HIDDEN,256,2,batch_first=True,bidirectional=True,dropout=0.2)
                self.attn   = nn.Linear(512,1)
                self.drop   = nn.Dropout(DROPOUT)
                self.clf    = nn.Linear(512,n_classes)
            def forward(self,i,a,t):
                out,_  = self.bilstm(self.bert(i,a,t).last_hidden_state)
                sc     = self.attn(out).masked_fill(a.unsqueeze(-1)==0,-1e9)
                ctx    = (torch.softmax(sc,1)*out).sum(1)
                return self.clf(self.drop(ctx))
        return _M()

    if name == "BertCNN":
        class _M(nn.Module):
            def __init__(self):
                super().__init__()
                self.bert  = BertModel.from_pretrained("bert-base-uncased")
                self.convs = nn.ModuleList([nn.Conv1d(BERT_HIDDEN,128,k,padding=k//2) for k in [2,3,4,5]])
                self.drop  = nn.Dropout(DROPOUT)
                self.clf   = nn.Sequential(nn.Linear(512,256),nn.GELU(),nn.Dropout(DROPOUT),nn.Linear(256,n_classes))
            def forward(self,i,a,t):
                x = self.bert(i,a,t).last_hidden_state.permute(0,2,1)
                p = [F.adaptive_max_pool1d(F.gelu(c(x)),1).squeeze(-1) for c in self.convs]
                return self.clf(self.drop(torch.cat(p,1)))
        return _M()

    if name == "BertTransformer":
        class _M(nn.Module):
            def __init__(self):
                super().__init__()
                self.bert    = BertModel.from_pretrained("bert-base-uncased")
                self.encoder = nn.ModuleList([TransformerEncoderBlock(BERT_HIDDEN,8,1024,0.1) for _ in range(2)])
                self.ln      = nn.LayerNorm(BERT_HIDDEN)
                self.drop    = nn.Dropout(DROPOUT)
                self.clf     = nn.Sequential(nn.Linear(BERT_HIDDEN,256),nn.GELU(),nn.Dropout(DROPOUT),nn.Linear(256,n_classes))
            def forward(self,i,a,t):
                x = self.bert(i,a,t).last_hidden_state
                for l in self.encoder: x = l(x,a)
                x = self.ln(x)
                m = a.unsqueeze(-1).float()
                x = (x*m).sum(1)/m.sum(1).clamp(min=1e-9)
                return self.clf(self.drop(x))
        return _M()

    raise ValueError(f"Unknown model: {name}")


# ── Load artefacts once at startup ────────────────────────────────────────────
print("[ModelService] Loading BERT tokenizer ...")
_tokenizer = BertTokenizer.from_pretrained(
    os.path.join(Config.ML_MODELS_DIR, "tokenizer")
)

print("[ModelService] Loading model metadata ...")
with open(os.path.join(Config.ML_MODELS_DIR, "model_meta.json")) as f:
    _meta = json.load(f)

_le       = joblib.load(os.path.join(Config.ML_MODELS_DIR, "label_encoder.pkl"))
_n_classes = _meta["n_classes"]
_best_name = _meta["best_model"]

print(f"[ModelService] Building {_best_name} ...")
_model = _build_model(_best_name, _n_classes).to(DEVICE)
_model.load_state_dict(
    torch.load(
        os.path.join(Config.ML_MODELS_DIR, "mood_bert_model.pt"),
        map_location=DEVICE, weights_only=True
    )
)
_model.eval()
print(f"[ModelService] Ready — model={_best_name}  classes={_meta['classes']}")


# ── Public inference function ─────────────────────────────────────────────────
def predict_mood(text: str) -> dict:
    """
    Predict emotion from raw text using BERT + Deep Learning.

    Returns:
        {
          "emotion"    : str,    # e.g. "sadness"
          "confidence" : float,  # 0.0 – 1.0
          "all_scores" : dict,   # {emotion: probability}
          "model"      : str,    # architecture name
        }
    """
    enc = _tokenizer(
        text.strip(),
        max_length     = MAX_LEN,
        padding        = "max_length",
        truncation     = True,
        return_tensors = "pt",
    )

    with torch.no_grad():
        logits = _model(
            enc["input_ids"].to(DEVICE),
            enc["attention_mask"].to(DEVICE),
            enc["token_type_ids"].to(DEVICE),
        )
        proba = torch.softmax(logits, dim=1)[0].cpu().numpy()

    label_id   = int(np.argmax(proba))
    emotion    = _le.inverse_transform([label_id])[0]
    confidence = round(float(proba[label_id]), 4)
    all_scores = {cls: round(float(p), 4) for cls, p in zip(_le.classes_, proba)}

    return {
        "emotion"    : emotion,
        "confidence" : confidence,
        "all_scores" : all_scores,
        "model"      : _best_name,
    }
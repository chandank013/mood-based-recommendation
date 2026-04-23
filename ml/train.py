"""
train.py — Advanced Deep Learning Emotion Classifier (PyTorch + BERT)

Four competing architectures built on top of BERT embeddings:

1. BertMLP          — Fine-tuned BERT [CLS] → MLP classifier
2. BertBiLSTM       — Fine-tuned BERT token states → Bidirectional LSTM
3. BertCNN          — Fine-tuned BERT token states → Multi-scale 1D CNN
4. BertTransformer  — Fine-tuned BERT + custom Transformer encoder head
                       (cross-attention over BERT hidden states)

All share:
  - BERT (bert-base-uncased) as frozen/unfrozen encoder
  - AdamW optimiser with linear warmup + cosine decay schedule
  - Label smoothing cross-entropy loss
  - Gradient clipping
  - Early stopping on validation F1
"""

import os
import json
import joblib
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from transformers import BertModel, get_linear_schedule_with_warmup
from sklearn.metrics import f1_score, classification_report
from torch.optim import AdamW

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")

# ── Config ────────────────────────────────────────────────────────────────────
BERT_MODEL   = "bert-base-uncased"
BERT_HIDDEN  = 768       # BERT-base hidden size
MAX_LEN      = 128
BATCH_SIZE   = 16
MAX_EPOCHS   = 10
PATIENCE     = 3         # Early stopping patience
LR           = 2e-5      # Learning rate (BERT fine-tuning best practice)
WARMUP_RATIO = 0.1       # 10% of steps for warmup
CLIP_GRAD    = 1.0       # Gradient clipping norm
LABEL_SMOOTH = 0.1       # Label smoothing epsilon
DROPOUT      = 0.3

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ── Dataset ───────────────────────────────────────────────────────────────────
class EmotionDataset(Dataset):
    def __init__(self, tokens_path: str):
        data = torch.load(tokens_path, weights_only=True)
        self.input_ids      = data["input_ids"]
        self.attention_mask = data["attention_mask"]
        self.token_type_ids = data["token_type_ids"]
        self.labels         = data["labels"]

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return {
            "input_ids"      : self.input_ids[idx],
            "attention_mask" : self.attention_mask[idx],
            "token_type_ids" : self.token_type_ids[idx],
            "labels"         : self.labels[idx],
        }


def make_loader(path: str, shuffle: bool = False) -> DataLoader:
    return DataLoader(
        EmotionDataset(path),
        batch_size  = BATCH_SIZE,
        shuffle     = shuffle,
        num_workers = 0,
        pin_memory  = DEVICE.type == "cuda",
    )


# ── Label Smoothing Loss ──────────────────────────────────────────────────────
class LabelSmoothingCrossEntropy(nn.Module):
    def __init__(self, classes: int, smoothing: float = LABEL_SMOOTH):
        super().__init__()
        self.smoothing = smoothing
        self.cls       = classes

    def forward(self, pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        confidence = 1.0 - self.smoothing
        smooth_val = self.smoothing / (self.cls - 1)
        one_hot    = torch.full_like(pred, smooth_val)
        one_hot.scatter_(1, target.unsqueeze(1), confidence)
        log_prob   = F.log_softmax(pred, dim=1)
        return -(one_hot * log_prob).sum(dim=1).mean()


# ── 1. BERT + MLP ─────────────────────────────────────────────────────────────
class BertMLP(nn.Module):
    """
    Fine-tune BERT, take [CLS] token, pass through 3-layer MLP.
    Simplest but very strong baseline.
    """
    def __init__(self, n_classes: int, freeze_bert: bool = False):
        super().__init__()
        self.bert = BertModel.from_pretrained(BERT_MODEL)
        if freeze_bert:
            for p in self.bert.parameters():
                p.requires_grad = False

        self.classifier = nn.Sequential(
            nn.Linear(BERT_HIDDEN, 512),
            nn.LayerNorm(512),
            nn.GELU(),
            nn.Dropout(DROPOUT),
            nn.Linear(512, 256),
            nn.LayerNorm(256),
            nn.GELU(),
            nn.Dropout(DROPOUT),
            nn.Linear(256, n_classes),
        )

    def forward(self, input_ids, attention_mask, token_type_ids):
        out = self.bert(
            input_ids       = input_ids,
            attention_mask  = attention_mask,
            token_type_ids  = token_type_ids,
        )
        cls_out = out.pooler_output            # [B, 768]
        return self.classifier(cls_out)


# ── 2. BERT + Bidirectional LSTM ──────────────────────────────────────────────
class BertBiLSTM(nn.Module):
    """
    BERT token hidden states → Bidirectional LSTM → attention pooling.
    Captures sequential dependencies in emotion-laden text.
    """
    def __init__(self, n_classes: int, hidden_size: int = 256):
        super().__init__()
        self.bert = BertModel.from_pretrained(BERT_MODEL)

        self.bilstm = nn.LSTM(
            input_size  = BERT_HIDDEN,
            hidden_size = hidden_size,
            num_layers  = 2,
            batch_first = True,
            bidirectional = True,
            dropout     = 0.2,
        )
        self.attn_weight = nn.Linear(hidden_size * 2, 1)
        self.drop        = nn.Dropout(DROPOUT)
        self.classifier  = nn.Linear(hidden_size * 2, n_classes)

    def forward(self, input_ids, attention_mask, token_type_ids):
        bert_out = self.bert(
            input_ids      = input_ids,
            attention_mask = attention_mask,
            token_type_ids = token_type_ids,
        )
        seq_out = bert_out.last_hidden_state          # [B, L, 768]
        lstm_out, _ = self.bilstm(seq_out)            # [B, L, 512]

        # Attention pooling — weighted sum over tokens
        attn_scores = self.attn_weight(lstm_out)      # [B, L, 1]
        attn_scores = attn_scores.masked_fill(
            attention_mask.unsqueeze(-1) == 0, -1e9
        )
        attn_weights = torch.softmax(attn_scores, dim=1)  # [B, L, 1]
        context      = (attn_weights * lstm_out).sum(dim=1)  # [B, 512]
        return self.classifier(self.drop(context))


# ── 3. BERT + Multi-Scale CNN ─────────────────────────────────────────────────
class BertCNN(nn.Module):
    """
    BERT hidden states → Parallel CNN branches (kernel 2,3,4,5) → 
    Global max pool + concat → classifier.
    Captures n-gram emotion patterns at multiple scales.
    """
    def __init__(self, n_classes: int, num_filters: int = 128):
        super().__init__()
        self.bert = BertModel.from_pretrained(BERT_MODEL)

        self.convs = nn.ModuleList([
            nn.Conv1d(
                in_channels  = BERT_HIDDEN,
                out_channels = num_filters,
                kernel_size  = k,
                padding      = k // 2,
            )
            for k in [2, 3, 4, 5]
        ])
        self.drop       = nn.Dropout(DROPOUT)
        self.classifier = nn.Sequential(
            nn.Linear(num_filters * 4, 256),
            nn.GELU(),
            nn.Dropout(DROPOUT),
            nn.Linear(256, n_classes),
        )

    def forward(self, input_ids, attention_mask, token_type_ids):
        bert_out = self.bert(
            input_ids      = input_ids,
            attention_mask = attention_mask,
            token_type_ids = token_type_ids,
        )
        seq_out = bert_out.last_hidden_state          # [B, L, 768]
        x       = seq_out.permute(0, 2, 1)            # [B, 768, L]

        pooled = []
        for conv in self.convs:
            c = F.gelu(conv(x))                       # [B, F, L]
            c = F.adaptive_max_pool1d(c, 1).squeeze(-1)  # [B, F]
            pooled.append(c)

        out = torch.cat(pooled, dim=1)                 # [B, F*4]
        return self.classifier(self.drop(out))


# ── 4. BERT + Custom Transformer Encoder Head ─────────────────────────────────
class MultiHeadSelfAttention(nn.Module):
    """Scaled dot-product multi-head self-attention."""
    def __init__(self, d_model: int, n_heads: int = 8, dropout: float = 0.1):
        super().__init__()
        assert d_model % n_heads == 0
        self.d_k    = d_model // n_heads
        self.n_heads = n_heads
        self.W_q    = nn.Linear(d_model, d_model)
        self.W_k    = nn.Linear(d_model, d_model)
        self.W_v    = nn.Linear(d_model, d_model)
        self.W_o    = nn.Linear(d_model, d_model)
        self.drop   = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, mask: torch.Tensor = None):
        B, L, D = x.shape
        Q = self.W_q(x).view(B, L, self.n_heads, self.d_k).transpose(1, 2)
        K = self.W_k(x).view(B, L, self.n_heads, self.d_k).transpose(1, 2)
        V = self.W_v(x).view(B, L, self.n_heads, self.d_k).transpose(1, 2)

        scores = (Q @ K.transpose(-2, -1)) / (self.d_k ** 0.5)  # [B, H, L, L]
        if mask is not None:
            scores = scores.masked_fill(mask.unsqueeze(1).unsqueeze(2) == 0, -1e9)
        attn   = self.drop(torch.softmax(scores, dim=-1))
        out    = (attn @ V).transpose(1, 2).contiguous().view(B, L, D)
        return self.W_o(out)


class TransformerEncoderBlock(nn.Module):
    """Pre-LN Transformer block (more stable training)."""
    def __init__(self, d_model: int, n_heads: int, ff_dim: int, dropout: float = 0.1):
        super().__init__()
        self.self_attn = MultiHeadSelfAttention(d_model, n_heads, dropout)
        self.ff        = nn.Sequential(
            nn.Linear(d_model, ff_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(ff_dim, d_model),
        )
        self.ln1  = nn.LayerNorm(d_model)
        self.ln2  = nn.LayerNorm(d_model)
        self.drop = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, mask: torch.Tensor = None):
        # Pre-LN: normalise before sublayer (more stable than post-LN)
        x = x + self.drop(self.self_attn(self.ln1(x), mask))
        x = x + self.drop(self.ff(self.ln2(x)))
        return x


class BertTransformer(nn.Module):
    """
    BERT hidden states → 2-layer custom Transformer encoder →
    mean pooling → classifier.
    The custom Transformer refines BERT representations for emotion.
    """
    def __init__(self, n_classes: int, n_heads: int = 8,
                 n_layers: int = 2, ff_dim: int = 1024):
        super().__init__()
        self.bert = BertModel.from_pretrained(BERT_MODEL)

        self.encoder = nn.ModuleList([
            TransformerEncoderBlock(BERT_HIDDEN, n_heads, ff_dim, dropout=0.1)
            for _ in range(n_layers)
        ])
        self.ln_final   = nn.LayerNorm(BERT_HIDDEN)
        self.drop       = nn.Dropout(DROPOUT)
        self.classifier = nn.Sequential(
            nn.Linear(BERT_HIDDEN, 256),
            nn.GELU(),
            nn.Dropout(DROPOUT),
            nn.Linear(256, n_classes),
        )

    def forward(self, input_ids, attention_mask, token_type_ids):
        bert_out = self.bert(
            input_ids      = input_ids,
            attention_mask = attention_mask,
            token_type_ids = token_type_ids,
        )
        x = bert_out.last_hidden_state              # [B, L, 768]

        for layer in self.encoder:
            x = layer(x, attention_mask)

        x = self.ln_final(x)

        # Masked mean pooling — ignore [PAD] tokens
        mask_exp = attention_mask.unsqueeze(-1).float()
        x = (x * mask_exp).sum(dim=1) / mask_exp.sum(dim=1).clamp(min=1e-9)  # [B, 768]

        return self.classifier(self.drop(x))


# ── Training loop ─────────────────────────────────────────────────────────────
def train_epoch(model, loader, optimizer, scheduler, criterion) -> float:
    model.train()
    total_loss = 0.0
    for batch in loader:
        input_ids      = batch["input_ids"].to(DEVICE)
        attention_mask = batch["attention_mask"].to(DEVICE)
        token_type_ids = batch["token_type_ids"].to(DEVICE)
        labels         = batch["labels"].to(DEVICE)

        optimizer.zero_grad()
        logits = model(input_ids, attention_mask, token_type_ids)
        loss   = criterion(logits, labels)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), CLIP_GRAD)
        optimizer.step()
        scheduler.step()
        total_loss += loss.item()
    return total_loss / len(loader)


@torch.no_grad()
def evaluate(model, loader) -> tuple[float, float, np.ndarray]:
    model.eval()
    all_preds, all_labels = [], []
    for batch in loader:
        input_ids      = batch["input_ids"].to(DEVICE)
        attention_mask = batch["attention_mask"].to(DEVICE)
        token_type_ids = batch["token_type_ids"].to(DEVICE)
        labels         = batch["labels"]

        logits = model(input_ids, attention_mask, token_type_ids)
        preds  = logits.argmax(dim=1).cpu().numpy()
        all_preds.extend(preds)
        all_labels.extend(labels.numpy())

    all_preds  = np.array(all_preds)
    all_labels = np.array(all_labels)
    acc = float(np.mean(all_preds == all_labels))
    f1  = float(f1_score(all_labels, all_preds, average="weighted"))
    return acc, f1, all_preds


def train_model(model, train_loader, val_loader, model_name: str,
                n_classes: int) -> dict:
    """Full training loop with early stopping."""
    criterion = LabelSmoothingCrossEntropy(n_classes)
    optimizer = AdamW(
        model.parameters(),
        lr           = LR,
        weight_decay = 0.01,
        eps          = 1e-8,
    )

    total_steps  = len(train_loader) * MAX_EPOCHS
    warmup_steps = int(total_steps * WARMUP_RATIO)
    scheduler    = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps   = warmup_steps,
        num_training_steps = total_steps,
    )

    best_f1, best_epoch, patience_cnt = 0.0, 0, 0
    history = []

    print(f"\n  ┌─── Training {model_name} ───")
    print(f"  │  Device: {DEVICE} | Params: {sum(p.numel() for p in model.parameters()):,}")

    for epoch in range(1, MAX_EPOCHS + 1):
        train_loss          = train_epoch(model, train_loader, optimizer, scheduler, criterion)
        val_acc, val_f1, _  = evaluate(model, val_loader)
        history.append({"epoch": epoch, "loss": train_loss, "val_acc": val_acc, "val_f1": val_f1})

        improved = "✓" if val_f1 > best_f1 else " "
        print(f"  │  Epoch {epoch:>2} [{improved}]  loss={train_loss:.4f}  val_acc={val_acc:.4f}  val_f1={val_f1:.4f}")

        if val_f1 > best_f1:
            best_f1    = val_f1
            best_epoch = epoch
            patience_cnt = 0
            # Save best checkpoint
            torch.save(model.state_dict(),
                       os.path.join(MODELS_DIR, f"{model_name}_best.pt"))
        else:
            patience_cnt += 1
            if patience_cnt >= PATIENCE:
                print(f"  │  Early stopping at epoch {epoch}")
                break

    print(f"  └─── Best F1={best_f1:.4f} at epoch {best_epoch}")
    return {"best_f1": best_f1, "best_epoch": best_epoch, "history": history}


# ── Main ──────────────────────────────────────────────────────────────────────
def run():
    print("=" * 45)
    print("  MOOD RECOMMENDER — ADVANCED DL TRAINING (BERT + PyTorch)")
    print("=" * 45)
    print(f"\n  Device  : {DEVICE}")
    print(f"  BERT    : {BERT_MODEL}")
    print(f"  Batch   : {BATCH_SIZE}  LR: {LR}  MaxEpochs: {MAX_EPOCHS}")

    with open(os.path.join(MODELS_DIR, "config.json")) as f:
        cfg = json.load(f)
    n_classes = cfg["n_classes"]
    classes   = cfg["classes"]

    le = joblib.load(os.path.join(MODELS_DIR, "label_encoder.pkl"))

    train_loader = make_loader(os.path.join(MODELS_DIR, "train_tokens.pt"), shuffle=True)
    val_loader   = make_loader(os.path.join(MODELS_DIR, "val_tokens.pt"),   shuffle=False)
    test_loader  = make_loader(os.path.join(MODELS_DIR, "test_tokens.pt"),  shuffle=False)

    # ── Candidate architectures ───────────────────────────────────────────────
    candidates = {
        "BertMLP"        : BertMLP(n_classes).to(DEVICE),
        "BertBiLSTM"     : BertBiLSTM(n_classes).to(DEVICE),
        "BertCNN"        : BertCNN(n_classes).to(DEVICE),
        "BertTransformer": BertTransformer(n_classes).to(DEVICE),
    }

    results = {}
    print(f"\n{'─'*65}")

    for name, model in candidates.items():
        result = train_model(model, train_loader, val_loader, name, n_classes)
        results[name] = result

    # ── Select best model ─────────────────────────────────────────────────────
    best_name = max(results, key=lambda k: results[k]["best_f1"])
    print(f"\n{'═'*65}")
    print(f"  CV Summary:")
    print(f"{'─'*65}")
    for name, r in results.items():
        marker = " ← best" if name == best_name else ""
        print(f"  {name:<20}  Val F1={r['best_f1']:.4f}  "
              f"Best Epoch={r['best_epoch']}{marker}")

    # ── Load best checkpoint and test ────────────────────────────────────────
    best_model = candidates[best_name]
    best_model.load_state_dict(
        torch.load(os.path.join(MODELS_DIR, f"{best_name}_best.pt"),
                   map_location=DEVICE, weights_only=True)
    )

    test_acc, test_f1, test_preds = evaluate(best_model, test_loader)
    print(f"\n  Test set:  Accuracy={test_acc:.4f}  F1={test_f1:.4f}")

    # Full classification report
    test_data  = torch.load(os.path.join(MODELS_DIR, "test_tokens.pt"), weights_only=True)
    test_labels = test_data["labels"].numpy()
    print(f"\n{classification_report(test_labels, test_preds, target_names=classes)}")

    # ── Sanity check ─────────────────────────────────────────────────────────
    from transformers import BertTokenizer
    tokenizer = BertTokenizer.from_pretrained(os.path.join(MODELS_DIR, "tokenizer"))

    def predict(text: str) -> str:
        enc = tokenizer(text, max_length=MAX_LEN, padding="max_length",
                        truncation=True, return_tensors="pt")
        best_model.eval()
        with torch.no_grad():
            logits = best_model(
                enc["input_ids"].to(DEVICE),
                enc["attention_mask"].to(DEVICE),
                enc["token_type_ids"].to(DEVICE),
            )
        return le.inverse_transform([logits.argmax().item()])[0]

    samples = [
        "i feel absolutely wonderful and joyful today",
        "i am so angry and frustrated with everything",
        "i feel terrified and cannot stop shaking",
        "everything feels hopeless and dark",
        "i am deeply in love and grateful",
        "i was completely shocked by what happened",
    ]
    print("\n  [Sanity check]")
    for s in samples:
        print(f"  [{predict(s):>9}]  {s}")

    # ── Save final model + meta ───────────────────────────────────────────────
    torch.save(best_model.state_dict(),
               os.path.join(MODELS_DIR, "mood_bert_model.pt"))

    meta = {
        "best_model"  : best_name,
        "bert_model"  : BERT_MODEL,
        "max_len"     : MAX_LEN,
        "n_classes"   : n_classes,
        "classes"     : classes,
        "test_acc"    : round(test_acc, 4),
        "test_f1"     : round(test_f1, 4),
        "all_results" : {k: {"val_f1": round(v["best_f1"],4),
                             "best_epoch": v["best_epoch"]}
                         for k, v in results.items()},
    }
    with open(os.path.join(MODELS_DIR, "model_meta.json"), "w") as f:
        json.dump(meta, f, indent=2)

    print(f"\n[OK] Saved → models/mood_bert_model.pt")
    print(f"[OK] Saved → models/model_meta.json")
    print("=" * 45)
    return best_model, le, tokenizer, best_name


if __name__ == "__main__":
    run()
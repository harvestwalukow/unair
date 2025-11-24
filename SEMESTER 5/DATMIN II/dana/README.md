## ABSA pada Review Aplikasi DANA dengan IndoBERT-Lite

Repositori ini berisi satu notebook `absa_dana_experiment.ipynb` yang mereplikasi alur eksperimen paper **“Utilizing Sentiment Insights for Software Evaluation with Aspect-Based Sentiment Analysis in App Reviews Using IndoBERT-Lite”** menggunakan dataset **review aplikasi DANA** (`dana_app_reviews_downloaded.csv`).

Notebook dirancang **end-to-end**: mulai dari pemuatan data, pelabelan aspek & sentimen, preprocessing IndoBERT, split data, training multi-task classifier, hingga evaluasi dan visualisasi.

---

## 1. Dataset

- **Sumber**: file `dana_app_reviews_downloaded.csv`
- **Kolom utama**:
  - `userName` – nama pengguna
  - `score` – rating (1–5)
  - `at` – timestamp review
  - `content` – teks review (Bahasa Indonesia)
  - `sentimen` – label sentimen awal (kategori: `POSITIVE`, `NEGATIVE`, `NEUTRAL`)

Kolom teks review dideteksi otomatis sebagai:

```python
TEXT_COLUMN = "content"
```

Baris dengan teks kosong atau `NaN` dihapus sebelum diproses lebih lanjut.

---

## 2. Skema Label

### 2.1. Label Aspek

Mengikuti paper, digunakan 5 aspek:

- `design`
- `functionality`
- `performance`
- `service`
- `usability`

Karena dataset tidak memiliki kolom aspek eksplisit, aspek dihasilkan dengan **rule-based heuristics** pada teks review:

```python
ASPECT_LABELS = ["design", "functionality", "performance", "service", "usability"]

def rule_based_aspect(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ["tampilan", "desain", "design", "ui", "ux", "warna"]):
        return "design"
    if any(k in t for k in ["fitur", "fungsi", "function", "menu", "top up", "transfer", "bayar"]):
        return "functionality"
    if any(k in t for k in ["lemot", "lambat", "hang", "error", "bug", "force close", "crash", "loading"]):
        return "performance"
    if any(k in t for k in ["cs", "customer service", "layanan", "help center", "respon", "pelayanan"]):
        return "service"
    if any(k in t for k in ["mudah", "simple", "gampang", "ribet", "susah", "user friendly"]):
        return "usability"
    # fallback
    return "usability"
```

### 2.2. Label Sentimen

Sentimen diambil langsung dari kolom `sentimen` di CSV, kemudian dinormalisasi ke tiga kelas:

```python
SENTIMENT_LABELS = ["positive", "neutral", "negative"]

df["sentiment"] = (
    df["sentimen"]
    .astype(str)
    .str.upper()
    .map({
        "POSITIVE": "positive",
        "NEGATIVE": "negative",
        "NEUTRAL":  "neutral",
    })
)
```

> **Catatan penting validitas**  
> Percobaan awal menggunakan model BERT dasar untuk melabeli sentimen secara otomatis menyebabkan **semua review terklasifikasi sebagai `neutral`**, sehingga metrik sentimen menjadi tidak bermakna (F1 = 1.0 hanya karena tidak ada variasi kelas).  
> Bagian tersebut _tidak_ digunakan dalam analisis akhir; hasil yang dianalisis menggunakan label `sentimen` asli dari dataset.

---

## 3. Handling Imbalance

Distribusi awal aspek dan sentimen sangat tidak seimbang, misalnya:

- `usability` jauh lebih dominan daripada aspek lain
- sentimen juga tidak merata

Untuk mengurangi bias dan mempercepat training, dilakukan **undersampling per pasangan (aspect, sentiment)**:

```python
# Gabungkan aspek dan sentimen
df["pair_label"] = df["aspect"] + "__" + df["sentiment"]

print("Distribusi awal pair_label:")
print(df["pair_label"].value_counts().head(20))

MAX_SAMPLES_PER_PAIR = 2000  # maksimal sampel per pasangan (aspect, sentiment)

balanced_parts = []
for pair, count in df["pair_label"].value_counts().items():
    subset = df[df["pair_label"] == pair]
    if count > MAX_SAMPLES_PER_PAIR:
        subset = subset.sample(MAX_SAMPLES_PER_PAIR, random_state=SEED)
    balanced_parts.append(subset)

df_balanced = pd.concat(balanced_parts).sample(frac=1, random_state=SEED).reset_index(drop=True)
df = df_balanced.drop(columns=["pair_label"])

print("\nDistribusi aspek setelah balancing:")
print(df["aspect"].value_counts())
print("\nDistribusi sentimen setelah balancing:")
print(df["sentiment"].value_counts())
```

Setelah balancing, dataset menjadi jauh lebih seimbang antar kombinasi aspek–sentimen, dan ukuran total data berkurang sehingga training lebih cepat dan risiko overfit menurun.

---

## 4. Split Data & Encoding Label

Label teks dikonversi menjadi ID numerik:

```python
aspect2id = {a: i for i, a in enumerate(ASPECT_LABELS)}
id2aspect = {i: a for a, i in aspect2id.items()}

sentiment2id = {s: i for i, s in enumerate(SENTIMENT_LABELS)}
id2sentiment = {i: s for s, i in sentiment2id.items()}

df["aspect_id"] = df["aspect"].map(aspect2id)
df["sentiment_id"] = df["sentiment"].map(sentiment2id)

df["pair_label"] = df["aspect_id"].astype(str) + "_" + df["sentiment_id"].astype(str)
```

Data kemudian di-split menjadi **70% train, 20% validation, 10% test** dengan stratifikasi pada kombinasi aspek–sentimen:

```python
from sklearn.model_selection import train_test_split

train_df, temp_df = train_test_split(
    df,
    test_size=0.3,
    random_state=SEED,
    stratify=df["pair_label"],
)

val_df, test_df = train_test_split(
    temp_df,
    test_size=1/3,  # 1/3 dari 30% = 10% total
    random_state=SEED,
    stratify=temp_df["pair_label"],
)

print("Train:", train_df.shape, "Val:", val_df.shape, "Test:", test_df.shape)
```

---

## 5. Preprocessing & Tokenisasi IndoBERT

Model dasar yang digunakan adalah **IndoBERT** dari HuggingFace:

```python
PRETRAINED_MODEL_NAME = "indobenchmark/indobert-base-p1"
MAX_LEN = 128
```

Tokenizer:

```python
from transformers import BertTokenizerFast

tokenizer = BertTokenizerFast.from_pretrained(PRETRAINED_MODEL_NAME)
```

Dataset PyTorch dengan tokenisasi:

```python
class ABSADataset(Dataset):
    def __init__(self, df, text_col, max_len):
        self.texts = df[text_col].astype(str).tolist()
        self.aspect_ids = df["aspect_id"].astype(int).tolist()
        self.sentiment_ids = df["sentiment_id"].astype(int).tolist()
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        encoding = tokenizer(
            text,
            padding="max_length",
            truncation=True,
            max_length=self.max_len,
            return_tensors="pt",
        )
        return {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "aspect_label": torch.tensor(self.aspect_ids[idx], dtype=torch.long),
            "sentiment_label": torch.tensor(self.sentiment_ids[idx], dtype=torch.long),
        }
```

---

## 6. Arsitektur Model: IndoBERT Multi-Task

Model direalisasikan sebagai **multi-task classifier**: satu backbone IndoBERT dengan dua output head (aspek & sentimen).

```python
from transformers import AutoConfig, AutoModel

class IndoBertABSA(nn.Module):
    def __init__(self, pretrained_name, num_aspect_labels, num_sentiment_labels, dropout=0.1):
        super().__init__()
        self.config = AutoConfig.from_pretrained(pretrained_name)
        self.bert = AutoModel.from_pretrained(pretrained_name, config=self.config)
        hidden_size = self.config.hidden_size
        self.dropout = nn.Dropout(dropout)
        self.aspect_classifier = nn.Linear(hidden_size, num_aspect_labels)
        self.sentiment_classifier = nn.Linear(hidden_size, num_sentiment_labels)

    def forward(self, input_ids, attention_mask, labels_aspect=None, labels_sentiment=None):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        # Gunakan representasi [CLS]
        pooled = outputs.last_hidden_state[:, 0]
        pooled = self.dropout(pooled)

        logits_aspect = self.aspect_classifier(pooled)
        logits_sentiment = self.sentiment_classifier(pooled)

        loss = None
        if labels_aspect is not None and labels_sentiment is not None:
            loss_fct = nn.CrossEntropyLoss()
            loss_aspect = loss_fct(logits_aspect, labels_aspect)
            loss_sentiment = loss_fct(logits_sentiment, labels_sentiment)
            loss = loss_aspect + loss_sentiment

        return {
            "loss": loss,
            "logits_aspect": logits_aspect,
            "logits_sentiment": logits_sentiment,
        }
```

---

## 7. Setup Eksperimen

Parameter utama:

```python
NUM_EPOCHS = 1
BATCH_SIZES = [16, 32, 64]
LR = 2e-5
```

Untuk setiap batch size:

1. Buat `DataLoader` train/val/test.
2. Inisialisasi model baru.
3. Training 1 epoch dengan scheduler linear warmup.
4. Pilih model terbaik berdasarkan F1 sentimen pada validation (secara teori; dalam praktik, fokus analisis pada aspek).
5. Evaluasi di test set.

Bagian inti loop training:

```python
for bs in BATCH_SIZES:
    train_loader, val_loader, test_loader = create_dataloaders(bs)
    model = IndoBertABSA(
        pretrained_name=PRETRAINED_MODEL_NAME,
        num_aspect_labels=len(ASPECT_LABELS),
        num_sentiment_labels=len(SENTIMENT_LABELS),
    ).to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)
    total_steps = len(train_loader) * NUM_EPOCHS
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=int(0.1 * total_steps),
        num_training_steps=total_steps,
    )

    best_val_f1 = 0.0
    history_train_loss = []
    history_val_loss = []
    start_time = time.time()

    for epoch in range(1, NUM_EPOCHS + 1):
        model.train()
        running_loss = 0.0
        for step, batch in enumerate(train_loader, start=1):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            aspect_labels = batch["aspect_label"].to(device)
            sentiment_labels = batch["sentiment_label"].to(device)

            optimizer.zero_grad()
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels_aspect=aspect_labels,
                labels_sentiment=sentiment_labels,
            )

            loss = outputs["loss"]
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            scheduler.step()

            running_loss += loss.item()
            if step % 100 == 0 or step == len(train_loader):
                print(f"  Step {step}/{len(train_loader)} - loss {loss.item():.4f}")

        avg_train_loss = running_loss / max(1, len(train_loader))
        # ... validasi & evaluasi ...
```

---

## 8. Evaluasi & Hasil

### 8.1. Metrik

Untuk aspek dan sentimen digunakan:

- **Accuracy**
- **Precision (weighted)**
- **Recall (weighted)**
- **F1-score (weighted)**
- **Classification report** per kelas

Fungsi metrik:

```python
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report

def compute_metrics(y_true, y_pred, label_names):
    acc = accuracy_score(y_true, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="weighted", zero_division=0
    )
    labels = list(range(len(label_names)))
    report = classification_report(
        y_true,
        y_pred,
        labels=labels,
        target_names=label_names,
        zero_division=0,
    )
    return {
        "accuracy": acc,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "report": report,
    }
```

### 8.2. Hasil Utama (Aspek)

Pada eksperimen dengan **1 epoch**:

- **Batch size 16**

  - Akurasi aspek test ≈ **0.91**
  - Aspek dengan F1 tertinggi: `functionality`, `performance`, `service`, `usability` (≈ 0.9+)
  - Aspek dengan F1 terendah: `design` (sekitar 0.7) – konsisten dengan jumlah data paling sedikit dan kata kunci yang lebih halus.

- **Batch size 32**

  - Akurasi aspek test ≈ **0.85**
  - Sedikit penurunan dibanding bs=16; pola per aspek tetap sama (design terendah).

- **Batch size 64**
  - Akurasi aspek test ≈ **0.81**
  - Penurunan lebih jauh; menunjukkan batch size yang terlalu besar tidak selalu menguntungkan pada dataset ini.

Secara umum:

- **Model aspek sudah cukup kuat**, terutama untuk aspek mayoritas.
- **Batch size 16** memberikan performa terbaik pada eksperimen ini.

### 8.3. Hasil Sentimen

Karena adanya masalah pada percobaan awal (semua label sentimen otomatis berubah menjadi `neutral`), analisis metrik sentimen **tidak dilaporkan sebagai hasil utama** dalam README ini.

Untuk analisis sentimen yang valid, direkomendasikan untuk:

- Menggunakan kolom `sentimen` asli sebagai ground truth, **tanpa** di-overwrite oleh model lain, dan
- Menjalankan kembali pipeline training & evaluasi.

---

## 9. Visualisasi

Notebook menghasilkan beberapa visual:

- **Kurva training vs validation loss** untuk setiap batch size.
- **Confusion matrix** untuk prediksi aspek dan sentimen.
- **Stacked bar chart** distribusi prediksi sentimen per aspek.

Contoh plotting loss:

```python
plt.figure(figsize=(10, 6))
for bs in BATCH_SIZES:
    if bs in train_histories:
        plt.plot(train_histories[bs], label=f"Train (bs={bs})")
        plt.plot(val_histories[bs], linestyle="--", label=f"Val (bs={bs})")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.title("Training vs Validation Loss untuk Berbagai Batch Size")
plt.legend()
plt.grid(True)
plt.show()
```

---

## 10. Keterbatasan & Diskusi

- **Label aspek** dihasilkan secara **rule-based**, bukan anotasi manual; sehingga hasil mencerminkan seberapa baik model mempelajari pola yang dikodekan heuristik, bukan “kebenaran absolut”.
- Imbalance awal yang besar antara aspek membuat perlu dilakukan **undersampling**, sehingga distribusi data tidak lagi mencerminkan distribusi asli di store.
- Percobaan otomatis untuk melabeli sentimen dengan model BERT dasar menghasilkan label semua `neutral`; hal ini diidentifikasi dan tidak digunakan dalam analisis akhir.
- Hanya dilakukan **1 epoch** per konfigurasi batch size pada eksperimen terakhir untuk menyeimbangkan waktu komputasi dan kebutuhan eksplorasi.

Meskipun demikian, eksperimen ini menunjukkan bahwa:

- IndoBERT (IndoBERT-Lite/BERT-base Indonesia) cukup efektif sebagai backbone untuk **Aspect-Based Sentiment Analysis** pada review aplikasi DANA.
- Performa aspek yang tinggi pada aspek mayoritas menunjukkan potensi pendekatan multi-task ABSA untuk evaluasi kualitas perangkat lunak berbasis ulasan pengguna.

---

## 11. Cara Menjalankan Notebook

1. Pastikan file `dana_app_reviews_downloaded.csv` berada di direktori kerja yang sama dengan notebook.
2. Buka `absa_dana_experiment.ipynb` di Jupyter / VS Code / Google Colab.
3. Jalankan sel pertama untuk memuat library dan mengatur konfigurasi:
   - Periksa `DATA_PATH`, `TEXT_COLUMN`, `PRETRAINED_MODEL_NAME`, `NUM_EPOCHS`, `BATCH_SIZES`.
4. Jalankan seluruh sel **berurutan dari atas ke bawah**:
   - Load data → labeling aspek & sentimen → handling imbalance → split → dataset/dataloader → model → training loop → evaluasi → visualisasi.

Jika ingin eksperimen cepat:

```python
NUM_EPOCHS = 1
BATCH_SIZES = [16]
MAX_LEN = 64
```

Kemudian jalankan ulang notebook dari awal.


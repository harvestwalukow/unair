from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable
from zlib import crc32

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.metrics import roc_auc_score
from sklearn.naive_bayes import MultinomialNB


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "Beauty_and_Personal_Care.jsonl"
OUTPUT_DIR = BASE_DIR / "outputs"
FIG_DIR = OUTPUT_DIR / "figures"
TABLE_DIR = OUTPUT_DIR / "tables"
TEXT_DIR = OUTPUT_DIR / "text"

DATASET_URL = "https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023"
DATASET_DOC_URL = "https://amazon-reviews-2023.github.io/main.html"
PAPER_URL = "https://arxiv.org/abs/2403.03952"

THEME_KEYWORDS = {
    "Product does not work as expected": [
        "doesn t work",
        "didn t work",
        "not work",
        "stopped working",
        "waste of money",
        "ineffective",
        "no difference",
        "does nothing",
        "worthless",
        "poor quality",
    ],
    "Packaging, leakage, or damaged items": [
        "leak",
        "leaking",
        "spilled",
        "broken",
        "damaged",
        "seal",
        "packaging",
        "pump",
        "cap",
        "opened",
        "arrived open",
    ],
    "Skin irritation or side effects": [
        "itch",
        "itchy",
        "burn",
        "burning",
        "rash",
        "irritat",
        "allergic",
        "reaction",
        "redness",
        "broke me out",
        "break out",
        "swollen",
    ],
    "Authenticity or mismatch concerns": [
        "fake",
        "counterfeit",
        "changed formula",
        "not the same",
        "wrong item",
        "expired",
        "old product",
    ],
    "Bad smell or overly strong fragrance": [
        "bad smell",
        "terrible smell",
        "awful smell",
        "strong smell",
        "chemical smell",
        "smells bad",
        "stinks",
        "stinky",
        "too strong",
        "overpowering",
        "gasoline",
    ],
}

STOPWORDS = {
    "the", "and", "for", "that", "with", "this", "was", "but", "have", "are",
    "not", "you", "had", "they", "all", "its", "too", "very", "out", "use",
    "used", "after", "from", "just", "like", "will", "one", "your", "them",
    "there", "their", "about", "into", "been", "would", "could", "should",
    "because", "when", "where", "what", "which", "while", "then", "than",
    "also", "only", "were", "being", "over", "under", "again", "more", "most",
    "some", "such", "much", "many", "each", "other", "these", "those", "here",
    "make", "made", "does", "did", "doing", "done", "product", "amazon",
    "really", "still", "even", "been", "them", "they", "would", "have", "has",
    "our", "his", "her", "she", "him", "hers", "ours", "mine", "yours", "my",
    "me", "we", "i", "it", "on", "of", "to", "in", "is", "a", "an", "be", "as",
    "if", "so", "or", "at", "up",
}


def normalize_text(value: str) -> str:
    text = value.lower()
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def assign_themes(text: str) -> list[str]:
    hits: list[str] = []
    for theme, keywords in THEME_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            hits.append(theme)
    return hits


def iter_reviews() -> Iterable[dict]:
    with DATA_PATH.open("r", encoding="utf-8") as handle:
        for idx, line in enumerate(handle, start=1):
            if idx % 500_000 == 0:
                print(f"Processed {idx:,} lines...")
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def split_key(record: dict) -> int:
    key = f"{record.get('asin','')}|{record.get('timestamp',0)}|{record.get('rating',0)}"
    return crc32(key.encode("utf-8")) % 5


def month_from_timestamp(timestamp: int) -> str:
    if not timestamp:
        return "Unknown"
    return pd.to_datetime(timestamp, unit="ms", errors="coerce").to_period("M").strftime("%Y-%m")


def top_terms(counter: Counter[str], n: int = 8) -> str:
    return ", ".join(word for word, _ in counter.most_common(n))


def update_term_counter(counter: Counter[str], text: str) -> None:
    for token in text.split():
        if len(token) < 4 or token.isdigit() or token in STOPWORDS:
            continue
        counter[token] += 1


@dataclass
class FirstPassStats:
    total_reviews: int = 0
    rating_sum: float = 0.0
    low_reviews: int = 0
    verified_reviews: int = 0
    helpful_sum: int = 0
    low_helpful_sum: int = 0
    low_helpful_count: int = 0
    rating_counts: Counter = field(default_factory=Counter)
    monthly_sum: dict[str, float] = field(default_factory=lambda: defaultdict(float))
    monthly_count: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    low_theme_count: Counter = field(default_factory=Counter)
    high_theme_count: Counter = field(default_factory=Counter)
    high_segment_count: int = 0
    low_segment_count: int = 0
    high_review_length_sum: int = 0
    low_review_length_sum: int = 0
    high_helpful_sum: int = 0
    low_segment_helpful_sum: int = 0
    high_term_counter: Counter = field(default_factory=Counter)
    low_term_counter: Counter = field(default_factory=Counter)


def first_pass(vectorizer: HashingVectorizer, model: MultinomialNB, batch_size: int = 5000) -> FirstPassStats:
    stats = FirstPassStats()
    batch_texts: list[str] = []
    batch_labels: list[int] = []
    model_initialized = False

    for record in iter_reviews():
        title = (record.get("title") or "").strip()
        text = (record.get("text") or "").strip()
        review_text = f"{title} {text}".strip()
        if not review_text:
            continue

        rating = float(record.get("rating", math.nan))
        if math.isnan(rating):
            continue

        helpful_vote = int(record.get("helpful_vote", 0) or 0)
        verified_purchase = bool(record.get("verified_purchase", False))
        timestamp = int(record.get("timestamp", 0) or 0)
        month = month_from_timestamp(timestamp)
        clean_text = normalize_text(review_text)
        review_length = len(clean_text.split())
        if review_length == 0:
            continue

        stats.total_reviews += 1
        stats.rating_sum += rating
        stats.helpful_sum += helpful_vote
        stats.rating_counts[int(rating)] += 1
        stats.monthly_sum[month] += rating
        stats.monthly_count[month] += 1
        if verified_purchase:
            stats.verified_reviews += 1

        if rating <= 2:
            stats.low_reviews += 1
            stats.low_helpful_sum += helpful_vote
            stats.low_helpful_count += 1
            stats.low_segment_count += 1
            stats.low_review_length_sum += review_length
            stats.low_segment_helpful_sum += helpful_vote
            update_term_counter(stats.low_term_counter, clean_text)
            for theme in assign_themes(clean_text):
                stats.low_theme_count[theme] += 1
        elif rating >= 4:
            stats.high_segment_count += 1
            stats.high_review_length_sum += review_length
            stats.high_helpful_sum += helpful_vote
            update_term_counter(stats.high_term_counter, clean_text)
            for theme in assign_themes(clean_text):
                stats.high_theme_count[theme] += 1

        if rating in (1.0, 2.0, 4.0, 5.0):
            label = 1 if rating >= 4 else 0
            if split_key(record) != 0:
                batch_texts.append(clean_text)
                batch_labels.append(label)

            if len(batch_texts) >= batch_size:
                X_batch = vectorizer.transform(batch_texts)
                y_batch = np.array(batch_labels)
                if not model_initialized:
                    model.partial_fit(X_batch, y_batch, classes=np.array([0, 1]))
                    model_initialized = True
                else:
                    model.partial_fit(X_batch, y_batch)
                batch_texts.clear()
                batch_labels.clear()

    if batch_texts:
        X_batch = vectorizer.transform(batch_texts)
        y_batch = np.array(batch_labels)
        if not model_initialized:
            model.partial_fit(X_batch, y_batch, classes=np.array([0, 1]))
        else:
            model.partial_fit(X_batch, y_batch)

    return stats


def second_pass(vectorizer: HashingVectorizer, model: MultinomialNB) -> dict:
    y_true: list[int] = []
    y_pred: list[int] = []
    y_prob: list[float] = []

    for record in iter_reviews():
        rating = float(record.get("rating", math.nan))
        if rating not in (1.0, 2.0, 4.0, 5.0):
            continue
        if split_key(record) != 0:
            continue

        title = (record.get("title") or "").strip()
        text = (record.get("text") or "").strip()
        review_text = f"{title} {text}".strip()
        clean_text = normalize_text(review_text)
        if not clean_text:
            continue

        label = 1 if rating >= 4 else 0
        X = vectorizer.transform([clean_text])
        prob = float(model.predict_proba(X)[0, 1])
        pred = 1 if prob >= 0.5 else 0

        y_true.append(label)
        y_pred.append(pred)
        y_prob.append(prob)

    y_true_arr = np.array(y_true)
    y_pred_arr = np.array(y_pred)
    y_prob_arr = np.array(y_prob)

    tp = int(((y_true_arr == 1) & (y_pred_arr == 1)).sum())
    tn = int(((y_true_arr == 0) & (y_pred_arr == 0)).sum())
    fp = int(((y_true_arr == 0) & (y_pred_arr == 1)).sum())
    fn = int(((y_true_arr == 1) & (y_pred_arr == 0)).sum())

    accuracy = (tp + tn) / len(y_true_arr)
    precision_pos = tp / (tp + fp) if (tp + fp) else 0.0
    recall_pos = tp / (tp + fn) if (tp + fn) else 0.0
    f1_pos = 2 * precision_pos * recall_pos / (precision_pos + recall_pos) if (precision_pos + recall_pos) else 0.0
    precision_neg = tn / (tn + fn) if (tn + fn) else 0.0
    recall_neg = tn / (tn + fp) if (tn + fp) else 0.0
    f1_neg = 2 * precision_neg * recall_neg / (precision_neg + recall_neg) if (precision_neg + recall_neg) else 0.0
    roc_auc = roc_auc_score(y_true_arr, y_prob_arr)

    metrics = {
        "accuracy": round(float(accuracy), 4),
        "precision_positive": round(float(precision_pos), 4),
        "recall_positive": round(float(recall_pos), 4),
        "f1_positive": round(float(f1_pos), 4),
        "precision_negative": round(float(precision_neg), 4),
        "recall_negative": round(float(recall_neg), 4),
        "f1_negative": round(float(f1_neg), 4),
        "roc_auc": round(float(roc_auc), 4),
        "test_size": int(len(y_true_arr)),
        "negative_reviews_in_test": int((y_true_arr == 0).sum()),
        "positive_reviews_in_test": int((y_true_arr == 1).sum()),
        "false_negative_bad_review": fp,
        "false_positive_good_review": fn,
        "true_negative_bad_review": tn,
        "true_positive_good_review": tp,
    }

    report_df = pd.DataFrame(
        [
            {"class": "bad_review", "precision": precision_neg, "recall": recall_neg, "f1-score": f1_neg, "support": int((y_true_arr == 0).sum())},
            {"class": "good_review", "precision": precision_pos, "recall": recall_pos, "f1-score": f1_pos, "support": int((y_true_arr == 1).sum())},
            {"class": "accuracy", "precision": accuracy, "recall": accuracy, "f1-score": accuracy, "support": len(y_true_arr)},
        ]
    ).round(4)

    return {"metrics": metrics, "report_df": report_df, "cm": np.array([[tn, fp], [fn, tp]])}


def ensure_dirs() -> None:
    for path in [OUTPUT_DIR, FIG_DIR, TABLE_DIR, TEXT_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def create_tables(stats: FirstPassStats) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    avg_rating = round(stats.rating_sum / stats.total_reviews, 3)
    low_rating_pct = round(stats.low_reviews / stats.total_reviews * 100, 2)
    low_helpful_avg = round(stats.low_helpful_sum / stats.low_helpful_count, 2) if stats.low_helpful_count else 0.0
    verified_share = round(stats.verified_reviews / stats.total_reviews * 100, 2)

    monthly_rows = []
    for month, count in stats.monthly_count.items():
        monthly_rows.append({
            "month": month,
            "avg_rating": round(stats.monthly_sum[month] / count, 3),
            "review_count": count,
        })
    monthly = pd.DataFrame(monthly_rows).sort_values("month")

    kpis = pd.DataFrame(
        [
            {"kpi_type": "Primary", "metric": "Average rating", "value": avg_rating, "interpretation": "Overall category health based on customer sentiment."},
            {"kpi_type": "Supporting", "metric": "Low-rating review percentage (1-2 stars)", "value": low_rating_pct, "interpretation": "Shows concentration of serious dissatisfaction."},
            {"kpi_type": "Supporting", "metric": "Average helpful votes on low-rating reviews", "value": low_helpful_avg, "interpretation": "Shows how salient negative reviews are to other shoppers."},
            {"kpi_type": "Guardrail", "metric": "Verified purchase share (%)", "value": verified_share, "interpretation": "Anchors conclusions to more credible purchase experiences."},
        ]
    )

    summary = pd.DataFrame(
        [
            {"metric": "Full reviews analyzed", "value": stats.total_reviews},
            {"metric": "Verified purchase share (%)", "value": verified_share},
            {"metric": "Average helpful votes", "value": round(stats.helpful_sum / stats.total_reviews, 3)},
            {"metric": "Low-rating review count", "value": stats.low_reviews},
        ]
    )

    theme_rows = []
    for theme in THEME_KEYWORDS:
        low_count = stats.low_theme_count[theme]
        high_count = stats.high_theme_count[theme]
        theme_rows.append(
            {
                "theme": theme,
                "low_rating_count": low_count,
                "low_rating_share_pct": round(low_count / stats.low_segment_count * 100, 2) if stats.low_segment_count else 0.0,
                "high_rating_count": high_count,
                "high_rating_share_pct": round(high_count / stats.high_segment_count * 100, 2) if stats.high_segment_count else 0.0,
            }
        )
    themes = pd.DataFrame(theme_rows).sort_values("low_rating_count", ascending=False)

    comparison = pd.DataFrame(
        [
            {
                "segment": "High rating (4-5)",
                "avg_review_length": round(stats.high_review_length_sum / stats.high_segment_count, 2) if stats.high_segment_count else 0.0,
                "avg_helpful_vote": round(stats.high_helpful_sum / stats.high_segment_count, 2) if stats.high_segment_count else 0.0,
                "top_terms": top_terms(stats.high_term_counter),
            },
            {
                "segment": "Low rating (1-2)",
                "avg_review_length": round(stats.low_review_length_sum / stats.low_segment_count, 2) if stats.low_segment_count else 0.0,
                "avg_helpful_vote": round(stats.low_segment_helpful_sum / stats.low_segment_count, 2) if stats.low_segment_count else 0.0,
                "top_terms": top_terms(stats.low_term_counter),
            },
        ]
    )

    return kpis, monthly, summary, themes, comparison


def create_insights() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Temuan Data": "Average rating digunakan sebagai KPI utama untuk menangkap kesehatan kategori secara umum.",
                "Makna Bisnis": "Skor agregat tetap penting sebagai indikator headline, tetapi perlu dibaca bersama sinyal review buruk.",
                "Implikasi Keputusan": "Pantau average rating sebagai metrik utama dashboard dan pasangkan dengan alarm review negatif.",
            },
            {
                "Temuan Data": "Tema keluhan dominan terkonsentrasi pada efektivitas produk, masalah packaging, dan iritasi/efek samping.",
                "Makna Bisnis": "Keluhan utama menyentuh kualitas inti produk dan pengalaman pasca-pembelian.",
                "Implikasi Keputusan": "Prioritaskan audit kualitas produk, kemasan, dan formulasi pada item yang paling sering dikeluhkan.",
            },
            {
                "Temuan Data": "Model klasifikasi sederhana mampu membantu memilah review baik dan review buruk pada skala besar.",
                "Makna Bisnis": "Tim bisnis dapat mempercepat triase keluhan tanpa membaca seluruh review secara manual.",
                "Implikasi Keputusan": "Gunakan model sebagai sistem prioritas tindak lanjut untuk QA dan customer service.",
            },
        ]
    )


def save_figures(stats: FirstPassStats, monthly: pd.DataFrame, themes: pd.DataFrame, cm: np.ndarray) -> None:
    sns.set_theme(style="whitegrid")

    rating_df = pd.DataFrame(
        {"rating": sorted(stats.rating_counts.keys()), "count": [stats.rating_counts[r] for r in sorted(stats.rating_counts.keys())]}
    )
    plt.figure(figsize=(7, 4))
    sns.barplot(data=rating_df, x="rating", y="count", color="#D97706")
    plt.title("Rating Distribution in Full Dataset")
    plt.xlabel("Rating")
    plt.ylabel("Review Count")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "rating_distribution.png", dpi=200)
    plt.close()

    monthly_plot = monthly[monthly["month"] != "Unknown"].copy()
    if not monthly_plot.empty:
        plt.figure(figsize=(10, 4))
        plt.plot(monthly_plot["month"], monthly_plot["avg_rating"], marker="o", color="#2563EB")
        plt.xticks(rotation=60, ha="right")
        plt.title("Average Rating by Month")
        plt.xlabel("Month")
        plt.ylabel("Average Rating")
        plt.tight_layout()
        plt.savefig(FIG_DIR / "monthly_avg_rating.png", dpi=200)
        plt.close()

    plot_data = themes.sort_values("low_rating_count", ascending=True)
    plt.figure(figsize=(9, 4.5))
    plt.barh(plot_data["theme"], plot_data["low_rating_count"], color="#DC2626")
    plt.title("Complaint Theme Counts in Low Ratings (1-2 Stars)")
    plt.xlabel("Review Count")
    plt.ylabel("Theme")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "complaint_themes.png", dpi=200)
    plt.close()

    plt.figure(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False)
    plt.title("Confusion Matrix")
    plt.xlabel("Predicted Label")
    plt.ylabel("Actual Label")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "confusion_matrix.png", dpi=200)
    plt.close()


def write_outputs(
    stats: FirstPassStats,
    kpis: pd.DataFrame,
    monthly: pd.DataFrame,
    summary: pd.DataFrame,
    themes: pd.DataFrame,
    comparison: pd.DataFrame,
    insights: pd.DataFrame,
    model_report: pd.DataFrame,
    metrics: dict,
) -> None:
    kpis.to_csv(TABLE_DIR / "kpi_table.csv", index=False)
    monthly.to_csv(TABLE_DIR / "monthly_rating.csv", index=False)
    summary.to_csv(TABLE_DIR / "full_data_summary.csv", index=False)
    themes.to_csv(TABLE_DIR / "voc_themes.csv", index=False)
    comparison.to_csv(TABLE_DIR / "review_segment_comparison.csv", index=False)
    insights.to_csv(TABLE_DIR / "business_translation.csv", index=False)
    model_report.to_csv(TABLE_DIR / "classification_report.csv", index=False)
    pd.DataFrame([metrics]).to_csv(TABLE_DIR / "model_metrics.csv", index=False)

    primary_rating = float(kpis.loc[kpis["metric"] == "Average rating", "value"].iloc[0])
    low_rating_pct = float(kpis.loc[kpis["metric"] == "Low-rating review percentage (1-2 stars)", "value"].iloc[0])
    low_helpful = float(kpis.loc[kpis["metric"] == "Average helpful votes on low-rating reviews", "value"].iloc[0])
    guardrail = float(kpis.loc[kpis["metric"] == "Verified purchase share (%)", "value"].iloc[0])
    top3_themes = themes.head(3)["theme"].tolist()

    memo = f"""# Decision Memo

## Analisis Review Pelanggan untuk Mendukung Keputusan Bisnis pada Kategori Beauty and Personal Care

Nama Mahasiswa: [Isi Nama Anda]  
NIM: [Isi NIM Anda]  
Mata Kuliah: Analisis Keputusan Bisnis  
Tahun Akademik: 2025/2026

## Konteks Data

Analisis ini menggunakan **seluruh review** dari file lokal `Beauty_and_Personal_Care.jsonl` yang berasal dari dataset resmi Amazon Reviews 2023. File dibaca secara streaming agar seluruh kategori tetap dapat dianalisis tanpa sampling. Total review yang terproses dalam analisis ini adalah **{stats.total_reviews:,} review**.

## KPI Keputusan

KPI utama yang dipilih adalah **average rating**. Pada seluruh data kategori, rata-rata rating tercatat **{primary_rating:.3f}**.

Dua KPI turunan yang digunakan adalah:

1. **Persentase review buruk (1-2 bintang)** sebesar **{low_rating_pct:.2f}%**.
2. **Average helpful votes pada review buruk** sebesar **{low_helpful:.2f}**.

Guardrail KPI yang digunakan adalah **verified purchase share** sebesar **{guardrail:.2f}%** agar rekomendasi tetap bertumpu pada pengalaman pembelian yang lebih kredibel.

## Temuan Utama Voice of Customer

Tiga tema keluhan yang paling dominan pada review 1-2 bintang adalah:

1. **{top3_themes[0]}**
2. **{top3_themes[1]}**
3. **{top3_themes[2]}**

Pola review buruk menunjukkan bahwa keluhan pelanggan banyak berkaitan dengan ketidakefektifan produk, kualitas kemasan saat produk diterima, serta reaksi negatif setelah penggunaan.

## Hasil Predictive Modeling

Model klasifikasi sederhana menggunakan **Multinomial Naive Bayes** dengan fitur teks review (`HashingVectorizer`) untuk membedakan review baik (`4-5`) dan review buruk (`1-2`). Hasil pada data uji menunjukkan:

- Accuracy: **{metrics['accuracy']:.4f}**
- Precision kelas review baik: **{metrics['precision_positive']:.4f}**
- Recall kelas review baik: **{metrics['recall_positive']:.4f}**
- F1-score kelas review baik: **{metrics['f1_positive']:.4f}**
- ROC-AUC: **{metrics['roc_auc']:.4f}**

Model ini cukup membantu untuk triase awal review dalam volume besar, terutama untuk membantu tim bisnis, QA, dan customer service memprioritaskan review yang perlu ditindaklanjuti lebih cepat.

## Risiko Bisnis Mis-klasifikasi

Risiko utama muncul ketika **review buruk diprediksi sebagai review baik**. Jika ini terjadi, keluhan serius dapat terlewat, respons bisnis menjadi terlambat, dan masalah kualitas bisa berkembang menjadi penurunan rating, peningkatan retur, dan kerusakan reputasi.

## Rekomendasi Keputusan Bisnis

1. Prioritaskan audit kualitas pada produk dengan keluhan efektivitas paling tinggi.
2. Perkuat quality control kemasan dan proses distribusi untuk menekan keluhan kebocoran atau kerusakan.
3. Gunakan dashboard yang memasangkan average rating dengan persentase review buruk sebagai early warning.
4. Gunakan model klasifikasi sebagai alat prioritas, bukan pengganti evaluasi manual penuh.
"""

    appendix = f"""# Appendix Evidence

## Ringkasan Data

- Data yang dianalisis: seluruh file `Beauty_and_Personal_Care.jsonl`
- Total review terproses: {stats.total_reviews:,}
- Sumber dataset: {DATASET_URL}
- Dokumentasi field dataset: {DATASET_DOC_URL}

## Bukti KPI

File tabel:

- `outputs/tables/kpi_table.csv`
- `outputs/tables/monthly_rating.csv`
- `outputs/tables/full_data_summary.csv`

Grafik:

- `outputs/figures/rating_distribution.png`
- `outputs/figures/monthly_avg_rating.png`

## Bukti Voice of Customer

File tabel:

- `outputs/tables/voc_themes.csv`
- `outputs/tables/review_segment_comparison.csv`
- `outputs/tables/business_translation.csv`

Grafik:

- `outputs/figures/complaint_themes.png`

## Bukti Model Prediktif

Model: Multinomial Naive Bayes  
Fitur utama: teks review yang diubah menjadi fitur hashing bag-of-words

File evaluasi:

- `outputs/tables/model_metrics.csv`
- `outputs/tables/classification_report.csv`
- `outputs/figures/confusion_matrix.png`

## Catatan Metodologi

1. Analisis menggunakan seluruh data kategori dari file lokal `Beauty_and_Personal_Care.jsonl`.
2. Proses dilakukan secara streaming agar file besar tetap dapat dianalisis tanpa sampling.
3. Tema keluhan diidentifikasi dengan pendekatan keyword-based thematic coding agar mudah diterjemahkan ke konteks bisnis.
"""

    references = f"""# Daftar Pustaka

1. McAuley Lab. (2024). *Amazon Reviews 2023*. Hugging Face Datasets. {DATASET_URL}
2. Hou, Y., Li, J., He, Z., et al. (2024). *Bridging Language and Items for Retrieval and Recommendation*. arXiv. {PAPER_URL}
3. Amazon Reviews'23. (2024). *Dataset Documentation and Data Fields*. {DATASET_DOC_URL}
4. James, G., Witten, D., Hastie, T., & Tibshirani, R. (2021). *An Introduction to Statistical Learning* (2nd ed.). Springer.
"""

    (BASE_DIR / "decision_memo.md").write_text(memo, encoding="utf-8")
    (BASE_DIR / "appendix_evidence.md").write_text(appendix, encoding="utf-8")
    (BASE_DIR / "daftar_pustaka.md").write_text(references, encoding="utf-8")

    run_summary = {
        "data_source": str(DATA_PATH),
        "full_reviews_analyzed": stats.total_reviews,
        "dataset_url": DATASET_URL,
        "primary_kpi_average_rating": primary_rating,
        "low_rating_pct": low_rating_pct,
        "low_rating_helpful_vote_average": low_helpful,
        "guardrail_verified_purchase_share_pct": guardrail,
        "top_3_themes": top3_themes,
        "model_type": "Multinomial Naive Bayes",
        "model_metrics": metrics,
    }
    (TEXT_DIR / "run_summary.json").write_text(json.dumps(run_summary, indent=2), encoding="utf-8")


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset file not found: {DATA_PATH}")

    ensure_dirs()
    vectorizer = HashingVectorizer(n_features=2**18, alternate_sign=False, ngram_range=(1, 2), norm="l2")
    model = MultinomialNB(alpha=0.5)

    print("Starting first pass on full dataset...")
    stats = first_pass(vectorizer, model)
    print("Starting evaluation pass...")
    eval_result = second_pass(vectorizer, model)

    kpis, monthly, summary, themes, comparison = create_tables(stats)
    insights = create_insights()
    save_figures(stats, monthly, themes, eval_result["cm"])
    write_outputs(
        stats=stats,
        kpis=kpis,
        monthly=monthly,
        summary=summary,
        themes=themes,
        comparison=comparison,
        insights=insights,
        model_report=eval_result["report_df"],
        metrics=eval_result["metrics"],
    )

    print("Full-data analysis completed.")
    print(f"Reviews analyzed: {stats.total_reviews:,}")
    print(f"Decision memo: {BASE_DIR / 'decision_memo.md'}")
    print(f"Outputs folder: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

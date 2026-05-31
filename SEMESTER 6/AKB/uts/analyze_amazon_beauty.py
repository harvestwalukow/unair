from __future__ import annotations

import json
import math
import re
import time
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
SAMPLE_RATIO = 0.25
SAMPLE_BUCKET_MOD = 4
SAMPLE_BUCKET_KEEP = 0

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
    yield from iter_reviews_with_progress("General")


def iter_reviews_with_progress(stage: str, log_every: int = 100_000) -> Iterable[dict]:
    file_size = DATA_PATH.stat().st_size
    bytes_read = 0
    start = time.time()

    with DATA_PATH.open("r", encoding="utf-8") as handle:
        for idx, line in enumerate(handle, start=1):
            bytes_read += len(line.encode("utf-8"))
            if idx % log_every == 0:
                elapsed = time.time() - start
                pct = (bytes_read / file_size) * 100 if file_size else 0.0
                speed = idx / elapsed if elapsed else 0.0
                print(
                    f"[{stage}] {idx:,} lines | {pct:5.2f}% file read | "
                    f"{speed:,.0f} reviews/sec | elapsed {elapsed/60:,.1f} min"
                )
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def split_key(record: dict) -> int:
    key = f"{record.get('asin','')}|{record.get('timestamp',0)}|{record.get('rating',0)}"
    return crc32(key.encode("utf-8")) % 5


def sample_key(record: dict, month: str, rating: float) -> int:
    key = (
        f"{month}|{rating}|{record.get('asin','')}|{record.get('parent_asin','')}|"
        f"{record.get('user_id','')}|{record.get('timestamp',0)}"
    )
    return crc32(key.encode("utf-8")) % SAMPLE_BUCKET_MOD


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
    total_rows_seen: int = 0
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
    trained_rows = 0
    trained_batches = 0

    print("[Pass 1] Starting KPI, VOC, and training pass...")
    for record in iter_reviews_with_progress("Pass 1"):
        stats.total_rows_seen += 1
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
        if sample_key(record, month, rating) != SAMPLE_BUCKET_KEEP:
            continue
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
                trained_rows += len(batch_texts)
                trained_batches += 1
                if trained_batches % 20 == 0:
                    print(
                        f"[Pass 1] Trained {trained_rows:,} labeled reviews "
                        f"across {trained_batches:,} batches"
                    )
                batch_texts.clear()
                batch_labels.clear()

    if batch_texts:
        X_batch = vectorizer.transform(batch_texts)
        y_batch = np.array(batch_labels)
        if not model_initialized:
            model.partial_fit(X_batch, y_batch, classes=np.array([0, 1]))
        else:
            model.partial_fit(X_batch, y_batch)
        trained_rows += len(batch_texts)
        trained_batches += 1

    print(
        f"[Pass 1] Completed. Rows seen: {stats.total_rows_seen:,}. "
        f"Sampled reviews analyzed: {stats.total_reviews:,}. "
        f"Labeled reviews used for training: {trained_rows:,} in {trained_batches:,} batches."
    )

    return stats


def second_pass(vectorizer: HashingVectorizer, model: MultinomialNB, batch_size: int = 5000) -> dict:
    y_true: list[int] = []
    y_pred: list[int] = []
    y_prob: list[float] = []
    batch_texts: list[str] = []
    batch_labels: list[int] = []
    eval_rows = 0

    print("[Pass 2] Starting evaluation pass...")
    for record in iter_reviews_with_progress("Pass 2"):
        rating = float(record.get("rating", math.nan))
        if rating not in (1.0, 2.0, 4.0, 5.0):
            continue

        timestamp = int(record.get("timestamp", 0) or 0)
        month = month_from_timestamp(timestamp)
        if sample_key(record, month, rating) != SAMPLE_BUCKET_KEEP:
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
        batch_texts.append(clean_text)
        batch_labels.append(label)

        if len(batch_texts) >= batch_size:
            X = vectorizer.transform(batch_texts)
            probs = model.predict_proba(X)[:, 1]
            preds = (probs >= 0.5).astype(int)
            y_true.extend(batch_labels)
            y_pred.extend(preds.tolist())
            y_prob.extend(probs.tolist())
            eval_rows += len(batch_texts)
            if eval_rows % 100_000 == 0:
                print(f"[Pass 2] Evaluated {eval_rows:,} labeled reviews")
            batch_texts.clear()
            batch_labels.clear()

    if batch_texts:
        X = vectorizer.transform(batch_texts)
        probs = model.predict_proba(X)[:, 1]
        preds = (probs >= 0.5).astype(int)
        y_true.extend(batch_labels)
        y_pred.extend(preds.tolist())
        y_prob.extend(probs.tolist())
        eval_rows += len(batch_texts)

    print(f"[Pass 2] Completed. Evaluated {eval_rows:,} labeled reviews.")

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
            {"metric": "Sampling ratio (%)", "value": round(SAMPLE_RATIO * 100, 2)},
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
    model_report: pd.DataFrame,
    metrics: dict,
) -> None:
    kpis.to_csv(TABLE_DIR / "kpi_table.csv", index=False)
    monthly.to_csv(TABLE_DIR / "monthly_rating.csv", index=False)
    summary.to_csv(TABLE_DIR / "full_data_summary.csv", index=False)
    themes.to_csv(TABLE_DIR / "voc_themes.csv", index=False)
    comparison.to_csv(TABLE_DIR / "review_segment_comparison.csv", index=False)
    model_report.to_csv(TABLE_DIR / "classification_report.csv", index=False)
    pd.DataFrame([metrics]).to_csv(TABLE_DIR / "model_metrics.csv", index=False)

    primary_rating = float(kpis.loc[kpis["metric"] == "Average rating", "value"].iloc[0])
    low_rating_pct = float(kpis.loc[kpis["metric"] == "Low-rating review percentage (1-2 stars)", "value"].iloc[0])
    low_helpful = float(kpis.loc[kpis["metric"] == "Average helpful votes on low-rating reviews", "value"].iloc[0])
    guardrail = float(kpis.loc[kpis["metric"] == "Verified purchase share (%)", "value"].iloc[0])
    top3_themes = themes.head(3)["theme"].tolist()

    run_summary = {
        "data_source": str(DATA_PATH),
        "sampling_method": "Proportionate stratified deterministic sampling by month and rating using hash buckets",
        "sampling_ratio": SAMPLE_RATIO,
        "full_reviews_available": stats.total_rows_seen,
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

    print(f"Dataset file: {DATA_PATH}")
    print(f"Dataset size: {DATA_PATH.stat().st_size / (1024**3):.2f} GB")
    print(
        "Sampling method: proportionate stratified deterministic sampling "
        f"by month and rating with ratio {SAMPLE_RATIO:.0%}"
    )
    stats = first_pass(vectorizer, model)
    eval_result = second_pass(vectorizer, model)

    kpis, monthly, summary, themes, comparison = create_tables(stats)
    save_figures(stats, monthly, themes, eval_result["cm"])
    write_outputs(
        stats=stats,
        kpis=kpis,
        monthly=monthly,
        summary=summary,
        themes=themes,
        comparison=comparison,
        model_report=eval_result["report_df"],
        metrics=eval_result["metrics"],
    )

    print("Full-data analysis completed.")
    print(f"Reviews analyzed: {stats.total_reviews:,}")
    print(f"Outputs folder: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

"""Build and forecast a weekly Indonesian Economic Stress Index (ESI).

The pipeline uses the data already collected in this workspace:
X posts, Google Trends, and daily USD/IDR. Preprocessing, imputation,
standardization, and PCA are fitted on the chronological training period only.
"""

from __future__ import annotations

import argparse
import json
import random
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.base import clone
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor


SEED = 42
SENTIMENT_MODEL = "w11wo/indonesian-roberta-base-sentiment-classifier"
WEEK_FREQ = "W-SUN"

X_PATH = Path("data/raw/x/x_harga_ekonomi_top20_2022_2026_raw_combined.csv")
GT_PATH = Path("data/raw/google_trends_native/google_trends_raw.csv")
FX_PATH = Path("data/idr_usd_2022_today.csv")
SENTIMENT_CACHE = Path("data/processed/x_sentiment.csv")
OUTPUT_DIR = Path("output")
FIGURE_DIR = OUTPUT_DIR / "figures"

GT_RENAME = {
    "harga naik": "gt_harga_naik",
    "biaya hidup": "gt_biaya_hidup",
    "harga beras": "gt_harga_beras",
    "harga bbm": "gt_harga_bbm",
    "PHK": "gt_phk",
}

GT_FEATURES = list(GT_RENAME.values())
GT_WINSOR_QUANTILE = 0.975

PCA_FEATURES = [
    "x_tweet_volume_log1p",
    "x_negative_sentiment_mean",
    "x_negative_tweet_ratio",
    "gt_harga_naik",
    "gt_biaya_hidup",
    "gt_harga_beras",
    "gt_harga_bbm",
    "gt_phk",
    "gt_mean_score",
    "usd_idr_return",
    "usd_idr_volatility_4w",
    "rupiah_depreciation_dummy",
]

FORECAST_BASE_FEATURES = [
    "esi_current",
    "gt_mean_score",
    *GT_FEATURES,
    "x_tweet_volume_log1p",
    "x_negative_sentiment_mean",
    "x_negative_tweet_ratio",
    "usd_idr_return",
    "usd_idr_volatility_4w",
    "rupiah_depreciation_dummy",
]


def forecast_feature_names() -> list[str]:
    names = list(FORECAST_BASE_FEATURES)
    for _, prefix in [
        ("esi_current", "esi"),
        ("gt_mean_score", "gt_mean_score"),
        ("x_negative_sentiment_mean", "x_negative_sentiment_mean"),
        ("usd_idr_return", "usd_idr_return"),
    ]:
        names.extend(f"{prefix}_lag_{lag}" for lag in [1, 2, 3, 4, 8])
        names.extend(f"{prefix}_diff_{period}" for period in [1, 2, 4])
        names.extend(f"{prefix}_roll_mean_{window}" for window in [2, 4, 8])
    for column in GT_FEATURES:
        names.extend(f"{column}_lag_{lag}" for lag in [1, 2, 4])
        names.append(f"{column}_diff_1")
    names.extend(["esi_squared", "esi_momentum", "esi_momentum_squared", "esi_level_momentum"])
    return names


FORECAST_FEATURES = forecast_feature_names()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=["all", "sentiment", "model"], default="all")
    parser.add_argument("--start", default="2022-01-01")
    parser.add_argument("--end", default="2026-06-20")
    parser.add_argument("--force-sentiment", action="store_true")
    return parser.parse_args()


def set_seed() -> None:
    random.seed(SEED)
    np.random.seed(SEED)


def clean_text(text: object) -> str:
    value = str(text or "")
    value = re.sub(r"https?://\S+|www\.\S+", " ", value)
    value = re.sub(r"@\w+", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def score_sentiment(x: pd.DataFrame, force: bool = False) -> pd.DataFrame:
    """Return Indonesian X posts with negative-class probabilities."""
    needed = x.loc[x["lang"].eq("in")].copy()
    needed["clean_text"] = needed["full_text"].map(clean_text)
    needed = needed.loc[needed["clean_text"].ne("")].copy()
    needed["id_str"] = needed["id_str"].astype(str)

    if SENTIMENT_CACHE.exists() and not force:
        cached = pd.read_csv(SENTIMENT_CACHE, dtype={"id_str": str})
        required = {"id_str", "negative_probability", "sentiment_label"}
        if required.issubset(cached.columns) and set(needed["id_str"]).issubset(set(cached["id_str"])):
            return needed.merge(cached[list(required)], on="id_str", how="left", validate="one_to_one")

    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(SENTIMENT_MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(SENTIMENT_MODEL)
    model.eval()
    label_map = {int(k): str(v).lower() for k, v in model.config.id2label.items()}
    negative_index = next(index for index, label in label_map.items() if label == "negative")

    probabilities: list[float] = []
    labels: list[str] = []
    texts = needed["clean_text"].tolist()
    batch_size = 16
    with torch.inference_mode():
        for start in range(0, len(texts), batch_size):
            batch = texts[start : start + batch_size]
            encoded = tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=256,
                return_tensors="pt",
            )
            logits = model(**encoded).logits
            probs = torch.softmax(logits, dim=-1).cpu().numpy()
            probabilities.extend(probs[:, negative_index].astype(float).tolist())
            labels.extend(label_map[int(index)] for index in probs.argmax(axis=1))

    needed["negative_probability"] = probabilities
    needed["sentiment_label"] = labels
    SENTIMENT_CACHE.parent.mkdir(parents=True, exist_ok=True)
    needed[["id_str", "negative_probability", "sentiment_label"]].to_csv(
        SENTIMENT_CACHE, index=False
    )
    return needed


def weekly_x(x_scored: pd.DataFrame) -> pd.DataFrame:
    x = x_scored.copy()
    timestamps = pd.to_datetime(x["created_at"], utc=True).dt.tz_convert("Asia/Jakarta")
    x["week"] = timestamps.dt.tz_localize(None).dt.to_period(WEEK_FREQ).dt.end_time.dt.normalize()
    weekly = x.groupby("week", as_index=False).agg(
        x_tweet_volume=("id_str", "nunique"),
        x_negative_sentiment_mean=("negative_probability", "mean"),
        x_negative_tweet_ratio=("sentiment_label", lambda values: float((values == "negative").mean())),
    )
    weekly["x_tweet_volume_log1p"] = np.log1p(weekly["x_tweet_volume"])
    return weekly


def weekly_google_trends() -> pd.DataFrame:
    gt = pd.read_csv(GT_PATH)
    gt["week"] = pd.to_datetime(gt["week"])
    gt = gt.rename(columns=GT_RENAME)
    terms = list(GT_RENAME.values())
    gt["gt_mean_score"] = gt[terms].mean(axis=1)
    return gt[["week", *terms, "gt_mean_score", "isPartial"]].copy()


def weekly_fx() -> pd.DataFrame:
    fx = pd.read_csv(FX_PATH)
    fx["date"] = pd.to_datetime(fx["date"])
    fx = fx.set_index("date").sort_index()
    weekly = fx["usd_idr"].resample(WEEK_FREQ).last().rename("usd_idr_close").to_frame()
    weekly["usd_idr_return"] = weekly["usd_idr_close"].pct_change(fill_method=None)
    weekly["usd_idr_volatility_4w"] = weekly["usd_idr_return"].rolling(4).std()
    weekly["rupiah_depreciation_dummy"] = (weekly["usd_idr_return"] > 0).astype(float)
    return weekly.reset_index(names="week")


def build_weekly_dataset(x_scored: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    gt = weekly_google_trends()
    fx = weekly_fx()
    x = weekly_x(x_scored)

    # Google Trends is the weekly calendar because it is already observed weekly.
    merged = gt.merge(fx, on="week", how="left", validate="one_to_one")
    merged = merged.merge(x, on="week", how="left", validate="one_to_one")
    merged = merged.loc[
        merged["week"].between(pd.Timestamp(start), pd.Timestamp(end), inclusive="both")
    ].sort_values("week").reset_index(drop=True)
    merged["x_tweet_volume"] = merged["x_tweet_volume"].fillna(0)
    merged["x_tweet_volume_log1p"] = np.log1p(merged["x_tweet_volume"])
    return merged


def construct_esi(data: pd.DataFrame) -> tuple[pd.DataFrame, dict, SimpleImputer, StandardScaler, PCA]:
    n_train = int(np.floor(len(data) * 0.80))
    if n_train < 30 or len(data) - n_train < 10:
        raise ValueError("Insufficient chronological observations for an 80/20 split.")
    train_mask = np.arange(len(data)) < n_train

    # Limit extreme Trends observations using bounds learned only from train.
    modelling_data = data.copy()
    modelling_data["gt_mean_score_raw"] = modelling_data["gt_mean_score"]
    modelling_data[GT_FEATURES] = modelling_data[GT_FEATURES].astype(float)
    gt_upper_bounds = modelling_data.loc[train_mask, GT_FEATURES].quantile(GT_WINSOR_QUANTILE)
    modelling_data.loc[:, GT_FEATURES] = modelling_data[GT_FEATURES].clip(
        upper=gt_upper_bounds, axis=1
    )
    modelling_data["gt_mean_score"] = modelling_data[GT_FEATURES].mean(axis=1)

    imputer = SimpleImputer(strategy="median")
    scaler = StandardScaler()
    pca = PCA()
    train_imputed = imputer.fit_transform(modelling_data.loc[train_mask, PCA_FEATURES])
    train_scaled = scaler.fit_transform(train_imputed)
    pca.fit(train_scaled)
    all_imputed = imputer.transform(modelling_data[PCA_FEATURES])
    all_scaled = scaler.transform(all_imputed)
    raw_pc1 = pca.transform(all_scaled)[:, 0]

    obvious_stress = modelling_data[
        ["x_negative_sentiment_mean", "x_negative_tweet_ratio", "gt_mean_score",
         "usd_idr_volatility_4w", "rupiah_depreciation_dummy"]
    ].copy()
    stress_imputed = SimpleImputer(strategy="median").fit_transform(obvious_stress.loc[train_mask])
    stress_reference_train = StandardScaler().fit_transform(stress_imputed).mean(axis=1)
    orientation_corr = float(np.corrcoef(raw_pc1[train_mask], stress_reference_train)[0, 1])
    sign = 1.0 if np.isfinite(orientation_corr) and orientation_corr >= 0 else -1.0

    result = modelling_data.copy()
    # The published modelling dataset contains train-fitted imputations.
    result.loc[:, PCA_FEATURES] = all_imputed
    result["esi"] = raw_pc1 * sign
    result["split"] = np.where(train_mask, "train", "test")
    loadings = pca.components_[0] * sign
    metadata = {
        "weeks": int(len(data)),
        "pca_train_weeks": int(n_train),
        "pca_test_weeks": int(len(data) - n_train),
        "test_start_week": modelling_data.loc[n_train, "week"].date().isoformat(),
        "google_trends_winsor_quantile": GT_WINSOR_QUANTILE,
        "google_trends_train_upper_bounds": {
            name: float(value) for name, value in gt_upper_bounds.items()
        },
        "pc1_explained_variance_ratio": float(pca.explained_variance_ratio_[0]),
        "orientation_correlation_before_sign": orientation_corr,
        "orientation_sign": int(sign),
        "pca_loadings": {name: float(value) for name, value in zip(PCA_FEATURES, loadings)},
    }
    return result, metadata, imputer, scaler, pca


def make_forecast_dataset(esi: pd.DataFrame) -> pd.DataFrame:
    frame = esi.copy()
    frame["esi_current"] = frame["esi"]
    for column, prefix in [
        ("esi_current", "esi"),
        ("gt_mean_score", "gt_mean_score"),
        ("x_negative_sentiment_mean", "x_negative_sentiment_mean"),
        ("usd_idr_return", "usd_idr_return"),
    ]:
        for lag in [1, 2, 3, 4, 8]:
            frame[f"{prefix}_lag_{lag}"] = frame[column].shift(lag)
        for period in [1, 2, 4]:
            frame[f"{prefix}_diff_{period}"] = frame[column].diff(period)
        for window in [2, 4, 8]:
            frame[f"{prefix}_roll_mean_{window}"] = frame[column].rolling(window).mean()
    for column in GT_FEATURES:
        for lag in [1, 2, 4]:
            frame[f"{column}_lag_{lag}"] = frame[column].shift(lag)
        frame[f"{column}_diff_1"] = frame[column].diff()
    frame["esi_squared"] = frame["esi_current"] ** 2
    frame["esi_momentum"] = frame["esi_current"].diff()
    frame["esi_momentum_squared"] = frame["esi_momentum"] ** 2
    frame["esi_level_momentum"] = frame["esi_current"] * frame["esi_momentum"]
    frame["esi_next_week"] = frame["esi"].shift(-1)
    frame["target_week"] = frame["week"].shift(-1)
    needed = [*FORECAST_FEATURES, "esi_next_week", "target_week"]
    return frame.dropna(subset=needed).reset_index(drop=True)


def regression_metrics(y_true: pd.Series, prediction: np.ndarray) -> dict[str, float]:
    return {
        "mae": float(mean_absolute_error(y_true, prediction)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, prediction))),
        "r2": float(r2_score(y_true, prediction)),
    }


def fit_models(forecast: pd.DataFrame, test_start_week: str):
    cutoff = pd.Timestamp(test_start_week)
    train = forecast.loc[forecast["target_week"] < cutoff].copy()
    test = forecast.loc[forecast["week"] >= cutoff].copy()
    if train.empty or test.empty:
        raise ValueError("Chronological train/test forecast split is empty.")

    x_train = train[FORECAST_FEATURES]
    y_train = train["esi_next_week"]
    y_test = test["esi_next_week"]

    linear = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", LinearRegression()),
    ])
    ridge = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", Ridge(alpha=10.0)),
    ])
    random_forest = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", RandomForestRegressor(
            n_estimators=150,
            max_depth=5,
            min_samples_leaf=8,
            max_features=0.8,
            random_state=SEED,
            n_jobs=1,
        )),
    ])
    xgboost = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", XGBRegressor(
            n_estimators=100,
            max_depth=2,
            learning_rate=0.1,
            min_child_weight=5,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_lambda=10.0,
            objective="reg:squarederror",
            random_state=SEED,
            n_jobs=1,
            verbosity=0,
        )),
    ])
    learned_specs = {
        "Linear Regression": linear,
        "Ridge Regression": ridge,
        "Random Forest": random_forest,
        "XGBoost": xgboost,
    }

    # Expanding walk-forward: at week t, targets through t are available.
    learned_predictions = {name: [] for name in learned_specs}
    for index in range(len(test)):
        history = pd.concat([train, test.iloc[:index]], ignore_index=True)
        for name, estimator in learned_specs.items():
            model = clone(estimator)
            model.fit(history[FORECAST_FEATURES], history["esi_next_week"])
            learned_predictions[name].append(
                float(model.predict(test.loc[[test.index[index]], FORECAST_FEATURES])[0])
            )

    predictions = {
        "Naive Forecast": test["esi_current"].to_numpy(),
        "Moving Average 4 Minggu": test[
            ["esi_current", "esi_lag_1", "esi_lag_2", "esi_lag_3"]
        ].mean(axis=1).to_numpy(),
        **{name: np.asarray(values) for name, values in learned_predictions.items()},
    }
    predictions["Ensemble Ridge-Random Forest"] = (
        0.5 * predictions["Ridge Regression"] + 0.5 * predictions["Random Forest"]
    )
    naive_mae = regression_metrics(y_test, predictions["Naive Forecast"])["mae"]
    result_rows = []
    for model_name, prediction in predictions.items():
        metrics = regression_metrics(y_test, prediction)
        metrics["model"] = model_name
        metrics["mae_improvement_vs_naive_pct"] = float(
            (naive_mae - metrics["mae"]) / naive_mae * 100
        )
        result_rows.append(metrics)
    results = pd.DataFrame(result_rows)[
        ["model", "mae", "rmse", "r2", "mae_improvement_vs_naive_pct"]
    ].sort_values("rmse").reset_index(drop=True)

    prediction_frame = test[["week", "target_week", "esi_next_week"]].rename(
        columns={"esi_next_week": "actual_esi"}
    )
    for model_name, prediction in predictions.items():
        prediction_frame[model_name] = prediction

    models = {}
    for name, estimator in learned_specs.items():
        fitted = clone(estimator)
        fitted.fit(x_train, y_train)
        models[name] = fitted

    # Training-only expanding CV documents ensemble selection.
    cv_actual: list[float] = []
    cv_predictions = {"Ridge Regression": [], "Random Forest": [], "Ensemble": []}
    for cv_train, cv_valid in TimeSeriesSplit(n_splits=5).split(train):
        ridge_cv = clone(ridge).fit(
            train.iloc[cv_train][FORECAST_FEATURES], train.iloc[cv_train]["esi_next_week"]
        )
        rf_cv = clone(random_forest).fit(
            train.iloc[cv_train][FORECAST_FEATURES], train.iloc[cv_train]["esi_next_week"]
        )
        ridge_pred = ridge_cv.predict(train.iloc[cv_valid][FORECAST_FEATURES])
        rf_pred = rf_cv.predict(train.iloc[cv_valid][FORECAST_FEATURES])
        cv_actual.extend(train.iloc[cv_valid]["esi_next_week"].to_numpy())
        cv_predictions["Ridge Regression"].extend(ridge_pred)
        cv_predictions["Random Forest"].extend(rf_pred)
        cv_predictions["Ensemble"].extend(0.5 * ridge_pred + 0.5 * rf_pred)

    tuning = {
        "forecast_protocol": "expanding walk-forward one-step-ahead",
        "ensemble_weights": {"Ridge Regression": 0.5, "Random Forest": 0.5},
        "random_forest_params": random_forest.named_steps["model"].get_params(),
        "ridge_alpha": 10.0,
        "training_cv_metrics": {
            name: regression_metrics(np.asarray(cv_actual), np.asarray(values))
            for name, values in cv_predictions.items()
        },
        "forecast_train_rows": int(len(train)),
        "forecast_test_rows": int(len(test)),
    }
    return results, prediction_frame, models, tuning, train, test


def save_figures(
    weekly: pd.DataFrame,
    esi: pd.DataFrame,
    results: pd.DataFrame,
    predictions: pd.DataFrame,
    models: dict,
    pca: PCA,
) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", context="notebook")

    fig, ax = plt.subplots(figsize=(12, 4.8))
    ax.plot(esi["week"], esi["esi"], color="#0f766e", linewidth=1.6)
    test_start = esi.loc[esi["split"].eq("test"), "week"].min()
    ax.axvline(test_start, color="#b91c1c", linestyle="--", label="Awal periode uji")
    ax.axhline(0, color="gray", linewidth=0.8)
    ax.set(title="Economic Stress Index Mingguan", xlabel="Minggu", ylabel="ESI (skor PC1)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "fig_esi_timeseries.png", dpi=220)
    plt.close(fig)

    best_model = results.iloc[0]["model"]
    fig, ax = plt.subplots(figsize=(12, 6.2))
    ax.plot(
        predictions["target_week"], predictions["actual_esi"],
        color="#2563eb", marker="o", markersize=3.8, linewidth=2,
        label="ESI aktual pada minggu target",
    )
    ax.plot(
        predictions["target_week"], predictions[best_model],
        color="#ea580c", marker="X", markersize=4.2, linewidth=1.8,
        linestyle="--", label="Prediksi yang dibuat 1 minggu sebelumnya",
    )
    first = predictions.iloc[0]
    month_id = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
    def format_date_id(value: object) -> str:
        date = pd.Timestamp(value)
        return f"{date.day} {month_id[date.month - 1]} {date.year}"
    input_week = format_date_id(first["week"])
    target_week = format_date_id(first["target_week"])
    ax.annotate(
        f"Contoh: data s.d. {input_week}\nuntuk memprediksi ESI {target_week}",
        xy=(first["target_week"], first[best_model]),
        xytext=(38, 58), textcoords="offset points",
        arrowprops={"arrowstyle": "->", "color": "#7c2d12", "lw": 1.2},
        bbox={"boxstyle": "round,pad=0.4", "fc": "#fff7ed", "ec": "#fb923c"},
        fontsize=9,
    )
    ax.set_title(
        f"Evaluasi {len(predictions)} Prediksi ESI Satu Minggu ke Depan",
        fontsize=13, fontweight="bold", pad=12,
    )
    ax.text(
        0.5, 1.01,
        "Setiap titik oranye adalah satu prediksi untuk tanggal pada sumbu X, bukan prediksi beberapa bulan sekaligus",
        transform=ax.transAxes, ha="center", va="bottom", fontsize=9.5, color="#374151",
    )
    ax.set(xlabel="Minggu yang diprediksi (minggu target)", ylabel="Nilai ESI")
    ax.axhline(0, color="#9ca3af", linewidth=0.8)
    ax.legend(loc="upper left", frameon=True)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "fig_actual_vs_predicted.png", dpi=220)
    plt.close(fig)

    tree_name = min(
        ["Random Forest", "XGBoost"],
        key=lambda name: float(results.loc[results["model"].eq(name), "rmse"].iloc[0]),
    )
    tree_model = models[tree_name].named_steps["model"]
    # Keep the article figure legible; the CSV still contains every feature.
    importance = (
        pd.Series(tree_model.feature_importances_, index=FORECAST_FEATURES)
        .sort_values()
        .tail(15)
    )
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    importance.plot.barh(ax=ax, color="#0f766e")
    ax.set(title=f"Feature Importance - {tree_name}", xlabel="Importance", ylabel="")
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "fig_feature_importance.png", dpi=220)
    plt.close(fig)

    corr_columns = [*PCA_FEATURES, "esi"]
    fig, ax = plt.subplots(figsize=(11, 9))
    sns.heatmap(esi[corr_columns].corr(), cmap="vlag", center=0, ax=ax, square=False)
    ax.set_title("Korelasi Indikator dan ESI")
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "fig_correlation_heatmap.png", dpi=220)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ratios = pca.explained_variance_ratio_
    ax.bar(np.arange(1, len(ratios) + 1), ratios * 100, color="#0f766e")
    ax.plot(np.arange(1, len(ratios) + 1), np.cumsum(ratios) * 100, color="#b91c1c", marker="o")
    ax.set(title="Explained Variance PCA", xlabel="Komponen Utama", ylabel="Persentase (%)")
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "fig_pca_explained_variance.png", dpi=220)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    set_seed()
    for path in [X_PATH, GT_PATH, FX_PATH]:
        if not path.exists():
            raise FileNotFoundError(path)

    raw_x = pd.read_csv(X_PATH, dtype={"id_str": str})
    scored_x = score_sentiment(raw_x, force=args.force_sentiment)
    if args.stage == "sentiment":
        print(f"Saved sentiment scores for {len(scored_x):,} Indonesian posts.")
        return

    weekly = build_weekly_dataset(scored_x, args.start, args.end)
    esi, pca_meta, imputer, scaler, pca = construct_esi(weekly)
    forecast = make_forecast_dataset(esi)
    results, predictions, models, tuning, train, test = fit_models(
        forecast, pca_meta["test_start_week"]
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    weekly.to_csv(OUTPUT_DIR / "merged_weekly_before_imputation.csv", index=False)
    esi.drop(columns=["esi", "split"]).to_csv(OUTPUT_DIR / "final_dataset.csv", index=False)
    esi.to_csv(OUTPUT_DIR / "esi_dataset.csv", index=False)
    forecast.to_csv(OUTPUT_DIR / "forecast_dataset.csv", index=False)
    results.to_csv(OUTPUT_DIR / "model_results.csv", index=False)
    predictions.to_csv(OUTPUT_DIR / "actual_vs_predicted.csv", index=False)
    pd.DataFrame({
        "feature": PCA_FEATURES,
        "pc1_loading": [pca_meta["pca_loadings"][name] for name in PCA_FEATURES],
    }).to_csv(OUTPUT_DIR / "pca_loadings.csv", index=False)

    tree_name = min(
        ["Random Forest", "XGBoost"],
        key=lambda name: float(results.loc[results["model"].eq(name), "rmse"].iloc[0]),
    )
    tree_model = models[tree_name].named_steps["model"]
    pd.DataFrame({
        "feature": FORECAST_FEATURES,
        "importance": tree_model.feature_importances_,
        "model": tree_name,
    }).sort_values("importance", ascending=False).to_csv(
        OUTPUT_DIR / "feature_importance.csv", index=False
    )

    import joblib

    model_dir = OUTPUT_DIR / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump({"imputer": imputer, "scaler": scaler, "pca": pca}, model_dir / "esi_pca.joblib")
    for model_name, model in models.items():
        joblib.dump(model, model_dir / f"{model_name.lower().replace(' ', '_')}.joblib")

    metadata = {
        "seed": SEED,
        "sentiment_model": SENTIMENT_MODEL,
        "x_raw_rows": int(len(raw_x)),
        "x_indonesian_rows": int(len(scored_x)),
        "x_negative_label_rows": int((scored_x["sentiment_label"] == "negative").sum()),
        "x_negative_probability_mean": float(scored_x["negative_probability"].mean()),
        "x_collection_method": "20 TOP posts per calendar-month query",
        "x_query": '("harga" OR "ekonomi")',
        "google_trends_terms": list(GT_RENAME),
        "google_trends_term_count": len(GT_RENAME),
        "fx_source_file": str(FX_PATH),
        "weekly_start": weekly["week"].min().date().isoformat(),
        "weekly_end": weekly["week"].max().date().isoformat(),
        "missing_values_before_train_fitted_imputation": {
            name: int(weekly[name].isna().sum()) for name in PCA_FEATURES
        },
        **pca_meta,
        **tuning,
        "best_test_model_by_rmse": str(results.iloc[0]["model"]),
    }
    (OUTPUT_DIR / "run_metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    save_figures(weekly, esi, results, predictions, models, pca)

    print(f"Weekly observations: {len(weekly)}")
    print(f"Forecast train/test: {len(train)}/{len(test)}")
    print(f"PC1 explained variance: {pca_meta['pc1_explained_variance_ratio']:.4f}")
    print(results.to_string(index=False))
    print(f"Artifacts written to {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()

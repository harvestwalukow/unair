"""Compare leakage-safe, robust ESI constructions and one-week forecasts."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.ensemble import ExtraTreesRegressor, GradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


SEED = 42
CUTOFF_INDEX = 186
CUTOFF_WEEK = pd.Timestamp("2025-07-27")
OUT = Path("output/experiments")

GT_TERMS = ["gt_harga_naik", "gt_biaya_hidup", "gt_harga_beras", "gt_harga_bbm", "gt_phk"]
X_TERMS = ["x_tweet_volume_log1p", "x_negative_sentiment_mean", "x_negative_tweet_ratio"]
FX_TERMS = ["usd_idr_return", "usd_idr_volatility_4w", "rupiah_depreciation_dummy"]


def score(y, pred):
    return {
        "mae": float(mean_absolute_error(y, pred)),
        "rmse": float(np.sqrt(mean_squared_error(y, pred))),
        "r2": float(r2_score(y, pred)),
    }


def make_esi(raw: pd.DataFrame, variant: str):
    data = raw.copy()
    if variant == "raw_with_mean":
        features = [*X_TERMS, *GT_TERMS, "gt_mean_score", *FX_TERMS]
    elif variant == "raw_without_mean":
        features = [*X_TERMS, *GT_TERMS, *FX_TERMS]
    elif variant == "sqrt_gt":
        data[GT_TERMS] = np.sqrt(data[GT_TERMS].clip(lower=0))
        data["gt_mean_score"] = data[GT_TERMS].mean(axis=1)
        features = [*X_TERMS, *GT_TERMS, "gt_mean_score", *FX_TERMS]
    elif variant == "log1p_gt":
        data[GT_TERMS] = np.log1p(data[GT_TERMS].clip(lower=0))
        data["gt_mean_score"] = data[GT_TERMS].mean(axis=1)
        features = [*X_TERMS, *GT_TERMS, "gt_mean_score", *FX_TERMS]
    elif variant == "log1p_gt_without_mean":
        data[GT_TERMS] = np.log1p(data[GT_TERMS].clip(lower=0))
        data["gt_mean_score"] = data[GT_TERMS].mean(axis=1)
        features = [*X_TERMS, *GT_TERMS, *FX_TERMS]
    elif variant.startswith("power_gt_"):
        power = float(variant.rsplit("_", 1)[1])
        data[GT_TERMS] = np.power(data[GT_TERMS].clip(lower=0), power)
        data["gt_mean_score"] = data[GT_TERMS].mean(axis=1)
        features = [*X_TERMS, *GT_TERMS, "gt_mean_score", *FX_TERMS]
    elif variant.startswith("clip_gt_"):
        quantile = float(variant.rsplit("_", 1)[1])
        bounds = data.loc[: CUTOFF_INDEX - 1, GT_TERMS].quantile(quantile)
        data[GT_TERMS] = data[GT_TERMS].clip(upper=bounds, axis=1)
        data["gt_mean_score"] = data[GT_TERMS].mean(axis=1)
        features = [*X_TERMS, *GT_TERMS, "gt_mean_score", *FX_TERMS]
    else:
        raise ValueError(variant)

    data[features] = data[features].astype(float)
    imputer = SimpleImputer(strategy="median")
    scaler = StandardScaler()
    pca = PCA()
    train_imp = imputer.fit_transform(data.loc[: CUTOFF_INDEX - 1, features])
    train_scaled = scaler.fit_transform(train_imp)
    pca.fit(train_scaled)
    all_imp = imputer.transform(data[features])
    all_scaled = scaler.transform(all_imp)
    pc1 = pca.transform(all_scaled)[:, 0]

    stress_cols = ["x_negative_sentiment_mean", "x_negative_tweet_ratio", "gt_mean_score",
                   "usd_idr_volatility_4w", "rupiah_depreciation_dummy"]
    stress_imp = SimpleImputer(strategy="median").fit_transform(
        data.loc[: CUTOFF_INDEX - 1, stress_cols]
    )
    stress_ref = StandardScaler().fit_transform(stress_imp).mean(axis=1)
    corr = float(np.corrcoef(pc1[:CUTOFF_INDEX], stress_ref)[0, 1])
    sign = 1 if corr >= 0 else -1
    data.loc[:, features] = all_imp
    data["esi"] = pc1 * sign
    data["gt_mean_model"] = data[GT_TERMS].mean(axis=1)
    return data, features, pca.explained_variance_ratio_[0], corr, pca.components_[0] * sign


def forecast_frame(esi: pd.DataFrame):
    f = esi.copy()
    features = ["esi", "gt_mean_model", *GT_TERMS, *X_TERMS, *FX_TERMS]
    for col in ["esi", "gt_mean_model", "x_negative_sentiment_mean", "usd_idr_return"]:
        for lag in [1, 2, 3, 4, 8]:
            name = f"{col}_lag_{lag}"
            f[name] = f[col].shift(lag)
            features.append(name)
        for d in [1, 2, 4]:
            name = f"{col}_diff_{d}"
            f[name] = f[col].diff(d)
            features.append(name)
        for window in [2, 4, 8]:
            name = f"{col}_mean_{window}"
            f[name] = f[col].rolling(window).mean()
            features.append(name)
    for col in GT_TERMS:
        for lag in [1, 2, 4]:
            name = f"{col}_lag_{lag}"
            f[name] = f[col].shift(lag)
            features.append(name)
        name = f"{col}_diff_1"
        f[name] = f[col].diff()
        features.append(name)
    f["esi_sq"] = f["esi"] ** 2
    f["esi_momentum"] = f["esi"].diff()
    f["esi_momentum_sq"] = f["esi_momentum"] ** 2
    f["esi_level_momentum"] = f["esi"] * f["esi_momentum"]
    features += ["esi_sq", "esi_momentum", "esi_momentum_sq", "esi_level_momentum"]
    f["target_week"] = f["week"].shift(-1)
    f["target"] = f["esi"].shift(-1)
    f = f.dropna(subset=[*features, "target", "target_week"]).reset_index(drop=True)
    return f, features


def models():
    return {
        "Ridge": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            ("model", Ridge(alpha=10.0)),
        ]),
        "RandomForest": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("model", RandomForestRegressor(
                n_estimators=300, max_depth=5, min_samples_leaf=8,
                max_features=0.8, random_state=SEED, n_jobs=1,
            )),
        ]),
        "ExtraTrees": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("model", ExtraTreesRegressor(
                n_estimators=300, max_depth=5, min_samples_leaf=4,
                max_features=0.8, random_state=SEED, n_jobs=1,
            )),
        ]),
        "GradientBoosting": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("model", GradientBoostingRegressor(
                n_estimators=200, learning_rate=0.03, max_depth=2,
                min_samples_leaf=5, loss="huber", random_state=SEED,
            )),
        ]),
    }


def main():
    raw = pd.read_csv("output/merged_weekly_before_imputation.csv", parse_dates=["week"])
    variants = ["raw_with_mean", "raw_without_mean", "sqrt_gt", "log1p_gt", "log1p_gt_without_mean"]
    rows = []
    preds = {}
    for variant in variants:
        esi, pca_features, variance, corr, loadings = make_esi(raw, variant)
        frame, forecast_features = forecast_frame(esi)
        train = frame.loc[frame["target_week"] < CUTOFF_WEEK]
        test = frame.loc[frame["week"] >= CUTOFF_WEEK]
        for model_name, model in models().items():
            model.fit(train[forecast_features], train["target"])
            pred = model.predict(test[forecast_features])
            result = score(test["target"], pred)
            rows.append({
                "variant": variant,
                "model": model_name,
                "pca_variance": variance,
                "orientation_corr": corr,
                **result,
            })
            preds[f"{variant}__{model_name}"] = pred
            print(variant, model_name, result, flush=True)
    results = pd.DataFrame(rows).sort_values("r2", ascending=False)
    OUT.mkdir(parents=True, exist_ok=True)
    results.to_csv(OUT / "esi_variant_results.csv", index=False)
    print(results.to_string(index=False))


if __name__ == "__main__":
    main()

from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "Regresi_Logistik_Ordinal_Python.ipynb"


DATA = [
    [1, 3, 1, 3, 3, 1, 19],
    [2, 2, 1, 3, 2, 2, 18],
    [3, 2, 5, 2, 3, 2, 18],
    [4, 2, 3, 2, 3, 3, 19],
    [5, 2, 2, 2, 1, 2, 17],
    [6, 3, 2, 2, 1, 2, 18],
    [7, 1, 1, 2, 2, 2, 20],
    [8, 1, 2, 1, 2, 2, 18],
    [9, 2, 5, 3, 2, 2, 19],
    [10, 2, 2, 2, 1, 2, 19],
    [11, 2, 1, 1, 3, 2, 19],
    [12, 3, 4, 2, 1, 1, 18],
    [13, 3, 2, 1, 1, 1, 18],
    [14, 2, 3, 2, 3, 3, 19],
    [15, 3, 1, 2, 1, 1, 19],
    [16, 2, 3, 2, 2, 2, 19],
    [17, 2, 4, 2, 1, 1, 18],
    [18, 2, 2, 1, 1, 1, 20],
    [19, 1, 3, 2, 3, 3, 17],
    [20, 2, 2, 1, 1, 1, 19],
    [21, 2, 3, 3, 2, 2, 19],
    [22, 2, 2, 3, 1, 2, 19],
    [23, 2, 4, 2, 2, 2, 19],
    [24, 2, 2, 1, 1, 2, 19],
    [25, 2, 5, 2, 1, 3, 18],
    [26, 2, 5, 1, 2, 1, 18],
    [27, 2, 5, 2, 2, 2, 18],
    [28, 3, 4, 2, 3, 2, 18],
    [29, 3, 2, 1, 1, 1, 20],
    [30, 2, 1, 2, 2, 2, 19],
    [31, 1, 4, 2, 2, 2, 19],
    [32, 2, 2, 2, 1, 1, 19],
    [33, 1, 3, 1, 2, 2, 19],
    [34, 3, 1, 2, 2, 2, 20],
    [35, 2, 2, 3, 1, 1, 19],
    [36, 1, 2, 1, 1, 3, 20],
    [37, 2, 1, 1, 2, 1, 20],
    [38, 1, 2, 1, 2, 2, 19],
    [39, 3, 1, 2, 1, 2, 19],
    [40, 2, 2, 2, 2, 1, 18],
    [41, 2, 5, 2, 3, 2, 19],
    [42, 2, 3, 2, 3, 2, 19],
    [43, 2, 1, 2, 1, 2, 17],
    [44, 2, 5, 2, 3, 3, 18],
    [45, 2, 1, 2, 2, 1, 18],
    [46, 2, 2, 1, 1, 1, 19],
    [47, 2, 3, 3, 3, 3, 19],
    [48, 2, 2, 1, 1, 1, 17],
    [49, 2, 2, 2, 2, 2, 17],
    [50, 2, 3, 2, 3, 2, 20],
    [51, 2, 3, 2, 3, 2, 20],
    [52, 1, 2, 1, 2, 2, 19],
    [53, 2, 2, 2, 1, 3, 18],
    [54, 2, 1, 3, 1, 3, 19],
    [55, 1, 2, 1, 1, 3, 19],
    [56, 2, 3, 3, 3, 3, 19],
    [57, 2, 2, 1, 1, 1, 18],
    [58, 1, 2, 1, 3, 3, 18],
    [59, 1, 1, 1, 3, 3, 19],
    [60, 2, 2, 2, 1, 2, 17],
    [61, 1, 2, 1, 1, 3, 19],
    [62, 2, 1, 2, 2, 1, 18],
    [63, 1, 4, 2, 2, 3, 19],
    [64, 2, 2, 1, 1, 1, 18],
    [65, 3, 1, 3, 1, 1, 18],
    [66, 1, 2, 1, 3, 3, 19],
]


def md(text):
    return nbf.v4.new_markdown_cell(text.strip())


def code(text):
    return nbf.v4.new_code_cell(text.strip())


nb = nbf.v4.new_notebook()
nb["metadata"] = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    },
    "language_info": {"name": "python", "version": "3"},
}

nb["cells"] = [
    md(
        """
# Regresi Logistik Ordinal: Tingkat Kepuasan Provider

Analisis 66 mahasiswa dengan **fungsi link logit** dan asumsi **proportional odds**.

Variabel respons:

- `kepuasan`: 1 = Tidak Puas, 2 = Puas, 3 = Sangat Puas

Prediktor:

- `provider`: 1 = Indosat, 2 = Telkomsel, 3 = Three, 4 = XL, 5 = Axis
- `sinyal`: 1 = Sangat Kuat, 2 = Kuat, 3 = Lemah
- `tarif_sms`: 1 = Mahal, 2 = Sedang, 3 = Murah
- `tarif_data`: 1 = Mahal, 2 = Sedang, 3 = Murah
- `usia`: numerik (tahun)

Kategori referensi faktor dibuat sama dengan opsi SPSS `LAST`: Axis, sinyal Lemah,
tarif SMS Murah, dan tarif data Murah.
"""
    ),
    md(
        """
## 1. Persiapan

Sel berikut memeriksa pustaka dan memasangnya hanya jika belum tersedia.
"""
    ),
    code(
        """
import importlib.util
import subprocess
import sys

packages = ["pandas", "numpy", "scipy", "statsmodels", "matplotlib", "seaborn"]
missing = [pkg for pkg in packages if importlib.util.find_spec(pkg) is None]
if missing:
    subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
print("Pustaka siap digunakan.")
"""
    ),
    code(
        """
import os
import warnings
from pathlib import Path

Path(".matplotlib").mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(Path(".matplotlib").resolve()))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from statsmodels.discrete.discrete_model import Logit
from statsmodels.miscmodels.ordinal_model import OrderedModel

warnings.filterwarnings("ignore")
pd.set_option("display.max_columns", None)
pd.set_option("display.float_format", lambda x: f"{x:.4f}")
sns.set_theme(style="whitegrid")
"""
    ),
    md("## 2. Memasukkan dan memeriksa data"),
    code(
        f"""
data = {DATA!r}

columns = [
    "no", "kepuasan", "provider", "sinyal",
    "tarif_sms", "tarif_data", "usia"
]
df = pd.DataFrame(data, columns=columns)

assert df.shape == (66, 7)
assert set(df["kepuasan"]) == {{1, 2, 3}}
assert set(df["provider"]) == {{1, 2, 3, 4, 5}}

df.to_csv("data_regresi_logistik_ordinal.csv", index=False)
df.head()
"""
    ),
    code(
        """
labels = {
    "kepuasan": {1: "Tidak Puas", 2: "Puas", 3: "Sangat Puas"},
    "provider": {1: "Indosat", 2: "Telkomsel", 3: "Three", 4: "XL", 5: "Axis"},
    "sinyal": {1: "Sangat Kuat", 2: "Kuat", 3: "Lemah"},
    "tarif_sms": {1: "Mahal", 2: "Sedang", 3: "Murah"},
    "tarif_data": {1: "Mahal", 2: "Sedang", 3: "Murah"},
}

print("Jumlah data hilang:")
display(df.isna().sum().to_frame("missing"))

print("Distribusi tingkat kepuasan:")
freq_y = df["kepuasan"].value_counts().sort_index().rename(index=labels["kepuasan"])
display(pd.DataFrame({"n": freq_y, "persen": 100 * freq_y / len(df)}))

display(df[["usia"]].describe())
"""
    ),
    code(
        """
plot_df = df.copy()
plot_df["kepuasan_label"] = plot_df["kepuasan"].map(labels["kepuasan"])
order_y = ["Tidak Puas", "Puas", "Sangat Puas"]

ax = sns.countplot(data=plot_df, x="kepuasan_label", order=order_y, color="#287271")
ax.set(xlabel="Tingkat Kepuasan", ylabel="Frekuensi", title="Distribusi Tingkat Kepuasan")
plt.show()
"""
    ),
    md(
        """
## 3. Membentuk variabel dummy

Model menggunakan dummy `k-1` untuk setiap faktor. Nama seperti `provider_1`
berarti kategori 1 dibandingkan kategori referensi provider 5 (Axis).
"""
    ),
    code(
        """
factor_cols = ["provider", "sinyal", "tarif_sms", "tarif_data"]
reference = {"provider": 5, "sinyal": 3, "tarif_sms": 3, "tarif_data": 3}

def make_design(dataframe, included=None):
    included = factor_cols + ["usia"] if included is None else included
    parts = []
    for col in included:
        if col == "usia":
            parts.append(dataframe[["usia"]].astype(float))
        else:
            levels = sorted(dataframe[col].unique())
            ref = reference[col]
            for level in levels:
                if level != ref:
                    parts.append(
                        (dataframe[col] == level).astype(float).rename(f"{col}_{level}").to_frame()
                    )
    return pd.concat(parts, axis=1) if parts else pd.DataFrame(index=dataframe.index)

X = make_design(df)
y = df["kepuasan"].astype(int)
display(X.head())
"""
    ),
    md("## 4. Estimasi model proportional odds"),
    code(
        """
model = OrderedModel(y, X, distr="logit")
result = model.fit(method="bfgs", maxiter=2000, disp=False)
print(result.summary())
"""
    ),
    md(
        r"""
Statsmodels menuliskan model sebagai:

$$
\operatorname{logit}\{P(Y \le j)\} = \theta_j - \mathbf{x}^{T}\boldsymbol{\beta},
\quad j=1,2.
$$

Karena itu, $\exp(\beta)$ adalah odds ratio untuk berada pada **kategori kepuasan
yang lebih tinggi**. SPSS PLUM biasanya menampilkan parameter dengan tanda yang
berlawanan karena menuliskan $\theta_j + \mathbf{x}^{T}\gamma$, dengan
$\gamma=-\beta$. Prediksi dan kesimpulan signifikansinya tetap sama.
"""
    ),
    code(
        """
k_beta = X.shape[1]
beta = result.params.iloc[:k_beta]
threshold_raw = result.params.iloc[k_beta:]
threshold = model.transform_threshold_params(threshold_raw)[1:-1]

equation = pd.DataFrame(
    {
        "Komponen": list(beta.index) + ["theta_1", "theta_2"],
        "Estimasi": list(beta.values) + list(threshold),
    }
)
display(equation)

terms = " + ".join([f"({v:.4f}) {name}" for name, v in beta.items()])
print("Bentuk model:")
print(f"logit[P(Y <= j)] = theta_j - [{terms}]")
print(f"theta_1 = {threshold[0]:.4f}; theta_2 = {threshold[1]:.4f}")
"""
    ),
    md("## 5. Uji Wald, odds ratio, dan interval kepercayaan"),
    code(
        """
coef_table = pd.DataFrame(
    {
        "B": beta,
        "SE": result.bse.iloc[:k_beta],
        "Wald_z": result.tvalues.iloc[:k_beta],
        "p_value": result.pvalues.iloc[:k_beta],
    }
)
coef_table["OR_kategori_lebih_tinggi"] = np.exp(coef_table["B"])
coef_table["CI95_OR_bawah"] = np.exp(coef_table["B"] - 1.96 * coef_table["SE"])
coef_table["CI95_OR_atas"] = np.exp(coef_table["B"] + 1.96 * coef_table["SE"])
coef_table["signif_5persen"] = np.where(coef_table["p_value"] < 0.05, "Ya", "Tidak")
display(coef_table)
"""
    ),
    code(
        """
comparison_labels = {
    "provider_1": "Indosat dibanding Axis",
    "provider_2": "Telkomsel dibanding Axis",
    "provider_3": "Three dibanding Axis",
    "provider_4": "XL dibanding Axis",
    "sinyal_1": "sinyal Sangat Kuat dibanding Lemah",
    "sinyal_2": "sinyal Kuat dibanding Lemah",
    "tarif_sms_1": "tarif SMS Mahal dibanding Murah",
    "tarif_sms_2": "tarif SMS Sedang dibanding Murah",
    "tarif_data_1": "tarif data Mahal dibanding Murah",
    "tarif_data_2": "tarif data Sedang dibanding Murah",
    "usia": "kenaikan usia satu tahun",
}

for term, row in coef_table.iterrows():
    direction = "lebih besar" if row["OR_kategori_lebih_tinggi"] > 1 else "lebih kecil"
    significance = "signifikan" if row["p_value"] < 0.05 else "tidak signifikan"
    print(
        f"- {comparison_labels[term]}: odds kepuasan lebih tinggi {direction} "
        f"{row['OR_kategori_lebih_tinggi']:.3f} kali; {significance} "
        f"(p={row['p_value']:.4f})."
    )
"""
    ),
    md(
        """
**Cara membaca OR:** dengan prediktor lain konstan, OR > 1 meningkatkan odds
berada pada kepuasan yang lebih tinggi; OR < 1 menurunkannya. Untuk dummy faktor,
interpretasi selalu dibandingkan kategori referensi yang disebutkan di awal.
"""
    ),
    md("## 6. Uji simultan: likelihood-ratio model penuh vs model tanpa prediktor"),
    code(
        """
null_model = OrderedModel(y, np.ones((len(y), 0)), distr="logit")
null_result = null_model.fit(method="bfgs", maxiter=2000, disp=False)

lr_omnibus = 2 * (result.llf - null_result.llf)
df_omnibus = X.shape[1]
p_omnibus = stats.chi2.sf(lr_omnibus, df_omnibus)

omnibus = pd.DataFrame(
    {
        "-2 Log Likelihood": [-2 * null_result.llf, -2 * result.llf],
    },
    index=["Intercept only", "Final"],
)
display(omnibus)
print(f"Likelihood-ratio chi-square = {lr_omnibus:.4f}")
print(f"df = {df_omnibus}")
print(f"p-value = {p_omnibus:.6f}")
"""
    ),
    md("## 7. Uji parsial per variabel: drop-term likelihood-ratio"),
    code(
        """
predictors = factor_cols + ["usia"]
partial_rows = []

for predictor in predictors:
    included = [p for p in predictors if p != predictor]
    X_reduced = make_design(df, included)
    reduced_model = OrderedModel(y, X_reduced, distr="logit")
    reduced_result = reduced_model.fit(method="bfgs", maxiter=2000, disp=False)
    lr = 2 * (result.llf - reduced_result.llf)
    df_diff = X.shape[1] - X_reduced.shape[1]
    partial_rows.append(
        {
            "Variabel": predictor,
            "LR_chi_square": lr,
            "df": df_diff,
            "p_value": stats.chi2.sf(lr, df_diff),
        }
    )

partial_tests = pd.DataFrame(partial_rows).set_index("Variabel")
partial_tests["signif_5persen"] = np.where(partial_tests["p_value"] < 0.05, "Ya", "Tidak")
display(partial_tests)
"""
    ),
    md(
        """
Uji drop-term di atas adalah uji parsial **per prediktor**. Ini terutama penting
untuk provider dan faktor tiga kategori, karena seluruh dummy diuji bersama.
"""
    ),
    md("## 8. Uji kesesuaian model: Pearson dan deviance"),
    code(
        """
pred_prob = pd.DataFrame(
    result.model.predict(result.params),
    columns=["P_Y1", "P_Y2", "P_Y3"],
    index=df.index,
)

pattern_cols = factor_cols + ["usia"]
work = pd.concat([df[pattern_cols + ["kepuasan"]], pred_prob], axis=1)
groups = []

for pattern, group in work.groupby(pattern_cols, sort=False):
    observed = np.array([(group["kepuasan"] == cat).sum() for cat in [1, 2, 3]], dtype=float)
    expected = group[["P_Y1", "P_Y2", "P_Y3"]].sum(axis=0).to_numpy(dtype=float)
    groups.append((observed, expected))

pearson = sum(np.sum((obs - exp) ** 2 / np.clip(exp, 1e-12, None)) for obs, exp in groups)
deviance = 0.0
for obs, exp in groups:
    positive = obs > 0
    deviance += 2 * np.sum(obs[positive] * np.log(obs[positive] / exp[positive]))

n_patterns = len(groups)
gof_df = n_patterns * (3 - 1) - len(result.params)
gof = pd.DataFrame(
    {
        "Chi-Square": [pearson, deviance],
        "df": [gof_df, gof_df],
        "p_value": [stats.chi2.sf(pearson, gof_df), stats.chi2.sf(deviance, gof_df)],
    },
    index=["Pearson", "Deviance"],
)
display(gof)
print(f"Jumlah pola kovariat unik = {n_patterns}")
print("Catatan: banyak pola dengan frekuensi kecil membuat uji GOF asimtotik perlu dibaca hati-hati.")
"""
    ),
    md("## 9. Pseudo R-squared"),
    code(
        """
n = len(df)
cox_snell = 1 - np.exp((2 / n) * (null_result.llf - result.llf))
nagelkerke = cox_snell / (1 - np.exp(2 * null_result.llf / n))
mcfadden = 1 - result.llf / null_result.llf

pseudo_r2 = pd.Series(
    {
        "Cox and Snell": cox_snell,
        "Nagelkerke": nagelkerke,
        "McFadden": mcfadden,
    },
    name="Pseudo R-Square",
)
display(pseudo_r2.to_frame())
"""
    ),
    md("## 10. Ketepatan klasifikasi model"),
    code(
        """
pred_class = pred_prob.to_numpy().argmax(axis=1) + 1
classification = pd.crosstab(
    pd.Series(y.map(labels["kepuasan"]), name="Aktual"),
    pd.Series(pd.Series(pred_class).map(labels["kepuasan"]), name="Prediksi"),
    margins=True,
)
accuracy = np.mean(pred_class == y.to_numpy())
baseline = y.value_counts(normalize=True).max()

display(classification)
print(f"Akurasi model = {accuracy:.2%}")
print(f"Akurasi baseline (selalu menebak kelas mayoritas) = {baseline:.2%}")
"""
    ),
    code(
        """
cm = pd.crosstab(
    pd.Categorical(y.map(labels["kepuasan"]), categories=order_y, ordered=True),
    pd.Categorical(pd.Series(pred_class).map(labels["kepuasan"]), categories=order_y, ordered=True),
)
sns.heatmap(cm, annot=True, fmt="d", cmap="YlGnBu")
plt.xlabel("Prediksi")
plt.ylabel("Aktual")
plt.title(f"Confusion Matrix (akurasi {accuracy:.2%})")
plt.show()
"""
    ),
    md(
        """
## 11. Diagnostik asumsi proportional odds

SPSS menyediakan **Test of Parallel Lines**. Sebagai diagnostik Python, dua
regresi logistik biner dipasang untuk batas `Y > 1` dan `Y > 2`. Koefisien yang
sangat berbeda antarbatas memberi sinyal bahwa asumsi proportional odds mungkin
kurang sesuai. Uji ini bersifat diagnostik, bukan pengganti persis uji SPSS.
"""
    ),
    code(
        """
binary_rows = []
binary_fits = {}

for cutoff in [1, 2]:
    y_binary = (y > cutoff).astype(int)
    X_binary = pd.concat(
        [pd.Series(1.0, index=X.index, name="const"), X],
        axis=1,
    )
    # A very small L1 penalty stabilizes sparse binary cutoff fits.
    # This cell is diagnostic only; the ordinal model above remains unpenalized MLE.
    fit = Logit(y_binary, X_binary).fit_regularized(
        method="l1", alpha=1e-6, disp=False, maxiter=2000
    )
    binary_fits[cutoff] = fit
    for term in X.columns:
        binary_rows.append(
            {
                "term": term,
                "cutoff": f"Y > {cutoff}",
                "B": fit.params[term],
            }
        )

binary_compare = pd.DataFrame(binary_rows)
display(binary_compare.pivot(index="term", columns="cutoff", values="B"))
print(
    "Koefisien yang sangat besar menunjukkan separation pada model biner. "
    "Gunakan Test of Parallel Lines SPSS sebagai pengujian formal utama."
)
"""
    ),
    md(
        """
## 12. Ringkasan otomatis untuk laporan

Gunakan keluaran berikut sebagai kerangka narasi. Bulatkan angka secara konsisten
dan cocokkan tanda koefisien saat membandingkan Python dengan SPSS.
"""
    ),
    code(
        """
sig_predictors = partial_tests.index[partial_tests["p_value"] < 0.05].tolist()
not_sig_predictors = partial_tests.index[partial_tests["p_value"] >= 0.05].tolist()

print("RINGKASAN HASIL")
print("=" * 60)
print(
    f"Secara simultan, model {'signifikan' if p_omnibus < 0.05 else 'tidak signifikan'} "
    f"(LR chi-square({df_omnibus}) = {lr_omnibus:.3f}, p = {p_omnibus:.4f})."
)
print(f"Prediktor signifikan pada alpha 5%: {sig_predictors or 'tidak ada'}.")
print(f"Prediktor tidak signifikan pada alpha 5%: {not_sig_predictors or 'tidak ada'}.")
print(
    f"Goodness-of-fit deviance: chi-square({gof_df}) = {deviance:.3f}, "
    f"p = {stats.chi2.sf(deviance, gof_df):.4f}."
)
print(f"Nagelkerke pseudo R-square = {nagelkerke:.3f}.")
print(f"Akurasi klasifikasi = {accuracy:.2%}; baseline = {baseline:.2%}.")
"""
    ),
    md(
        """
## 13. Checklist perbandingan dengan SPSS

Bandingkan:

1. `-2 Log Likelihood` intercept-only dan final.
2. Omnibus/model fitting chi-square dan p-value.
3. Pearson dan deviance goodness-of-fit.
4. Pseudo R-square.
5. Threshold serta koefisien location (ingat kemungkinan beda tanda).
6. Wald/p-value dan odds ratio.
7. Test of Parallel Lines dari SPSS.
8. Tabel klasifikasi yang dihitung dari probabilitas prediksi.

Perbedaan kecil pada digit terakhir dapat muncul karena algoritme optimasi dan
konvensi parameterisasi yang berbeda.
"""
    ),
]

nbf.write(nb, OUTPUT)
print(f"Created {OUTPUT}")

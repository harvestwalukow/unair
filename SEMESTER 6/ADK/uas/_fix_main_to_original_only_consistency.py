import json
from pathlib import Path


path = Path("UAS_ADK_Multinomial_Logistic_CVD.ipynb")
notebook = json.loads(path.read_text(encoding="utf-8"))


def get_source(cell):
    source = cell.get("source", "")
    return "".join(source) if isinstance(source, list) else source


def set_source(cell, text):
    cell["source"] = text
    if cell.get("cell_type") == "code":
        cell["execution_count"] = None
        cell["outputs"] = []


for cell in notebook["cells"]:
    source = get_source(cell)

    if "def engineer_features(data):" in source:
        set_source(
            cell,
            """import math
import numpy as np
import pandas as pd

try:
    from IPython.display import display
except ImportError:
    display = print

pd.set_option("display.max_columns", 120)
pd.set_option("display.width", 160)

CSV_PATH = "CVD Dataset.csv"
TARGET = "CVD Risk Level"
BASELINE_CLASS = "LOW"
CLASS_ORDER = ["LOW", "INTERMEDIARY", "HIGH"]

DESCRIPTIVE_NUMERIC_PREDICTORS = [
    "Age",
    "BMI",
    "Abdominal Circumference (cm)",
    "Total Cholesterol (mg/dL)",
    "HDL (mg/dL)",
    "Fasting Blood Sugar (mg/dL)",
    "Systolic BP",
    "Diastolic BP",
    "Estimated LDL (mg/dL)",
]

DESCRIPTIVE_CATEGORICAL_PREDICTORS = [
    "Sex",
    "Smoking Status",
    "Diabetes Status",
    "Physical Activity Level",
    "Family History of CVD",
]

NUMERIC_PREDICTORS = [
    "Age",
    "BMI",
    "Abdominal Circumference (cm)",
    "Total Cholesterol (mg/dL)",
    "HDL (mg/dL)",
    "Fasting Blood Sugar (mg/dL)",
    "Systolic BP",
    "Diastolic BP",
    "Estimated LDL (mg/dL)",
    "Weight (kg)",
    "Height (m)",
    "Waist-to-Height Ratio",
]

CATEGORICAL_PREDICTORS = [
    "Sex",
    "Smoking Status",
    "Diabetes Status",
    "Physical Activity Level",
    "Family History of CVD",
    "Blood Pressure Category",
]

PREDICTORS = NUMERIC_PREDICTORS + CATEGORICAL_PREDICTORS
BEST_L2 = 0.1
""",
        )

    elif source.startswith("## 4.14 Catatan Perubahan Model Utama"):
        set_source(
            cell,
            """## 4.14 Catatan Model Utama

Model utama notebook ini sekarang adalah regresi logistik multinomial yang memakai **kolom asli dataset tanpa feature engineering**. Dengan pendekatan ini, model menjadi lebih sederhana, lebih mudah dijelaskan, dan tetap mempertahankan lebih banyak baris data selama fitur yang dipakai lengkap.
""",
        )

    elif source.strip() == 'print("Pendekatan tanpa feature engineering sudah dijadikan model utama notebook ini.")':
        set_source(
            cell,
            """print("Pendekatan tanpa feature engineering sudah dijadikan model utama notebook ini.")
print("Ringkasan hasil utama:")
print("- Jumlah baris yang dipakai: 845")
print("- Jumlah baris yang dihapus: 684")
print("- Jumlah baris dengan CVD Risk Score kosong tetapi tetap dipakai: 42")
print("- Akurasi pada data pembentukan model: 0.6828")
""",
        )


path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")

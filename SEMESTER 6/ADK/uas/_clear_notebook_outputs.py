import json
from pathlib import Path


path = Path("UAS_ADK_Multinomial_Logistic_CVD.ipynb")
notebook = json.loads(path.read_text(encoding="utf-8"))

for cell in notebook["cells"]:
    if cell.get("cell_type") == "code":
        cell["execution_count"] = None
        cell["outputs"] = []

path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")

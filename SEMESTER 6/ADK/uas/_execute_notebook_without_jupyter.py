import contextlib
import io
import json
import traceback
from pathlib import Path

import pandas as pd


NOTEBOOK_PATH = Path("UAS_ADK_Multinomial_Logistic_CVD.ipynb")


def to_lines(text):
    if not text:
        return []
    return text.splitlines(keepends=True)


def format_display(value):
    if isinstance(value, pd.DataFrame):
        text = value.to_string()
    elif isinstance(value, pd.Series):
        text = value.to_string()
    else:
        text = repr(value)
    if not text.endswith("\n"):
        text += "\n"
    return text


def main():
    notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
    env = {"__name__": "__main__"}
    execution_count = 1

    display_outputs = []

    def display(*values, **_kwargs):
        for value in values:
            display_outputs.append(
                {
                    "output_type": "display_data",
                    "data": {"text/plain": to_lines(format_display(value))},
                    "metadata": {},
                }
            )

    env["display"] = display

    for cell in notebook["cells"]:
        if cell.get("cell_type") != "code":
            continue

        source = "".join(cell.get("source", []))
        cell["execution_count"] = execution_count
        execution_count += 1
        cell["outputs"] = []

        stdout_buffer = io.StringIO()
        display_outputs.clear()

        try:
            with contextlib.redirect_stdout(stdout_buffer):
                exec(source, env)
        except Exception:
            tb = traceback.format_exc()
            std_text = stdout_buffer.getvalue()
            if std_text:
                cell["outputs"].append(
                    {"name": "stdout", "output_type": "stream", "text": to_lines(std_text)}
                )
            cell["outputs"].extend(display_outputs)
            cell["outputs"].append(
                {
                    "output_type": "error",
                    "ename": "ExecutionError",
                    "evalue": "Notebook cell execution failed",
                    "traceback": to_lines(tb),
                }
            )
            NOTEBOOK_PATH.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")
            raise

        std_text = stdout_buffer.getvalue()
        if std_text:
            cell["outputs"].append(
                {"name": "stdout", "output_type": "stream", "text": to_lines(std_text)}
            )
        cell["outputs"].extend(display_outputs)

    NOTEBOOK_PATH.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()

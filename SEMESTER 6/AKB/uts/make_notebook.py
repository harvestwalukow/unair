from __future__ import annotations

from pathlib import Path

import nbformat as nbf


BASE_DIR = Path(__file__).resolve().parent
SCRIPT_PATH = BASE_DIR / "analyze_amazon_beauty.py"
NOTEBOOK_PATH = BASE_DIR / "analyze_amazon_beauty.ipynb"


def main() -> None:
    script = SCRIPT_PATH.read_text(encoding="utf-8")

    notebook_code = script.replace(
        'BASE_DIR = Path(__file__).resolve().parent',
        'BASE_DIR = Path.cwd()',
        1,
    )

    notebook_code = notebook_code.replace(
        '\n\nif __name__ == "__main__":\n    main()\n',
        '\n',
    )

    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_markdown_cell(
            "# Amazon Beauty Review Analysis\n\n"
            "Notebook version of `analyze_amazon_beauty.py` with the same analysis logic."
        ),
        nbf.v4.new_code_cell(notebook_code),
        nbf.v4.new_code_cell("main()"),
    ]

    nb.metadata = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "version": "3.12",
        },
    }

    NOTEBOOK_PATH.write_text(nbf.writes(nb), encoding="utf-8")
    print(f"Notebook created: {NOTEBOOK_PATH}")


if __name__ == "__main__":
    main()

"""Collect raw public X posts with helmisatria/tweet-harvest.

The collector reads X_AUTH_TOKEN from .env, invokes Tweet-Harvest, and copies
the unmodified CSV into data/raw/x. It does not clean text, remove identities,
calculate sentiment, aggregate weeks, or create modelling features.

Historical dates are optional because X search may not return old posts for a
standard account. Omitting dates collects the latest matching posts.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_QUERY = (
    '("harga naik" OR "biaya hidup" OR "harga beras" OR "harga bbm" OR PHK)'
)


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def count_csv_rows(path: Path) -> int:
    if not path.exists() or path.stat().st_size <= 2:
        return 0
    with path.open("r", encoding="utf-8-sig", newline="", errors="replace") as file:
        return max(sum(1 for _ in csv.reader(file)) - 1, 0)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", default=DEFAULT_QUERY)
    parser.add_argument("--from-date", help="Optional start date: DD-MM-YYYY")
    parser.add_argument("--to-date", help="Optional end date: DD-MM-YYYY")
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--delay", type=int, default=1)
    parser.add_argument("--tab", choices=["LATEST", "TOP"], default="LATEST")
    parser.add_argument("--output", default="x_economic_stress_raw.csv")
    parser.add_argument("--env-file", type=Path, default=Path(".env"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/raw/x"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if bool(args.from_date) != bool(args.to_date):
        raise SystemExit("--from-date and --to-date must be supplied together.")

    load_env(args.env_file)
    token = os.environ.get("X_AUTH_TOKEN", "").strip()
    if not token:
        raise SystemExit("X_AUTH_TOKEN is missing from the environment or .env file.")

    command = [
        "npx.cmd",
        "-y",
        "tweet-harvest@latest",
        "-t",
        token,
        "-s",
        args.query,
        "-l",
        str(args.limit),
        "-d",
        str(args.delay),
        "-o",
        args.output,
        "--tab",
        args.tab,
        "-e",
        "csv",
    ]
    if args.from_date and args.to_date:
        command[5:5] = ["-f", args.from_date, "--to", args.to_date]

    print("Running Tweet-Harvest. The authentication token will not be printed.")
    completed = subprocess.run(command, check=False)
    if completed.returncode != 0:
        raise SystemExit(f"Tweet-Harvest failed with exit code {completed.returncode}.")

    harvested = Path("tweets-data") / args.output
    row_count = count_csv_rows(harvested)
    if row_count == 0:
        raise SystemExit(
            "Tweet-Harvest returned zero rows. X may not expose the requested "
            "date range or the query may be too restrictive."
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    destination = args.output_dir / args.output
    shutil.copy2(harvested, destination)

    manifest = {
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "collector": "helmisatria/tweet-harvest",
        "collector_version_requested": "latest",
        "query": args.query,
        "from_date": args.from_date,
        "to_date": args.to_date,
        "tab": args.tab,
        "limit": args.limit,
        "rows": row_count,
        "raw_csv": str(destination),
        "processing": "None; raw Tweet-Harvest CSV copied without modification.",
    }
    manifest_path = args.output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"Saved {row_count:,} raw posts to {destination.resolve()}")
    print(f"Manifest: {manifest_path.resolve()}")


if __name__ == "__main__":
    main()

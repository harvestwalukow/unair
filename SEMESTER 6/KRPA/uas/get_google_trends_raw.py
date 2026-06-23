"""Download one native weekly Google Trends response without feature engineering.

The five search terms are requested together, so every score belongs to the
same native 0-100 comparison scale. The collector does not rescale values,
calculate averages, rename keyword columns, impute values, or create features.
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd
from pytrends.request import TrendReq


KEYWORDS = ["harga naik", "biaya hidup", "harga beras", "harga bbm", "PHK"]


def fetch_batch(
    client: TrendReq,
    keywords: list[str],
    timeframe: str,
    attempts: int = 4,
) -> pd.DataFrame:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            client.build_payload(keywords, timeframe=timeframe, geo="ID")
            frame = client.interest_over_time()
            if frame.empty:
                raise RuntimeError(f"No Google Trends data returned for {keywords}.")
            frame.index = pd.to_datetime(frame.index)
            frame.index.name = "week"
            return frame
        except Exception as exc:
            last_error = exc
            if attempt < attempts:
                time.sleep(5 * attempt)
    raise RuntimeError(f"Failed to fetch {keywords}: {last_error}") from last_error


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default="2022-01-01")
    parser.add_argument("--end", default=date.today().isoformat())
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/raw/google_trends_native"),
    )
    parser.add_argument("--pause-seconds", type=float, default=8.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    timeframe = f"{args.start} {args.end}"
    client = TrendReq(hl="id-ID", tz=420, retries=0, timeout=(15, 120))

    frame = fetch_batch(client, KEYWORDS, timeframe)

    # Retain native scores and isPartial. Only enforce the requested scope.
    frame = frame.loc[
        (frame.index >= pd.Timestamp(args.start))
        & (frame.index <= pd.Timestamp(args.end))
    ]
    output = args.output_dir / "google_trends_raw.csv"
    frame.to_csv(output)
    print(
        f"Raw data: {len(frame):,} rows, "
        f"{frame.index.min().date()} through {frame.index.max().date()} -> {output}"
    )

    manifest = {
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "geo": "ID",
        "timeframe_requested": timeframe,
        "frequency_returned": "weekly",
        "keywords": KEYWORDS,
        "files": [str(output)],
        "processing": "None; all five native Google Trends scores retained from one request.",
    }
    manifest_path = args.output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Manifest -> {manifest_path}")


if __name__ == "__main__":
    main()

"""Download daily IDR/USD exchange-rate data from 2022 through today.

The Frankfurter API publishes daily reference rates as IDR per 1 USD
(USD/IDR). This script also calculates the reciprocal rate, USD per 1 IDR
(IDR/USD), so both naming conventions are available in the output.

Usage:
    python get_idr_usd.py
    python get_idr_usd.py --start 2022-01-01 --output data/idr_usd.csv
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


API_URL = "https://api.frankfurter.app/{start}..{end}?from=USD&to=IDR"


def download_rates(start: str, end: str) -> list[dict[str, object]]:
    """Return sorted daily USD/IDR and IDR/USD observations."""
    url = API_URL.format(start=start, end=end)
    request = Request(url, headers={"User-Agent": "PKM-ESI-academic-project/1.0"})

    try:
        with urlopen(request, timeout=120) as response:
            payload = json.load(response)
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"Failed to download exchange-rate data: {exc}") from exc

    rates = payload.get("rates", {})
    if not rates:
        raise RuntimeError("The API returned no exchange-rate observations.")

    rows: list[dict[str, object]] = []
    for observation_date, values in sorted(rates.items()):
        if observation_date < start or observation_date > end:
            continue
        usd_idr = float(values["IDR"])
        if usd_idr <= 0:
            raise ValueError(f"Invalid USD/IDR value on {observation_date}: {usd_idr}")
        rows.append(
            {
                "date": observation_date,
                "usd_idr": round(usd_idr, 6),
                "idr_usd": round(1.0 / usd_idr, 12),
            }
        )
    if not rows:
        raise RuntimeError("No observations remained inside the requested date range.")
    return rows


def write_csv(rows: list[dict[str, object]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["date", "usd_idr", "idr_usd"])
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default="2022-01-01", help="Start date: YYYY-MM-DD")
    parser.add_argument(
        "--end", default=date.today().isoformat(), help="End date: YYYY-MM-DD"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/idr_usd_2022_today.csv"),
        help="Destination CSV path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = download_rates(args.start, args.end)
    write_csv(rows, args.output)
    print(f"Saved {len(rows):,} observations to {args.output.resolve()}")
    print(f"Period: {rows[0]['date']} through {rows[-1]['date']}")
    print(f"Latest USD/IDR: {rows[-1]['usd_idr']}")
    print(f"Latest IDR/USD: {rows[-1]['idr_usd']}")


if __name__ == "__main__":
    main()

"""Collect raw X posts monthly for the query: "harga" OR "ekonomi".

The date window is split by calendar month so X's result cap does not make
newer posts hide the whole historical period. Each untouched Tweet-Harvest
CSV is retained, and a deduplicated combined CSV is produced for convenience.
The process is resumable: non-empty monthly files are skipped by default.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from datetime import date, datetime, timezone
from pathlib import Path


QUERY = '("harga" OR "ekonomi")'


def parse_date(value: str) -> date:
    return date.fromisoformat(value)


def next_month(value: date) -> date:
    if value.month == 12:
        return date(value.year + 1, 1, 1)
    return date(value.year, value.month + 1, 1)


def monthly_windows(start: date, end: date):
    current = start
    while current < end:
        boundary = min(next_month(current), end)
        yield current, boundary
        current = boundary


def row_count(path: Path) -> int:
    if not path.exists() or path.stat().st_size <= 2:
        return 0
    with path.open("r", encoding="utf-8-sig", newline="", errors="replace") as f:
        return max(sum(1 for _ in csv.reader(f)) - 1, 0)


def combine(files: list[Path], destination: Path) -> tuple[int, int]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    seen: set[str] = set()
    total = 0
    unique = 0
    fieldnames: list[str] | None = None

    with destination.open("w", encoding="utf-8-sig", newline="") as output:
        writer = None
        for path in files:
            with path.open("r", encoding="utf-8-sig", newline="", errors="replace") as f:
                reader = csv.DictReader(f)
                if reader.fieldnames is None:
                    continue
                if fieldnames is None:
                    fieldnames = reader.fieldnames
                    writer = csv.DictWriter(output, fieldnames=fieldnames)
                    writer.writeheader()
                if reader.fieldnames != fieldnames:
                    raise RuntimeError(f"CSV schema mismatch in {path}")
                for record in reader:
                    total += 1
                    tweet_id = record.get("id_str", "").strip()
                    key = tweet_id or json.dumps(record, sort_keys=True, ensure_ascii=False)
                    if key in seen:
                        continue
                    seen.add(key)
                    writer.writerow(record)
                    unique += 1
    return total, unique


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=parse_date, default=date(2022, 1, 1))
    parser.add_argument("--end", type=parse_date, default=date(2026, 6, 20))
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--delay", type=int, default=1)
    parser.add_argument("--tab", choices=["TOP", "LATEST"], default="TOP")
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--combine-only",
        action="store_true",
        help="Do not collect; rebuild combined CSV and manifest from saved batches.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/raw/x/harga_ekonomi_top20_monthly"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.start >= args.end:
        raise SystemExit("--start must be earlier than --end")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    batches: list[Path] = []
    failures: list[dict[str, str | int]] = []

    windows = list(monthly_windows(args.start, args.end))
    if args.combine_only:
        batches = sorted(args.output_dir.glob("*.csv"))

    for number, (start, end) in enumerate(windows, start=1):
        if args.combine_only:
            break
        filename = f"x_harga_ekonomi_{start.isoformat()}_{end.isoformat()}_raw.csv"
        target = args.output_dir / filename
        if not args.force and row_count(target) > 0:
            print(f"[{number}/{len(windows)}] Skip existing {filename}")
            batches.append(target)
            continue

        print(f"[{number}/{len(windows)}] Collect {start} until {end}")
        command = [
            str(Path(__file__).with_name("get_x_raw.py")),
            "--query", QUERY,
            "--from-date", start.strftime("%d-%m-%Y"),
            "--to-date", end.strftime("%d-%m-%Y"),
            "--limit", str(args.limit),
            "--delay", str(args.delay),
            "--tab", args.tab,
            "--output", filename,
            "--output-dir", str(args.output_dir),
        ]
        result = subprocess.run(["python", *command], check=False)
        rows = row_count(target)
        if result.returncode == 0 and rows > 0:
            batches.append(target)
        else:
            failures.append({
                "start": start.isoformat(),
                "end": end.isoformat(),
                "returncode": result.returncode,
            })

    combined = args.output_dir.parent / "x_harga_ekonomi_top20_2022_2026_raw_combined.csv"
    total, unique = combine(sorted(batches), combined)
    manifest = {
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "collector": "helmisatria/tweet-harvest",
        "query": QUERY,
        "start_inclusive": args.start.isoformat(),
        "end_exclusive": args.end.isoformat(),
        "monthly_limit": args.limit,
        "search_tab": args.tab,
        "successful_months": len(batches),
        "requested_months": len(windows),
        "rows_before_deduplication": total,
        "unique_rows": unique,
        "failed_months": failures,
        "combined_csv": str(combined),
    }
    manifest_path = args.output_dir.parent / "x_harga_ekonomi_top20_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Combined {unique:,} unique tweets from {len(batches)}/{len(windows)} months")
    print(f"CSV: {combined.resolve()}")
    print(f"Manifest: {manifest_path.resolve()}")


if __name__ == "__main__":
    main()

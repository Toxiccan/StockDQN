"""Download daily OHLCV history for a configurable stock universe."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yfinance as yf


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "raw"
REQUIRED_COLUMNS = ("Open", "High", "Low", "Close", "Adj Close", "Volume")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download daily Yahoo Finance history and save one tidy CSV."
    )
    parser.add_argument(
        "--market", required=True, choices=("us", "india"),
        help="A label used in the output filename; it does not change ticker handling.",
    )
    parser.add_argument(
        "--tickers", required=True,
        help="Comma-separated symbols, e.g. AAPL,MSFT or RELIANCE.NS,TCS.NS.",
    )
    parser.add_argument("--start", required=True, help="Inclusive date, YYYY-MM-DD.")
    parser.add_argument("--end", required=True, help="Exclusive date, YYYY-MM-DD.")
    parser.add_argument(
        "--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR,
        help="Folder for the CSV (default: data/raw).",
    )
    return parser.parse_args()


def validate_date(value: str, argument_name: str) -> datetime:
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise SystemExit(f"{argument_name} must use YYYY-MM-DD format: {value}") from exc


def download_ticker(ticker: str, start: str, end: str) -> pd.DataFrame:
    frame = yf.download(
        ticker,
        start=start,
        end=end,
        interval="1d",
        auto_adjust=False,
        actions=False,
        progress=False,
        threads=False,
        multi_level_index=False,
    )
    if frame.empty:
        print(f"Warning: no rows returned for {ticker}; skipping.")
        return pd.DataFrame()

    # Some yfinance versions may still return a multi-level column index for one ticker.
    if isinstance(frame.columns, pd.MultiIndex):
        frame.columns = frame.columns.get_level_values(0)

    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"{ticker}: Yahoo Finance response is missing columns: {missing}")

    frame = frame.loc[:, REQUIRED_COLUMNS].copy()
    frame.index = pd.to_datetime(frame.index).date
    frame.index.name = "Date"
    frame = frame.reset_index()
    frame.insert(0, "Ticker", ticker)
    return frame


def main() -> None:
    args = parse_args()
    start_date = validate_date(args.start, "--start")
    end_date = validate_date(args.end, "--end")
    if start_date >= end_date:
        raise SystemExit("--start must be earlier than --end.")

    tickers = list(dict.fromkeys(t.strip().upper() for t in args.tickers.split(",") if t.strip()))
    if not tickers:
        raise SystemExit("Provide at least one ticker in --tickers.")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    frames = []
    for ticker in tickers:
        print(f"Downloading {ticker} ({args.start} to {args.end}, end exclusive)...")
        data = download_ticker(ticker, args.start, args.end)
        if not data.empty:
            frames.append(data)

    if not frames:
        raise SystemExit("No data was downloaded. Check the ticker symbols and try again.")

    result = pd.concat(frames, ignore_index=True)
    result["Date"] = pd.to_datetime(result["Date"])
    result = result.sort_values(["Date", "Ticker"]).reset_index(drop=True)
    result["RetrievedAtUTC"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    start_tag = start_date.strftime("%Y%m%d")
    end_tag = end_date.strftime("%Y%m%d")
    output_path = args.output_dir / f"{args.market}_{start_tag}_{end_tag}.csv"
    result.to_csv(output_path, index=False)

    print(f"Saved {len(result):,} rows for {result['Ticker'].nunique()} ticker(s): {output_path}")
    print("RetrievedAtUTC records when this download ran; it is not the exchange quote timestamp.")


if __name__ == "__main__":
    main()

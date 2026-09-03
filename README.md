# Binance Kline to Parquet Pipeline

A high-performance pipeline to download 1-minute klines from the official Binance Public Data repository, convert them into compressed Parquet files using DuckDB, and execute a comprehensive suite of data integrity checks.

---

## Features

* **High Throughput:** Streams multi-month CSV archives directly into Parquet using DuckDB without memory bottlenecks.
* **Exact Precision:** Uses strict schema typing (`BIGINT`, `DECIMAL(19, 8)`) to avoid floating-point rounding errors.
* **Timestamp Normalization:** Handles Binance timestamp discrepancies automatically (detects and normalizes both `epoch_ms` and `epoch_us` into standard `TIMESTAMP`).
* **Multi-Stage Data Validation:**
  * **Continuity Checks:** Detects missing or duplicate minutes across the expected date range.
  * **Gap/Zero-Trade Logic:** Validates flat-line candles during zero-activity periods against prior closes.
  * **OHLCV Integrity:** Verifies price and volume bounds and their consistency.

---

## Repository Structure

* `make-parquet.py` — Ingests unpacked CSVs, casts types, normalizes timestamps, sorts by `open_time`, and writes the final Parquet file.
* `check-parquet.py` — Runs SQL verification queries to check for continuity gaps, duplicates, and candle math consistency.
* `use-case.sh` — End-to-end bash runner: clones Binance tooling, downloads monthly archives, extracts files, converts to Parquet, and verifies output.
* `requirements.txt` — Python dependencies (`duckdb`, `pandas`).

---

## Quick Start

### 1. Environment Setup

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

```

### 2. Run the Pipeline

The `use-case.sh` script provides a full, out-of-the-box run for `BTCUSDT` spot data covering the first half of 2026:

```bash
chmod +x use-case.sh
./use-case.sh

```

---

## Manual Usage

### Convert CSVs to Parquet (`make-parquet.py`)

Accepts a CSV glob path, start timestamp, end timestamp, and the output path:

```bash
python make-parquet.py \
  "path/to/klines/*.csv" \
  "2026-01-01" \
  "2026-07-01" \
  "data/solid.parquet"

```

### Validate Parquet Data (`check-parquet.py`)

Checks for full timeline continuity and candle integrity:

```bash
python check-parquet.py \
  "data/solid.parquet" \
  "2026-01-01" \
  "2026-07-01"

```

Expected verification output:

* `n_excess = 0` and `n_missing = 0` (perfect alignment with a synthetic 1-minute interval series).
* All validation sum totals in the final block equal `n_total`.

---

## Parquet Schema

| Column | Type | Description |
| --- | --- | --- |
| `open_time` | `TIMESTAMP` | Kline open timestamp (UTC) |
| `open` | `DECIMAL(19, 8)` | Open price |
| `high` | `DECIMAL(19, 8)` | Highest price |
| `low` | `DECIMAL(19, 8)` | Lowest price |
| `close` | `DECIMAL(19, 8)` | Close price |
| `volume` | `DECIMAL(19, 8)` | Base asset volume |
| `qav` | `DECIMAL(19, 8)` | Quote asset volume |
| `n_trades` | `BIGINT` | Number of completed trades |
| `buy_volume` | `DECIMAL(19, 8)` | Taker buy base asset volume |
| `buy_qav` | `DECIMAL(19, 8)` | Taker buy quote asset volume |

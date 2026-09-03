set -e

TYPE="spot"
SYMBOL="BTCUSDT"
YEARS="2026"
MONTHS="1 2 3 4 5 6"
START_DATE="2026-01-01"
END_DATE="2026-07-01"
PARQUET_FILE="data/solid.parquet"

if [ "$TYPE" = "um" ] || [ "$TYPE" = "cm" ]; then
  KLINE_DIR="binance-public-data/python/data/futures/$TYPE/monthly/klines/$SYMBOL/1m"
else
  KLINE_DIR="binance-public-data/python/data/$TYPE/monthly/klines/$SYMBOL/1m"
fi

if [ ! -d "binance-public-data" ]; then
  git clone https://github.com/binance/binance-public-data.git
  git -C binance-public-data checkout 5c7f319
  sed -i.bak "s/'2025'/'2025', '2026'/" binance-public-data/python/enums.py && rm -f binance-public-data/python/enums.py.bak
fi

python binance-public-data/python/download-kline.py -t "$TYPE" -s "$SYMBOL" -i 1m -y $YEARS -m $MONTHS -skip-daily 1
find "$KLINE_DIR" -type f -name "*.zip" -exec sh -c 'unzip -o "$1" -d "$(dirname "$1")" && rm "$1"' _ {} \;
mkdir -p "$(dirname "$PARQUET_FILE")"
python make-parquet.py "$KLINE_DIR/*.csv" "$START_DATE" "$END_DATE" "$PARQUET_FILE"
rm -f "$KLINE_DIR"/*.csv
python check-parquet.py "$PARQUET_FILE" "$START_DATE" "$END_DATE"

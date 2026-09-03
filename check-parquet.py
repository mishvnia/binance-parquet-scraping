import sys
import duckdb

conn = duckdb.connect()

conn.execute(f'''
  CREATE VIEW df AS
  SELECT 
    *,
    volume - buy_volume AS sell_volume,
    qav - buy_qav AS sell_qav
  FROM '{sys.argv[1]}'
''')

print()

print(conn.execute('''
  WITH ffilled AS (
    SELECT 
      open, high, low, close, n_trades,
      last_value(CASE WHEN n_trades != 0 THEN close ELSE NULL END IGNORE NULLS) 
      OVER (ORDER BY open_time) AS ffill_close
    FROM df
  )
  SELECT
    COUNT(*) AS n_total,
    SUM(
      n_trades != 0 OR (
        ffill_close IS NOT NULL AND
        open = ffill_close AND
        high = ffill_close AND
        low = ffill_close AND
        close = ffill_close
      ) OR (
        ffill_close IS NULL AND 
        open = close AND high = close AND low = close
      )
    ) AS n_complete
  FROM ffilled
''').df().iloc[0])

print()

print(conn.execute(f'''
  WITH target_series AS (
    SELECT unnest(generate_series(
      TIMESTAMP '{sys.argv[2]}',
      TIMESTAMP '{sys.argv[3]}' - INTERVAL 1 MINUTE,
      INTERVAL 1 MINUTE
    )) AS ts
  ),
  counts_df AS (
    SELECT open_time AS ts, COUNT(*) AS cnt_df
    FROM df
    GROUP BY 1
  ),
  counts_series AS (
    SELECT ts, COUNT(*) AS cnt_series
    FROM target_series
    GROUP BY 1
  ),
  combined AS (
    SELECT 
      COALESCE(d.ts, s.ts) AS ts,
      COALESCE(d.cnt_df, 0) AS cnt_df,
      COALESCE(s.cnt_series, 0) AS cnt_series
    FROM counts_df d
    FULL OUTER JOIN counts_series s ON d.ts = s.ts
  )
  SELECT 
    SUM(GREATEST(0, cnt_df - cnt_series)) AS n_excess,
    SUM(GREATEST(0, cnt_series - cnt_df)) AS n_missing
  FROM combined;
''').df().iloc[0])

print()

print(conn.execute('''
  SELECT

    SUM(n_trades >= 0),
    SUM(volume >= 0),
    SUM(buy_volume >= 0),
    SUM(sell_volume >= 0),

    SUM(qav >= 0),
    SUM(buy_qav >= 0),
    SUM(sell_qav >= 0),

    SUM((n_trades = 0) = (qav = 0)),
    SUM((volume = 0) = (qav = 0)),
    SUM((buy_volume = 0) = (buy_qav = 0)),
    SUM((sell_volume = 0) = (sell_qav = 0)),

    SUM(low > 0),
    SUM(low <= open),
    SUM(low <= close),
    SUM(low * volume <= qav),
    SUM(low * buy_volume <= buy_qav),
    SUM(low * sell_volume <= sell_qav),

    SUM(high >= open),
    SUM(high >= close),
    SUM(high * volume >= qav),
    SUM(high * buy_volume >= buy_qav),
    SUM(high * sell_volume >= sell_qav)

  FROM df
''').df().iloc[0])

conn.close()

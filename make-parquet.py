import sys
import duckdb

duckdb.read_csv(sys.argv[1], columns={
  'open_time'              : 'BIGINT',
  'open'                   : 'DECIMAL(19, 8)',
  'high'                   : 'DECIMAL(19, 8)',
  'low'                    : 'DECIMAL(19, 8)',
  'close'                  : 'DECIMAL(19, 8)',
  'volume'                 : 'DECIMAL(19, 8)',
  'close_time'             : 'BIGINT',
  'quote_volume'           : 'DECIMAL(19, 8)',
  'count'                  : 'BIGINT',
  'taker_buy_volume'       : 'DECIMAL(19, 8)',
  'taker_buy_quote_volume' : 'DECIMAL(19, 8)',
  'ignore'                 : 'VARCHAR'
}).select(f'''
  CASE
    WHEN open_time >= epoch_us(TIMESTAMP '{sys.argv[2]}')
    AND open_time < epoch_us(TIMESTAMP '{sys.argv[3]}')
    THEN make_timestamp(open_time)
    WHEN open_time >= epoch_ms(TIMESTAMP '{sys.argv[2]}')
    AND open_time < epoch_ms(TIMESTAMP '{sys.argv[3]}')
    THEN epoch_ms(open_time)
    ELSE CAST(error('Wrong open_time') AS TIMESTAMP)
  END AS open_time,
  open,
  high,
  low,
  close,
  volume,
  quote_volume as qav,
  count as n_trades,
  taker_buy_volume as buy_volume,
  taker_buy_quote_volume as buy_qav
''').order('open_time').to_parquet(sys.argv[4])

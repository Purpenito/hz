CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  telegram_user_id BIGINT UNIQUE NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_settings (
  id SERIAL PRIMARY KEY,
  user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
  notifications_enabled BOOLEAN NOT NULL DEFAULT TRUE,
  enabled_exchanges_json TEXT NOT NULL,
  enabled_arbitrage_types_json TEXT NOT NULL,
  min_profit_pct DOUBLE PRECISION NOT NULL DEFAULT 0.1,
  min_volume_24h DOUBLE PRECISION NOT NULL DEFAULT 100000,
  capital_usdt DOUBLE PRECISION NOT NULL DEFAULT 100,
  min_executable_ratio_pct DOUBLE PRECISION NOT NULL DEFAULT 50,
  max_signal_age_ms INTEGER NOT NULL DEFAULT 10000,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sent_signals (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  signal_key VARCHAR(255) NOT NULL,
  symbol VARCHAR(64) NOT NULL,
  arbitrage_type VARCHAR(64) NOT NULL,
  long_exchange VARCHAR(32) NOT NULL,
  short_exchange VARCHAR(32) NOT NULL,
  sent_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_sent_signals_user_signal ON sent_signals(user_id, signal_key);

# Arb Bot (Telegram crypto arbitrage scanner)

Production-oriented backend foundation for Telegram bot that scans only:
- `futures_futures`
- `funding`

Supported exchanges:
- Bybit
- KuCoin
- OKX
- Gate
- BingX

## Stack
- Python 3.11+
- aiogram 3
- FastAPI
- httpx / asyncio
- SQLAlchemy + PostgreSQL
- Redis
- Pydantic
- Alembic-ready migrations layout
- Docker / docker-compose

## Project structure
Implemented according to requested layered architecture in `arb_bot/app`:
- `exchanges/` adapters
- `market_data/` stores
- `arbitrage/` calculation core
- `services/` orchestration
- `bot/` Telegram handlers/keyboards/formatters
- `storage/` db, ORM and repositories

## Quick start (local)
1. Create venv and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Configure `.env` (`TELEGRAM_BOT_TOKEN`, DB/Redis URLs).
3. Run bot:
   ```bash
   export PYTHONPATH=$PWD/arb_bot
   python -m app.main
   ```

## Quick start (Docker)
```bash
docker compose -f docker/docker-compose.yml up --build
```

## Tests
```bash
export PYTHONPATH=$PWD/arb_bot
pytest arb_bot/app/tests -q
```

## Notes
- Exchange adapters are implemented as async stubs ready for replacing with real HTTP integrations.
- Scanner evaluates both pair directions, uses orderbook depth and applies user filters.
- Settings and sent signals are persisted through SQL models/migration.

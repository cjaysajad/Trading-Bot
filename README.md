# Trading Bot

A cryptocurrency trading bot starter built with Python and the `ccxt` library.
Supports Binance, Coinbase, and any other exchange that ccxt covers. Includes
grid trading and dollar-cost averaging strategies, with stop-loss and
take-profit guards and a dry-run mode that never places real orders.

## Safety

Dry-run mode is on by default (`DRY_RUN=true`). In dry-run the bot records the
orders it would place without sending them to the exchange. Set `DRY_RUN=false`
only after you understand the code and have tested on a testnet or with very
small amounts. This is a starter project, not financial advice, and it is not
audited.

## Requirements

- Python 3.11 or later

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in your exchange API key and secret in `.env`. Start with `DRY_RUN=true`.

## Run

```bash
python main.py
```

The bot runs a loop. Each step it fetches the current price, places strategy
orders (or records them in dry-run), and checks risk thresholds. Stop it with
Ctrl+C.

## Strategies

- Grid: places buy orders below the current price and sell orders above it at
  evenly spaced levels. Profit comes from price moving within the range.
- DCA: buys a fixed fiat amount on a fixed interval, regardless of price.

Switch with the `STRATEGY` variable (`grid` or `dca`).

## Configuration

All settings come from environment variables. See `.env.example` for the full
list and defaults.

## Test

```bash
pytest -q
```

Tests cover grid level generation, stop-loss and take-profit triggers, DCA
weighted average entry, and dry-run order recording. No network access is
needed.

## Project layout

| Path | Purpose |
|---|---|
| `main.py` | Entry point and run loop |
| `config.py` | Environment-driven settings |
| `exchange_client.py` | ccxt wrapper with dry-run mode |
| `strategies/grid.py` | Grid trading strategy |
| `strategies/dca.py` | Dollar-cost averaging strategy |

## License

MIT

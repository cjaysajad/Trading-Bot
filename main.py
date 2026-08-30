"""Entry point for the trading bot."""
from __future__ import annotations

import logging
import time

from config import Settings
from exchange_client import ExchangeClient
from strategies.dca import DcaStrategy
from strategies.grid import GridStrategy


def build_strategy(settings: Settings, client: ExchangeClient):
    if settings.strategy == "grid":
        return GridStrategy(settings, client)
    if settings.strategy == "dca":
        return DcaStrategy(
            settings, client, settings.dca.interval_minutes * 60
        )
    raise ValueError(f"unknown strategy: {settings.strategy}")


def run(settings: Settings | None = None) -> None:
    settings = settings or Settings.from_env()
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    log = logging.getLogger("trading")
    log.info(
        "starting bot: exchange=%s symbol=%s strategy=%s dry_run=%s",
        settings.exchange,
        settings.symbol,
        settings.strategy,
        settings.dry_run,
    )
    client = ExchangeClient(settings)
    strategy = build_strategy(settings, client)
    strategy.symbol = settings.symbol

    try:
        while True:
            strategy.step()
            time.sleep(settings.loop_interval_seconds)
    except KeyboardInterrupt:
        log.info("stopped by user")


if __name__ == "__main__":
    run()

"""Grid trading strategy.

Places buy orders at evenly spaced prices below the current price and sell
orders above it. Profit comes from price oscillating within the range. Each
sell level also checks the stop-loss and take-profit thresholds against the
average entry price of filled buys.
"""
from __future__ import annotations

import logging

from config import Settings
from exchange_client import ExchangeClient
from strategies.base import Strategy

log = logging.getLogger("trading.grid")


def grid_prices(lower: float, upper: float, levels: int) -> list[float]:
    """Return `levels` evenly spaced prices from lower to upper."""
    if levels < 2:
        raise ValueError("levels must be at least 2")
    if upper <= lower:
        raise ValueError("upper must be greater than lower")
    step = (upper - lower) / (levels - 1)
    return [lower + i * step for i in range(levels)]


class GridStrategy(Strategy):
    def __init__(self, settings: Settings, client: ExchangeClient) -> None:
        self.settings = settings
        self.client = client
        self.symbol = settings.symbol
        self._filled_buys: list[tuple[float, float]] = []
        self._placed_levels: set[int] = set()

    def should_exit(self, entry_price: float, current_price: float) -> str | None:
        """Return 'stop_loss', 'take_profit', or None."""
        change_pct = ((current_price - entry_price) / entry_price) * 100
        if change_pct <= -self.settings.risk.stop_loss_pct:
            return "stop_loss"
        if change_pct >= self.settings.risk.take_profit_pct:
            return "take_profit"
        return None

    def step(self) -> None:
        prices = grid_prices(
            self.settings.grid.lower,
            self.settings.grid.upper,
            self.settings.grid.levels,
        )
        current = self.client.fetch_price(self.symbol)
        for idx, level in enumerate(prices):
            if idx in self._placed_levels:
                continue
            side = "buy" if level < current else "sell"
            self.client.place_order(side, self.symbol, 0.001, level)
            if side == "buy":
                self._filled_buys.append((level, 0.001))
            self._placed_levels.add(idx)

        if self._filled_buys:
            avg_entry = sum(p * a for p, a in self._filled_buys) / sum(
                a for _, a in self._filled_buys
            )
            signal = self.should_exit(avg_entry, current)
            if signal:
                log.warning("exit signal %s at %s (entry %s)", signal, current, avg_entry)

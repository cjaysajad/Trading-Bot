"""Dollar-cost averaging strategy.

Buys a fixed amount on a fixed interval, regardless of price. Optional
stop-loss and take-profit checks apply to the average entry price of all
buys so far.
"""
from __future__ import annotations

import logging
from collections import deque
from time import time

from config import Settings
from exchange_client import ExchangeClient
from strategies.base import Strategy

log = logging.getLogger("trading.dca")


class DcaStrategy(Strategy):
    def __init__(
        self, settings: Settings, client: ExchangeClient, interval_seconds: int
    ) -> None:
        self.settings = settings
        self.client = client
        self.symbol = settings.symbol
        self.interval_seconds = interval_seconds
        self._buys: list[tuple[float, float]] = []
        self._last_buy_ts: float = 0.0
        self._recent: deque[float] = deque(maxlen=20)

    def average_entry(self) -> float:
        if not self._buys:
            return 0.0
        total_amount = sum(a for _, a in self._buys)
        if total_amount == 0:
            return 0.0
        return sum(p * a for p, a in self._buys) / total_amount

    def step(self) -> None:
        now = time()
        if now - self._last_buy_ts < self.interval_seconds:
            return
        price = self.client.fetch_price(self.symbol)
        amount = self.settings.dca.amount / price
        self.client.place_order("buy", self.symbol, amount, price)
        self._buys.append((price, amount))
        self._last_buy_ts = now
        self._recent.append(price)

        avg = self.average_entry()
        if avg > 0:
            change_pct = ((price - avg) / avg) * 100
            if change_pct <= -self.settings.risk.stop_loss_pct:
                log.warning("DCA stop-loss at %s (entry %s)", price, avg)
            elif change_pct >= self.settings.risk.take_profit_pct:
                log.warning("DCA take-profit at %s (entry %s)", price, avg)

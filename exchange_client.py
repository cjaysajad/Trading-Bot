"""Thin wrapper around ccxt with a dry-run mode that never places real orders."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

import ccxt

from config import Settings

log = logging.getLogger("trading")


@dataclass
class Order:
    side: str  # "buy" or "sell"
    symbol: str
    amount: float
    price: float
    dry_run: bool


@dataclass
class ExchangeClient:
    settings: Settings
    _exchange: ccxt.Exchange | None = None
    _dry_orders: list[Order] = field(default_factory=list)

    @property
    def exchange(self) -> ccxt.Exchange:
        if self._exchange is None:
            klass = getattr(ccxt, self.settings.exchange)
            self._exchange = klass(
                {"apiKey": self.settings.api_key, "enableRateLimit": True}
            )
            if self.settings.api_secret:
                self._exchange.secret = self.settings.api_secret
        return self._exchange

    def fetch_price(self, symbol: str) -> float:
        ticker = self.exchange.fetch_ticker(symbol)
        price = float(ticker["last"])
        log.debug("fetched price %s for %s", price, symbol)
        return price

    def place_order(
        self, side: str, symbol: str, amount: float, price: float
    ) -> Order:
        if self.settings.dry_run:
            order = Order(side, symbol, amount, price, dry_run=True)
            self._dry_orders.append(order)
            log.info("dry-run %s order: %s %s @ %s", side, amount, symbol, price)
            return order
        order = self.exchange.create_order(
            symbol, "limit", side, amount, price
        )
        log.info("placed %s order id=%s", side, order.get("id"))
        return Order(side, symbol, amount, price, dry_run=False)

    @property
    def dry_orders(self) -> list[Order]:
        return list(self._dry_orders)

"""Strategy interface."""
from __future__ import annotations

from dataclasses import dataclass

from exchange_client import ExchangeClient


@dataclass
class Strategy:
    symbol: str
    client: ExchangeClient

    def step(self) -> None:
        raise NotImplementedError

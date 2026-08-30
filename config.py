"""Configuration loaded from environment variables."""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class RiskConfig:
    stop_loss_pct: float
    take_profit_pct: float


@dataclass(frozen=True)
class GridConfig:
    levels: int
    lower: float
    upper: float


@dataclass(frozen=True)
class DcaConfig:
    amount: float
    interval_minutes: int


@dataclass(frozen=True)
class Settings:
    exchange: str
    api_key: str
    api_secret: str
    symbol: str
    dry_run: bool
    strategy: str
    grid: GridConfig
    dca: DcaConfig
    risk: RiskConfig
    loop_interval_seconds: int
    log_level: str

    @classmethod
    def from_env(cls) -> "Settings":
        def f(env: str, default: float) -> float:
            return float(os.environ.get(env, default))

        return cls(
            exchange=os.environ.get("EXCHANGE", "binance"),
            api_key=os.environ.get("API_KEY", ""),
            api_secret=os.environ.get("API_SECRET", ""),
            symbol=os.environ.get("SYMBOL", "BTC/USDT"),
            dry_run=os.environ.get("DRY_RUN", "true").lower() == "true",
            strategy=os.environ.get("STRATEGY", "grid"),
            grid=GridConfig(
                levels=int(f("GRID_LEVELS", 5)),
                lower=f("GRID_LOWER", 60000),
                upper=f("GRID_UPPER", 70000),
            ),
            dca=DcaConfig(
                amount=f("DCA_AMOUNT", 50),
                interval_minutes=int(f("DCA_INTERVAL_MINUTES", 60)),
            ),
            risk=RiskConfig(
                stop_loss_pct=f("STOP_LOSS_PCT", 5),
                take_profit_pct=f("TAKE_PROFIT_PCT", 10),
            ),
            loop_interval_seconds=int(f("LOOP_INTERVAL_SECONDS", 30)),
            log_level=os.environ.get("LOG_LEVEL", "INFO"),
        )

import pytest

from config import Settings, GridConfig, DcaConfig, RiskConfig
from exchange_client import ExchangeClient, Order
from strategies.grid import GridStrategy, grid_prices
from strategies.dca import DcaStrategy


def make_settings() -> Settings:
    return Settings(
        exchange="binance",
        api_key="",
        api_secret="",
        symbol="BTC/USDT",
        dry_run=True,
        strategy="grid",
        grid=GridConfig(levels=5, lower=60000, upper=70000),
        dca=DcaConfig(amount=50, interval_minutes=60),
        risk=RiskConfig(stop_loss_pct=5, take_profit_pct=10),
        loop_interval_seconds=30,
        log_level="DEBUG",
    )


class FakeClient(ExchangeClient):
    """Records orders without touching the network."""

    def __init__(self, settings: Settings, prices: list[float]) -> None:
        super().__init__(settings)
        self._prices = prices
        self._calls = 0

    def fetch_price(self, symbol: str) -> float:
        price = self._prices[self._calls % len(self._prices)]
        self._calls += 1
        return price

    def place_order(self, side, symbol, amount, price) -> Order:
        order = Order(side, symbol, amount, price, dry_run=True)
        self._dry_orders.append(order)
        return order


def test_grid_prices_even_spacing():
    prices = grid_prices(60000, 70000, 5)
    assert prices == [60000, 62500, 65000, 67500, 70000]


def test_grid_prices_requires_two_levels():
    with pytest.raises(ValueError):
        grid_prices(60000, 70000, 1)


def test_grid_prices_upper_must_exceed_lower():
    with pytest.raises(ValueError):
        grid_prices(70000, 70000, 5)


def test_grid_places_buys_below_current_and_sells_above():
    settings = make_settings()
    client = FakeClient(settings, prices=[65000])
    strategy = GridStrategy(settings, client)
    strategy.step()
    buys = [o for o in client.dry_orders if o.side == "buy"]
    sells = [o for o in client.dry_orders if o.side == "sell"]
    # current 65000: 60000, 62500 below -> buys; 65000, 67500, 70000 at/above -> sells
    assert len(buys) == 2
    assert len(sells) == 3


def test_should_exit_triggers_stop_loss():
    settings = make_settings()
    client = FakeClient(settings, prices=[65000])
    strategy = GridStrategy(settings, client)
    assert strategy.should_exit(entry_price=70000, current_price=65000) == "stop_loss"


def test_should_exit_triggers_take_profit():
    settings = make_settings()
    client = FakeClient(settings, prices=[65000])
    strategy = GridStrategy(settings, client)
    assert strategy.should_exit(entry_price=60000, current_price=67000) == "take_profit"


def test_should_exit_none_within_range():
    settings = make_settings()
    client = FakeClient(settings, prices=[65000])
    strategy = GridStrategy(settings, client)
    assert strategy.should_exit(entry_price=64000, current_price=65000) is None


def test_dca_average_entry_weighted():
    settings = make_settings()
    client = FakeClient(settings, prices=[100, 200])
    strategy = DcaStrategy(settings, client, interval_seconds=0)
    strategy.step()
    strategy.step()
    # buys: 0.5 @ 100 and 0.25 @ 200 -> avg = (50 + 50) / 0.75 = 133.33
    assert round(strategy.average_entry(), 2) == 133.33

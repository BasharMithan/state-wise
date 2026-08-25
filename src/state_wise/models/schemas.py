"""
market_data_model.py — Canonical market data schema
======================================================

Defines `MarketObservation`, the single normalized shape referenced (in
prose) by `01-market-data.md` as "normalized market observations ...
timestamped and ready for feature computation."

This is the one place the schema is allowed to be defined. Both the live
feed (`live_feed.py`) and the historical loader (`historical_loader.py`)
import it from here rather than each declaring their own shape — that's
what structurally guarantees live and backtest paths agree on what a bar
looks like, instead of relying on two implementations staying in sync by
convention.
"""

from dataclasses import dataclass

from datetime import datetime


@dataclass(frozen=True)
class MarketObservation:
    """A single normalized OHLCV bar, identical whether it came from a
    live Binance stream or historical data.

    Field choices map directly to what 02-feature-engineering.md needs:
    price-based features (open/high/low/close), volume-based features
    (volume), and the point-in-time correctness check from
    01-market-data.md (timestamp_ms + is_final)."""

    symbol: list[str]
    timestamp: datetime      # bar CLOSE time — never the open time, to avoid
                            # any ambiguity about what data was actually
                            # available "at" this timestamp
    open: float
    high: float
    low: float
    close: float
    volume: float
    is_final: bool          # False only for in-progress/unconfirmed bars;
                             # feature engineering must never consume these
                             # (see 02-feature-engineering.md's no-lookahead rule)
    source: str

    bid: str = ""
    ask: str = ""


    def __post_init__(self) -> None:
        # Cheap invariant checks — cheap enough to run on every bar, and
        # exactly the kind of thing that should fail loudly rather than
        # silently propagate a malformed observation downstream.
        if self.high < self.low:
            raise ValueError(f"{self.symbol}@{self.timestamp}: high < low")
        if not (self.low <= self.open <= self.high):
            raise ValueError(f"{self.symbol}@{self.timestamp}: open outside [low, high]")
        if not (self.low <= self.close <= self.high):
            raise ValueError(f"{self.symbol}@{self.timestamp}: close outside [low, high]")
        if self.volume < 0:
            raise ValueError(f"{self.symbol}@{self.timestamp}: negative volume")
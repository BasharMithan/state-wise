"""
StateWise — TradingSource Interface
=====================================

Defines the provider-agnostic contract for market data access. This is
the abstraction the `data/` component (01-market-data.md) is built
around: everything downstream of this interface (feature engineering,
predictor, regime detector, ...) only ever depends on `TradingSource`,
never on a specific exchange's client library directly.

Why this exists: Alpaca didn't work for this deployment's region, and
there's no guarantee Binance will remain the right choice either 
account restrictions, regional policy, or a provider's own risk
posture can all change independently of StateWise's code. Any concrete
data source (Binance, a future replacement, or several at once) plugs
into the pipeline the same way, as long as it implements this
interface. Swapping providers should mean writing one new subclass,
not touching feature engineering, the predictor, or anything else.

Concrete implementations:
    - BinanceTradingSource (liveFeed.py), live streaming + historical
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from datetime import datetime

from models.schemas import Candle 


class TradingSource(ABC):
    """
    Abstract base class every market data provider must implement.

    A TradingSource is responsible only for getting normalized market
    data (Candle) into StateWise, live streaming and
    historical backfill. It has no knowledge of features, models, risk,
    or execution; those are separate concerns downstream.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Short identifier for this source, e.g. 'binance'. Used in logs and audit trails."""
        raise NotImplementedError

    @abstractmethod
    async def connect(self) -> None:
        """
        Establish whatever connection/session the source needs
        (a client, an auth handshake, etc.). Must be safe to call
        again after close() to reconnect.
        """
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        """Tear down the connection cleanly. Must be safe to call even if connect() was never called."""
        raise NotImplementedError

    @abstractmethod
    def stream(self, symbols: list[str], interval: str) -> AsyncIterator[Candle]:
        """
        Yields Candle objects as new data arrives, live.

        Implementations are responsible for their own reconnection
        logic -- a caller iterating this stream should not need to
        handle transient network drops themselves.
        """
        raise NotImplementedError

    @abstractmethod
    async def fetch_historical(
        self,
        symbol: str,
        interval: str,
        start: datetime,
        end: datetime | None = None,
    ) -> list[Candle]:
        """
        Fetches historical Candle data for backtesting and
        model calibration. Must return data in the same shape stream()
        produces, so backtest and live code paths are identical from
        this point downstream.
        """
        raise NotImplementedError

    async def __aenter__(self) -> "TradingSource":
        await self.connect()
        return self

    async def __aexit__(self, *exc_info) -> None:
        await self.close()
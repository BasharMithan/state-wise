import asyncio
import json
import logging
from collections.abc import AsyncIterator
from datetime import timezone, datetime

import websockets
from websockets.exceptions import ConnectionClosed

from state_wise.configs.liveFeedConfig import LiveFeedConfig
from state_wise.models.schemas import Candle

logger = logging.getLogger(__name__)


class LiveFeed:
    def __init__(self, config: LiveFeedConfig):
        self.config: LiveFeedConfig = config
        self.backoff: float = config.reconnectBackoffSeconds



    @property
    def url(self) -> str:
        streams: str = "/".join(self.config.streams)
        return f"{self.config.webSocketBaseURL}?streams={streams}"

    

    async def stream(self) -> AsyncIterator[Candle]:
        """Yields `Candle` objects. Reconnects automatically on disconnect."""


        while True:
            try:

                async with websockets.connect(self.url, ping_interval=20, ping_timeout=20, ) as binance:
                    self.backoff: float = self.config.reconnectBackoffSeconds

                    async for message in binance:
                        yield self.parse(str(message))

            except (ConnectionClosed, OSError) as exc:
                logger.warning(f"Disconnected: {exc}")
                await asyncio.sleep(self.backoff)
                self.backoff = min(self.backoff * 2, self.config.maxBackoffSeconds)



    def parse(self, message: str) -> Candle:
        """Parses one raw combined-stream message into a `Candle` object.

        Args:
            message (str): The message got from the stream web socket (`LiveFeed.stream`).

        Returns:
            Candle: `Candle` object, or `None` for in-progress clandles
        """
        payload = json.loads(message)
        data = payload.get("data", payload)

        k = data['k']
        closeTime: int = int(k['T'])
        timestamp: datetime = datetime.fromtimestamp(closeTime / 1000.0, tz = timezone.utc)

        openPrice: float   = float(k['o'])
        highPrice: float   = float(k['h'])
        lowPrice: float    = float(k['l'])
        closePrice: float  = float(k['c'])
        volume: float      = float(k['v'])
        isFinal: bool      = bool(k['x'] ) # True when the candle is closed/confirmed.



        return Candle(
            symbol=self.config.symbol,
            timestamp=timestamp,
            open=openPrice,
            high=highPrice,
            low=lowPrice,
            close=closePrice,
            volume=volume,
            is_final=isFinal,
            source='Binance'
        )




async def main():
    config = LiveFeedConfig(symbol=["btcusdt"],interval="1m",testnet=True)
    live = LiveFeed(config)
    async for message in live.stream():
        print(message)

if __name__ == '__main__':
    asyncio.run(main())
    


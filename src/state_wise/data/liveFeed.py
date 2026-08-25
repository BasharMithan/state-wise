import asyncio
import json
import logging
from collections.abc import AsyncIterator
from datetime import timezone, datetime

import websockets
from websockets.exceptions import ConnectionClosed

from state_wise.configs.liveFeedConfig import LiveFeedConfig
from state_wise.models.schemas import MarketObservation

logger = logging.getLogger(__name__)


class LiveFeed:
    def __init__(self, config: LiveFeedConfig):
        self.config = config
        self._backoff = config.reconnectBackoffSeconds



    @property
    def url(self) -> str:
        streams = "/".join(self.config.streams)
        return f"{self.config.webSocketBaseURL}?streams={streams}"

    

    async def stream(self) -> AsyncIterator[MarketObservation]:
        """Yields `MarketObservation` objects. Reconnects automatically on disconnect."""


        while True:
            try:

                async with websockets.connect(self.url, ping_interval=20, ping_timeout=20, ) as binance:
                    self.backoff = self.config.reconnectBackoffSeconds

                    async for message in binance:
                        yield self.parse(str(message))

            except (ConnectionClosed, OSError) as exc:
                logger.warning("Disconnected: %s", exc)
                await asyncio.sleep(self.backoff)
                self._backoff = min(self.backoff * 2, self.config.maxBackoffSeconds)



    def parse(self, message: str) -> MarketObservation:
        """Parses one raw combined-stream message into a `MarketObservation` object.

        Args:
            message (str): The message got from the stream web socket (`LiveFeed.stream`).

        Returns:
            MarketObservation: `MarketObservation` object, or `None` for in-progress clandles
        """
        payload = json.loads(message)
        data = payload.get("data", payload)

        k = data['k']
        closeTime = int(k['T'])
        timestamp = datetime.fromtimestamp(closeTime / 1000.0, tz = timezone.utc)

        openPrice = float(k['o'])
        highPrice = float(k['h'])
        lowPrice  = float(k['l'])
        closePrice= float(k['c'])
        volume    = float(k['v'])
        isFinal   = bool(k['x']) # True when the candle is closed/confirmed.



        return MarketObservation(
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
    


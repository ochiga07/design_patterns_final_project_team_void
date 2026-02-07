from abc import ABC, abstractmethod

import requests


class BtcPriceConverter(ABC):
    @abstractmethod
    def get_btc_to_usd_rate(self) -> float:
        pass

    def satoshi_to_btc(self, satoshis: int) -> float:
        return satoshis / 100_000_000

    def satoshi_to_usd(self, satoshis: int) -> float:
        btc = self.satoshi_to_btc(satoshis)
        return round(btc * self.get_btc_to_usd_rate(), 2)


class CoinGeckoBtcPriceConverter(BtcPriceConverter):
    API_URL = "https://api.coingecko.com/api/v3/simple/price"

    def get_btc_to_usd_rate(self) -> float:
        response = requests.get(
            self.API_URL,
            params={"ids": "bitcoin", "vs_currencies": "usd"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        return float(data["bitcoin"]["usd"])

from unittest.mock import MagicMock, patch

from service.btc_price_converter import BtcPriceConverter, CoinGeckoBtcPriceConverter


class FakeConverter(BtcPriceConverter):
    def get_btc_to_usd_rate(self) -> float:
        return 100000.0


class TestBtcPriceConverter:

    def test_satoshi_to_btc(self) -> None:
        converter = FakeConverter()
        assert converter.satoshi_to_btc(100_000_000) == 1.0
        assert converter.satoshi_to_btc(50_000_000) == 0.5

    def test_satoshi_to_usd(self) -> None:
        converter = FakeConverter()
        assert converter.satoshi_to_usd(100_000_000) == 100000.0
        assert converter.satoshi_to_usd(50_000_000) == 50000.0


class TestCoinGeckoBtcPriceConverter:

    @patch("service.btc_price_converter.requests.get")
    def test_get_btc_to_usd_rate(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"bitcoin": {"usd": 97000.0}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        converter = CoinGeckoBtcPriceConverter()
        rate = converter.get_btc_to_usd_rate()

        assert rate == 97000.0
        mock_get.assert_called_once()

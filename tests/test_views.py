import pytest
from src.views import _get_currency_rates, _get_stock_prices
from unittest.mock import patch

@patch("src.views.requests.get")
def test_get_currency_rates(mock_get):
    mock_get.return_value.json.return_value = {"rates": {"USD": 0.05}}
    mock_get.return_value.raise_for_status = lambda: None
    res = _get_currency_rates(["USD"], "key")
    assert res[0]["currency"] == "USD"

@patch("src.views.requests.get")
def test_get_stock_prices(mock_get):
    mock_get.return_value.json.return_value = {"Global Quote": {"05. price": "100.5"}}
    mock_get.return_value.raise_for_status = lambda: None
    res = _get_stock_prices(["AAPL"], "key")
    assert res[0]["stock"] == "AAPL"
    assert res[0]["price"] == 100.5
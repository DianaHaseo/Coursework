import json

import pytest
from unittest.mock import patch, Mock
from datetime import datetime
from src.views import get_currency_rates, get_stock_prices, greeting_for_time, finance_data_response

@pytest.mark.parametrize("hour, expected", [
    (4, "Доброй ночи"),
    (6, "Доброе утро"),
    (13, "Добрый день"),
    (19, "Добрый вечер"),
    (23, "Доброй ночи"),
])
def test_greeting_for_time(hour, expected):
    dt = datetime(2025, 1, 1, hour, 0, 0)
    assert greeting_for_time(dt) == expected

@patch("src.views.requests.get")
def test_get_currency_rates_success(mock_get):
    mock_resp = Mock()
    mock_resp.json.return_value = {"rates": {"USD": 0.05, "EUR": 0.07}}
    mock_resp.raise_for_status = lambda: None
    mock_get.return_value = mock_resp

    res = get_currency_rates(["USD", "EUR"], "fake_key")
    assert any(r["currency"] == "USD" for r in res)
    assert any(r["currency"] == "EUR" for r in res)

@patch("src.views.requests.get")
def test_get_currency_rates_failure(mock_get):
    # Имитируем исключение вызова API
    mock_get.side_effect = Exception("API error")
    res = get_currency_rates(["USD"], "fake_key")
    assert res == []

@patch("src.views.requests.get")
def test_get_stock_prices_success(mock_get):
    def side_effect(url, params=None, timeout=10):
        class Resp:
            def raise_for_status(self): pass
            def json(self):
                return {
                    "Global Quote": {"05. price": "100.5"}
                }
        return Resp()

    mock_get.side_effect = side_effect

    stocks = ["AAPL", "GOOG"]
    res = get_stock_prices(stocks, "fake_key")
    assert all(r["stock"] in stocks for r in res)
    assert all(isinstance(r["price"], float) for r in res)

@patch("src.views.requests.get")
def test_get_stock_prices_failure(mock_get):
    mock_get.side_effect = Exception("API error")
    res = get_stock_prices(["AAPL"], "fake_key")
    assert res == []

def test_finance_data_response_empty_transactions():
    json_str = finance_data_response("2025-11-01 12:00:00", [])
    data = json.loads(json_str)
    assert "greeting" in data
    assert isinstance(data["cards"], list)
    assert isinstance(data["top_transactions"], list)
    assert isinstance(data["currency_rates"], list)
    assert isinstance(data["stock_prices"], list)
import logging
from typing import List, Dict, Any

import requests

from src.utils import (
    load_user_settings,
    get_api_keys
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# API endpoints
CURRENCY_API_ENDPOINT = "https://api.apilayer.com/exchangerates_data/latest"
STOCK_API_ENDPOINT = "https://www.alphavantage.co/query"


def _get_currency_rates(currencies: List[str], api_key: str) -> List[Dict[str, Any]]:
    if not currencies:
        return []

    headers = {"apikey": api_key} if api_key else {}
    params = {"base": "RUB", "symbols": ",".join(currencies)}

    try:
        r = requests.get(CURRENCY_API_ENDPOINT, params=params, headers=headers, timeout=10)
        r.raise_for_status()

        data = r.json()
        rates = data.get('rates', {})
        out = []

        for c in currencies:
            val = rates.get(c)
            if val is None or val == 0:
                continue

            rate = 1.0 / val
            out.append({"currency": c, "rate": round(rate, 2)})

        return out

    except Exception as e:
        logger.exception("Currency API error: %s", e)
        return []


def _get_stock_prices(stocks: List[str], api_key: str) -> List[Dict[str, Any]]:
    out = []

    if not stocks:
        return out

    for s in stocks:
        try:
            params = {"function": "GLOBAL_QUOTE", "symbol": s, "apikey": api_key}
            r = requests.get(STOCK_API_ENDPOINT, params=params, timeout=10)
            r.raise_for_status()

            data = r.json()
            quote = data.get("Global Quote", {})
            price_str = quote.get("05. price")
            if price_str:
                price = float(price_str)
                out.append({"stock": s, "price": price})
        except Exception as e:
            logger.exception("Stock API error for %s: %s", s, e)

    return out


def main_menu():
    print("=== Главное меню финансового инструмента ===")
    print("1. Показать курсы валют")
    print("2. Показать цены акций")
    print("3. Выход")
    choice = input("Выберите вариант: ")
    return choice


def show_currency_rates():
    settings = load_user_settings()
    keys = get_api_keys()
    rates = _get_currency_rates(settings.get("user_currencies", []), keys.get("currency_key", ""))
    for r in rates:
        print(f"{r['currency']}: {r['rate']}")


def show_stock_prices():
    settings = load_user_settings()
    keys = get_api_keys()
    prices = _get_stock_prices(settings.get("user_stocks", []), keys.get("stocks_key", ""))
    for s in prices:
        print(f"{s['stock']}: {s['price']}")


def main_loop():
    while True:
        choice = main_menu()
        if choice == "1":
            show_currency_rates()
        elif choice == "2":
            show_stock_prices()
        elif choice == "3":
            break
        else:
            print("Неверный выбор. Попробуйте ещё раз.")
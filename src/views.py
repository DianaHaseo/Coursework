import json
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Any

import requests
from dotenv import load_dotenv
import os

from src.utils import load_user_settings, get_api_keys

# Загрузка ключей из .env
load_dotenv()

API_KEY_1 = os.getenv("API_KEY_1")  # ключ для курсов валют
API_KEY_2 = os.getenv("API_KEY_2")  # ключ для цен акций


def greeting_for_time(dt: datetime) -> str:
    """Приветствие в зависимости от текущего времени суток."""
    hour = dt.hour
    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def filter_transactions_by_date(transactions: List[Dict[str, Any]], start: datetime, end: datetime) -> List[Dict[str, Any]]:
    """Фильтрация транзакций по дате в диапазоне start-end."""
    filtered = []
    for t in transactions:
        d = t.get('date')
        if isinstance(d, str):
            d = datetime.fromisoformat(d)
        if start <= d <= end:
            filtered.append(t)
    return filtered


def cards_summary(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Подсчет итогов расходов и кешбэка по картам."""
    card_data = defaultdict(lambda: {"total_spent": 0.0})
    for t in transactions:
        card = t.get("card_last4", "")
        amount = float(t.get("amount", 0.0))
        if amount < 0:  # считаем только расходы
            card_data[card]["total_spent"] += -amount

    result = []
    for card, data in card_data.items():
        total = data["total_spent"]
        cashback = total / 100
        result.append({
            "last_digits": card,
            "total_spent": round(total, 2),
            "cashback": round(cashback, 2)
        })
    return result


def top_transactions(transactions: List[Dict[str, Any]], top_n=5) -> List[Dict[str, Any]]:
    """Получение топ-N транзакций по абсолютной сумме платежа."""
    sorted_trans = sorted(transactions, key=lambda x: abs(float(x.get("amount", 0.0))), reverse=True)
    top_list = []
    for t in sorted_trans[:top_n]:
        d = t.get("date")
        if isinstance(d, str):
            d = datetime.fromisoformat(d)
        top_list.append({
            "date": d.strftime("%d.%m.%Y"),
            "amount": float(t.get("amount", 0.0)),
            "category": t.get("category", ""),
            "description": t.get("description", "")
        })
    return top_list


def get_currency_rates(user_currencies: List[str], api_key: str) -> List[Dict[str, Any]]:
    """Получение курсов валют с API."""
    if not user_currencies or not api_key:
        return []

    url = "https://api.apilayer.com/exchangerates_data/latest"
    headers = {"apikey": api_key}
    params = {"base": "RUB", "symbols": ",".join(user_currencies)}

    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        rates = data.get("rates", {})
        result = []
        for c in user_currencies:
            val = rates.get(c)
            if val:
                result.append({"currency": c, "rate": round(1.0 / val, 2)})
        return result
    except Exception:
        return []


def get_stock_prices(user_stocks: List[str], api_key: str) -> List[Dict[str, Any]]:
    """Получение цен акций с API."""
    if not user_stocks or not api_key:
        return []

    url = "https://www.alphavantage.co/query"
    result = []
    for s in user_stocks:
        try:
            params = {"function": "GLOBAL_QUOTE", "symbol": s, "apikey": api_key}
            r = requests.get(url, params=params, timeout=10)
            r.raise_for_status()
            data = r.json()
            quote = data.get("Global Quote", {})
            price_str = quote.get("05. price")
            if price_str:
                price = float(price_str)
                result.append({"stock": s, "price": round(price, 2)})
        except Exception:
            continue
    return result


def finance_data_response(date_str: str, transactions: List[Dict[str, Any]]) -> str:
    """Главная функция по формированию JSON-ответа для финансовых данных."""
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    start = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    filtered = filter_transactions_by_date(transactions, start, dt)
    cards = cards_summary(filtered)
    top_trans = top_transactions(filtered)

    # Загружаем настройки пользователя, например, из JSON
    settings = load_user_settings()

    currency_rates = get_currency_rates(settings.get("user_currencies", []), API_KEY_1)
    stock_prices = get_stock_prices(settings.get("user_stocks", []), API_KEY_2)

    response = {
        "greeting": greeting_for_time(dt),
        "cards": cards,
        "top_transactions": top_trans,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }
    return json.dumps(response, ensure_ascii=False, indent=2)
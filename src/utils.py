import os
import json
import logging
from datetime import datetime, date
from typing import Tuple, Dict, Any
import pandas as pd


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def load_user_settings(path: str = "user_settings.json") -> Dict[str, Any]:
    """
    Загружает настройки пользователя из JSON-файла.
    Если файл отсутствует, возвращает настройки по умолчанию с пустыми списками.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning("user_settings.json не найден: %s", path)
        return {"user_currencies": [], "user_stocks": []}


def get_api_keys() -> Dict[str, str]:
    """
    Возвращает словарь с API ключами из переменных окружения.
    """
    return {
        "currency_key": os.getenv("API_KEY_1", ""),
        "stocks_key": os.getenv("API_KEY_2", "")
    }


def parse_datetime(dt_str: str) -> datetime:
    """
    Парсит строку в объект datetime по формату '%Y-%m-%d %H:%M:%S'.
    """
    return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")


def month_range_for_date(dt: datetime) -> Tuple[date, date]:
    """
    Возвращает кортеж с началом месяца и текущей датой для переданной даты dt.
    """
    start = date(dt.year, dt.month, 1)
    end = dt.date()
    return start, end


def load_operations_xlsx(path: str = "data/operations.xlsx") -> pd.DataFrame:
    """
    Загружает Excel-файл с операциями и нормализует колонки к ожидаемому формату.
    Преобразует нужные колонки, возвращает DataFrame с операциями для дальнейшего анализа.
    """
    df = pd.read_excel(path)

    # Нормализация колонок: ищем наиболее вероятные названия
    lower_map = {c.lower(): c for c in df.columns}

    def find_col(possible):
        for p in possible:
            if p.lower() in lower_map:
                return lower_map[p.lower()]
        return None

    date_col = find_col(['Дата операции', 'Дата операции ', 'date', 'operation_date'])
    amount_col = find_col(['Сумма операции', 'Сумма операции ', 'Сумма', 'amount', 'sum'])
    category_col = find_col(['Категория', 'category'])
    desc_col = find_col(['Описание', 'Описание ', 'description', 'details'])
    card_col = find_col(['Номер карты', 'Карта', 'card', 'pan'])
    cashback_col = find_col(['Кешбэк', 'Кэшбэк', 'cashback'])

    if not date_col:
        raise ValueError("Не найден столбец с датой в operations.xlsx")

    nd = pd.DataFrame()
    nd['date'] = pd.to_datetime(df[date_col])
    nd['amount'] = pd.to_numeric(df[amount_col], errors='coerce').fillna(0.0) if amount_col else 0.0
    nd['category'] = df[category_col].astype(str) if category_col else df.get(desc_col, "").astype(str)
    nd['description'] = df[desc_col].astype(str) if desc_col else ""
    nd['card'] = df[card_col].astype(str) if card_col else ""
    nd['cashback'] = pd.to_numeric(df[cashback_col], errors='coerce').fillna(0.0) if cashback_col else 0.0

    nd['card_last4'] = nd['card'].astype(str).str.replace(r'\D', '', regex=True).str[-4:].fillna("")

    return nd

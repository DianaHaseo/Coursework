import logging
from typing import List, Dict, Any
import math
import re
from collections import defaultdict
from datetime import datetime


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def _is_expense(amount: float) -> bool:
    """Определяет, является ли сумма расходом (отрицательным числом)."""
    return amount < 0


def cashback_by_category(transactions: List[Dict[str, Any]], year: int, month: int) -> Dict[str, int]:
    """
    Рассчитывает кешбэк по категориям за указанный год и месяц.
    Кешбэк начисляется из суммы расходов (целое число рублей).
    """
    def in_month(t):
        d = t['date']
        if isinstance(d, str):
            d = datetime.fromisoformat(d)
        return d.year == year and d.month == month

    filtered = list(filter(in_month, transactions))
    sums = defaultdict(float)

    for t in filtered:
        amt = float(t.get('amount', 0))
        if _is_expense(amt):
            sums[t.get('category', 'Неизвестно')] += abs(amt)

    result = {cat: int(math.floor(total / 100.0)) for cat, total in sums.items()}
    return dict(sorted(result.items(), key=lambda x: x[1], reverse=True))


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """
    Рассчитывает сумму округления расходов вверх до заданного лимита для месяца.
    Полезно для подсчёта бонусов банков по инвестиционным услугам.
    """
    year, mon = map(int, month.split('-'))

    def in_month(t):
        d = t['date']
        if isinstance(d, str):
            d = datetime.fromisoformat(d)
        return d.year == year and d.month == mon

    filtered = list(filter(in_month, transactions))
    diffs = []

    for t in filtered:
        amt = float(t.get('amount', 0))
        if _is_expense(amt):
            orig = abs(amt)
            rounded = math.ceil(orig / limit) * limit
            diffs.append(rounded - orig)

    return sum(diffs)


def simple_search(transactions: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """
    Выполняет простой поиск по описанию и категории транзакций по ключевому слову.
    Возвращает список соответствующих транзакций.
    """
    q = query.lower()
    return list(
        filter(
            lambda t: q in str(t.get('description', '')).lower()
            or q in str(t.get('category', '')).lower(),
            transactions
        )
    )


def phone_search(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Поиск транзакций, в описании которых встречается телефонный номер в формате +7...
    """
    phone_re = re.compile(r"\+?7[\s-]?\(?\d{3}\)?[\s-]?\d{1,3}[\s-]?\d{2}[\s-]?\d{2}")
    return list(
        filter(
            lambda t: bool(phone_re.search(str(t.get('description', '')))),
            transactions
        )
    )


def transfers_to_persons(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Фильтрует транзакции, являющиеся переводами физическим лицам.
    Использует регулярные выражения для обнаружения имён и категорий переводов.
    """
    pattern = re.compile(r"\b[А-ЯЁ][а-яё]+(?:\s+[А-Я]\.)")

    def is_transfer(t):
        cat = str(t.get('category', '')).lower()
        desc = str(t.get('description', ''))
        return ('перевод' in cat or cat == 'переводы') and bool(pattern.search(desc))

    return list(filter(is_transfer, transactions))
import pytest
from src.services import cashback_by_category, investment_bank, simple_search, phone_search, transfers_to_persons
from datetime import datetime

transactions = [
    {"date": "2025-11-01", "amount": -120, "category": "Food", "description": "Lunch"},
    {"date": "2025-11-02", "amount": -250, "category": "Transport", "description": "Taxi"},
    {"date": "2025-11-02", "amount": 500, "category": "Salary", "description": "Income"},
    {"date": "2025-11-03", "amount": -90, "category": "Food", "description": "+7 999 123-45-67"},
    {"date": "2025-11-03", "amount": -100, "category": "Переводы", "description": "Перевод Иван И."}
]

def test_cashback_by_category():
    res = cashback_by_category(transactions, 2025, 11)
    assert res["Food"] == 2  # 120+90=210 → 2 рубля кешбэка

def test_investment_bank():
    res = investment_bank("2025-11", transactions, 100)
    assert isinstance(res, float)
    assert res >= 0

def test_simple_search():
    res = simple_search(transactions, "lunch")
    assert len(res) == 1
    assert res[0]["description"] == "Lunch"

def test_phone_search():
    res = phone_search(transactions)
    assert len(res) == 1
    assert "+7 999 123-45-67" in res[0]["description"]

def test_transfers_to_persons():
    res = transfers_to_persons(transactions)
    assert len(res) == 1
    assert "Иван И." in res[0]["description"]

import pytest
from src.services import cashback_by_category, investment_bank, simple_search, phone_search, transfers_to_persons

@pytest.fixture
def transactions():
    return [
        {"date": "2025-11-01", "amount": -120, "category": "Food", "description": "Lunch"},
        {"date": "2025-11-02", "amount": -250, "category": "Transport", "description": "Taxi"},
        {"date": "2025-11-02", "amount": 500, "category": "Salary", "description": "Income"},
        {"date": "2025-11-03", "amount": -90, "category": "Food", "description": "+7 999 123-45-67"},
        {"date": "2025-11-03", "amount": -100, "category": "Переводы", "description": "Перевод Иван И."}
    ]

@pytest.mark.parametrize(
    "year, month, expected_category, expected_cashback",
    [
        (2025, 11, "Food", 2),
        (2025, 11, "Transport", 2)
    ]
)
def test_cashback_by_category(transactions, year, month, expected_category, expected_cashback):
    res = cashback_by_category(transactions, year, month)
    assert res.get(expected_category, 0) == expected_cashback

def test_investment_bank(transactions):
    res = investment_bank("2025-11", transactions, 100)
    assert isinstance(res, float)
    assert res >= 0

@pytest.mark.parametrize(
    "query, expected_descriptions",
    [
        ("lunch", ["Lunch"]),
        ("Taxi", ["Taxi"]),
        ("income", ["Income"])
    ]
)
def test_simple_search(transactions, query, expected_descriptions):
    res = simple_search(transactions, query)
    descs = [t["description"] for t in res]
    for expected in expected_descriptions:
        assert expected in descs

def test_phone_search(transactions):
    res = phone_search(transactions)
    assert any("+7 999 123-45-67" in t["description"] for t in res)

def test_transfers_to_persons(transactions):
    res = transfers_to_persons(transactions)
    assert any("Иван И." in t["description"] for t in res)
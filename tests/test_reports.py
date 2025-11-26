import pytest
import pandas as pd
from src.reports import spending_by_category, spending_by_weekday, spending_by_workday

@pytest.fixture
def data():
    return pd.DataFrame([
        {"date": "2025-11-01", "amount": -100, "category": "Food"},
        {"date": "2025-11-02", "amount": -200, "category": "Transport"},
        {"date": "2025-11-03", "amount": 300, "category": "Salary"}
    ])

@pytest.mark.parametrize("category, date, expected_amount", [
    ("Food", "2025-11-03", -100),
    ("Transport", "2025-11-03", -200)
])
def test_spending_by_category(data, category, date, expected_amount):
    df = spending_by_category(data, category, date)
    assert not df.empty
    assert df.iloc[0]["amount"] == expected_amount

@pytest.mark.parametrize("date", ["2025-11-03", None])
def test_spending_by_weekday(data, date):
    df = spending_by_weekday(data, date)
    assert "average_spent" in df.columns

@pytest.mark.parametrize("date", ["2025-11-03", None])
def test_spending_by_workday(data, date):
    df = spending_by_workday(data, date)
    assert set(df["type"]) <= {"workday", "weekend"}
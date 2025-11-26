import pandas as pd
from datetime import datetime
from src.reports import spending_by_category, spending_by_weekday, spending_by_workday

data = pd.DataFrame([
    {"date": "2025-11-01", "amount": -100, "category": "Food"},
    {"date": "2025-11-02", "amount": -200, "category": "Transport"},
    {"date": "2025-11-03", "amount": 300, "category": "Salary"}
])

def test_spending_by_category():
    df = spending_by_category(data, "Food", "2025-11-03")
    assert not df.empty
    assert df.iloc[0]["amount"] == -100


def test_spending_by_weekday():
    df = spending_by_weekday(data, "2025-11-03")
    assert "average_spent" in df.columns


def test_spending_by_workday():
    df = spending_by_workday(data, "2025-11-03")
    assert set(df["type"]) <= {"workday", "weekend"}
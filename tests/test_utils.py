import pytest
from datetime import datetime
from src.utils import load_user_settings, parse_datetime, month_range_for_date

def test_load_user_settings():
    res = load_user_settings("non_existing_file.json")
    assert "user_currencies" in res
    assert "user_stocks" in res

@pytest.mark.parametrize("dt_str, year", [
    ("2025-11-19 15:00:00", 2025),
    ("2024-01-01 00:00:00", 2024)
])
def test_parse_datetime(dt_str, year):
    dt = parse_datetime(dt_str)
    assert dt.year == year

@pytest.mark.parametrize("dt, expected_day", [
    (datetime(2025, 11, 19), 19),
    (datetime(2023, 5, 10), 10)
])
def test_month_range_for_date(dt, expected_day):
    start, end = month_range_for_date(dt)
    assert start.day == 1
    assert end.day == expected_day

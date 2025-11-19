import pytest
from datetime import datetime
from src.utils import load_user_settings, parse_datetime, month_range_for_date

def test_load_user_settings():
    res = load_user_settings("non_existing_file.json")
    assert "user_currencies" in res
    assert "user_stocks" in res

def test_parse_datetime():
    dt = parse_datetime("2025-11-19 15:00:00")
    assert dt.year == 2025

def test_month_range_for_date():
    start, end = month_range_for_date(datetime(2025,11,19))
    assert start.day == 1
    assert end.day == 19


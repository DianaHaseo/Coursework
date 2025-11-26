import json
import logging
from datetime import datetime
from typing import Callable, Optional
import pandas as pd


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def save_report(func: Optional[Callable] = None, *, filename: Optional[str] = None):
    """
    Декоратор для сохранения результата функции в JSON-файл отчёта.
    Если filename не задан, формирует имя с меткой времени.
    Поддерживает сохранение pandas.DataFrame и других типов.
    """
    def decorator(f):
        def wrapper(*args, **kwargs):
            res = f(*args, **kwargs)

            nonlocal filename
            if filename is None:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                fname = f"report_{f.__name__}_{ts}.json"
            else:
                fname = filename

            if isinstance(res, pd.DataFrame):
                out = res.reset_index().to_dict(orient="records")
            else:
                out = res

            with open(fname, "w", encoding="utf-8") as fh:
                json.dump(out, fh, ensure_ascii=False, indent=2, default=str)

            logger.info("Report %s saved to %s", f.__name__, fname)
            return res

        return wrapper

    if callable(func):
        return decorator(func)
    else:
        filename = func
        return decorator


def _ensure_datetime_index(transactions: pd.DataFrame) -> pd.DataFrame:
    """
    Убеждается, что DataFrame transactions содержит колонку 'date' в типе datetime.
    Если колонка 'date' не в datetime формате, конвертирует её.
    """
    if 'date' not in transactions.columns:
        raise ValueError("DataFrame должен содержать колонку 'date'")

    df = transactions.copy()

    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'])

    return df


@save_report
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """
    Возвращает расход по указанной категории за последние 3 месяца до даты.
    Фильтрует транзакции по категории и дате, сортирует по дате.
    """
    df = _ensure_datetime_index(transactions)
    dt = pd.to_datetime(date) if date else pd.Timestamp.now()

    start = (dt - pd.DateOffset(months=3)).normalize()

    mask = (df['date'] > start) & (df['date'] <= dt) & (df['category'] == category)

    res = df.loc[mask, ['date', 'amount']].sort_values('date')
    return res


@save_report
def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """
    Рассчитывает средние расходы по дням недели за последние 3 месяца до даты.
    Отрицательные суммы считаются расходами.
    """
    df = _ensure_datetime_index(transactions)
    dt = pd.to_datetime(date) if date else pd.Timestamp.now()

    start = (dt - pd.DateOffset(months=3)).normalize()
    mask = (df['date'] > start) & (df['date'] <= dt)

    df_period = df.loc[mask].copy()
    df_period['expense'] = df_period['amount'].apply(lambda x: -x if x < 0 else 0)

    by_wd = (
        df_period
        .groupby(df_period['date'].dt.weekday)['expense']
        .mean()
        .rename("average_spent")
        .reset_index()
    )

    return by_wd


@save_report
def spending_by_workday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """
    Рассчитывает средние расходы в рабочие дни и выходные за последние 3 месяца до даты.
    Возвращает DataFrame с типом дня и средним расходом.
    """
    df = _ensure_datetime_index(transactions)
    dt = pd.to_datetime(date) if date else pd.Timestamp.now()

    start = (dt - pd.DateOffset(months=3)).normalize()
    mask = (df['date'] > start) & (df['date'] <= dt)

    df_period = df.loc[mask].copy()
    df_period['is_weekend'] = df_period['date'].dt.weekday >= 5
    df_period['expense'] = df_period['amount'].apply(lambda x: -x if x < 0 else 0)

    res = df_period.groupby('is_weekend')['expense'].mean().reset_index()
    res['type'] = res['is_weekend'].apply(lambda v: 'weekend' if v else 'workday')

    return res[['type', 'expense']].rename(columns={'expense': 'average_spent'})

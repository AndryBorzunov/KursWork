import datetime
import logging
from typing import Optional

import pandas as pd

from utils import report_to_xlsx

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("logs/reports.log", "w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s : %(filename)s : %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


@report_to_xlsx()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """
    Функция возвращает траты по заданной категории за последние три месяца (от переданной даты).
    """

    if date is None:
        date_end = datetime.datetime.now()
    else:
        date_end = datetime.datetime.strptime(date, "%Y.%m.%d")

    # Выбираем данные из диапазона времени

    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], dayfirst=True)
    time_param_start = date_end - datetime.timedelta(days=90)

    logger.info(f"Категория: {category}  Интервал времени с {time_param_start} по {date_end}")

    df_filtered = transactions[
        (transactions["Дата операции"] >= time_param_start)
        & (transactions["Дата операции"] <= date)
        & (transactions["Категория"] == category)
    ]

    logger.info(f"Найдено записей {df_filtered.shape[0]}")

    df_filtered.reset_index(drop=True)

    return df_filtered

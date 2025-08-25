import datetime
import pandas as pd
from typing import Optional
from utils import report_to_xlsx


@report_to_xlsx()
def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         date: Optional[str] = None) -> pd.DataFrame:
    """
        Функция возвращает траты по заданной категории за последние три месяца (от переданной даты).
    """

    if date is None:
        date = datetime.datetime.now()
    else:
        date = datetime.datetime.strptime(date, "%Y.%m.%d")

    # Выбираем данные из диапазона времени

    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], dayfirst=True)
    time_param_start = date - datetime.timedelta(days=90)

    df_filtered = transactions[(transactions["Дата операции"] >= time_param_start) &
                               (transactions["Дата операции"] <= date) &
                               (transactions["Категория"] == category)]

    return df_filtered
